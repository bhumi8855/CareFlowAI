
import os
from dotenv import load_dotenv
from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import LLMRunFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.worker import (
    PipelineWorker,
    PipelineParams,
    ProcessorUnusablePolicy,
)
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport
from pipecat.services.google.llm import GoogleLLMService
from pipecat.services.elevenlabs.stt import ElevenLabsRealtimeSTTService
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from pipecat.transports.base_transport import BaseTransport, TransportParams
from pipecat.workers.runner import WorkerRunner

from voice_tools import (
    check_doctor_availability,
    confirm_phone_number,
    book_appointment,
    cancel_appointment,
)

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

if not GEMINI_API_KEY or not ELEVENLABS_API_KEY or not ELEVENLABS_VOICE_ID:
    raise RuntimeError("Please check your API keys and voice ID in backend/.env")


transport_params = {
    "webrtc": lambda: TransportParams(
        audio_in_enabled=True,
        audio_out_enabled=True,
    ),
}


async def run_bot(transport: BaseTransport, runner_args: RunnerArguments):
    logger.info("Starting CareFlow AI voice assistant")

    stt = ElevenLabsRealtimeSTTService(
        api_key=ELEVENLABS_API_KEY,
        model="scribe_v2_realtime",
        settings=ElevenLabsRealtimeSTTService.Settings(
            language="en",
        ),
    )

    llm = GoogleLLMService(
        api_key=GEMINI_API_KEY,
        settings=GoogleLLMService.Settings(
            model="gemini-3.5-flash-lite",
            system_instruction="""
You are CareFlow AI, a polite and helpful doctor appointment voice assistant.

Speak naturally and keep responses short.

You can check doctor availability, book appointments, and cancel appointments
using the available tools.

Before booking or cancelling:
1. Ask the caller for their phone number.
2. Repeat the number digit by digit.
3. Ask the caller to explicitly confirm it.
4. Do not proceed until the caller confirms.

Never invent doctors, dates, slots, or booking confirmations.
Use the tool results to answer the caller.
After the caller explicitly confirms the repeated phone number,
call confirm_phone_number with that number and their affirmative response.
Only after that tool succeeds may you call book_appointment or
cancel_appointment. Never assume confirmation.
""",
        ),
    )

    tts = ElevenLabsTTSService(
        api_key=ELEVENLABS_API_KEY,
        voice_id=ELEVENLABS_VOICE_ID,
        model="eleven_flash_v2_5",
    )

    context = LLMContext(
    tools=[
        check_doctor_availability,
        confirm_phone_number,
        book_appointment,
        cancel_appointment,
    ]
)
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(
            vad_analyzer=SileroVADAnalyzer()
        ),
    )

    pipeline = Pipeline(
        [
            transport.input(),
            stt,
            user_aggregator,
            llm,
            tts,
            transport.output(),
            assistant_aggregator,
        ]
    )

    worker = PipelineWorker(
    pipeline,
    params=PipelineParams(
        enable_metrics=True,
        enable_usage_metrics=True,
    ),
    app_resources={
        "confirmed_phone": None,
    },
    processor_unusable_policy=ProcessorUnusablePolicy.END,
)

    runner = WorkerRunner(
        handle_sigint=runner_args.handle_sigint
    )

    await runner.add_workers(worker)

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info("Caller connected")
        context.add_message(
            {
                "role": "developer",
                "content": "Greet the caller and ask how you can help with a doctor appointment.",
            }
        )
        await worker.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info("Caller disconnected")
        await runner.cancel()

    await runner.run()


async def bot(runner_args: RunnerArguments):
    transport = await create_transport(
        runner_args,
        transport_params,
    )
    await run_bot(transport, runner_args)


if __name__ == "__main__":
    from pipecat.runner.run import main
    main()
