
from pipecat.services.llm_service import FunctionCallParams

from appointment_tools import (
    check_doctor_availability_tool,
    book_appointment_tool,
    cancel_appointment_tool,
)


async def check_doctor_availability(
    params: FunctionCallParams,
    speciality: str,
    date: str,
):
    """Check available doctors and appointment slots for a speciality and date."""
    result = check_doctor_availability_tool(speciality, date)
    await params.result_callback(result)


async def confirm_phone_number(
    params: FunctionCallParams,
    phone: str,
    confirmation: str,
):
    """Record the caller's phone number only after they explicitly confirm it."""

    resources = params.app_resources

    if resources is None:
        await params.result_callback({
            "success": False,
            "message": "Session confirmation is unavailable. Please try again."
        })
        return

    if len(phone) != 10 or not phone.isdigit():
        await params.result_callback({
            "success": False,
            "message": "Please ask the caller for a valid 10-digit phone number."
        })
        return

    answer = confirmation.strip().lower()

    if answer not in ["yes", "yes that's correct", "correct", "confirmed"]:
        await params.result_callback({
            "success": False,
            "message": "The caller has not confirmed the phone number."
        })
        return

    resources["confirmed_phone"] = phone

    await params.result_callback({
        "success": True,
        "message": "Phone number confirmed. You may proceed with the requested action."
    })


async def book_appointment(
    params: FunctionCallParams,
    doctor_id: int,
    date: str,
    time: str,
    phone: str,
):
    """Book an appointment after the caller has confirmed their phone number."""

    resources = params.app_resources or {}

    if resources.get("confirmed_phone") != phone:
        await params.result_callback({
            "success": False,
            "message": "Phone number confirmation is required before booking."
        })
        return

    result = book_appointment_tool(
        doctor_id,
        date,
        time,
        phone,
        True,
    )

    resources.pop("confirmed_phone", None)

    await params.result_callback(result)


async def cancel_appointment(
    params: FunctionCallParams,
    phone: str,
):
    """Cancel an appointment after the caller has confirmed their phone number."""

    resources = params.app_resources or {}

    if resources.get("confirmed_phone") != phone:
        await params.result_callback({
            "success": False,
            "message": "Phone number confirmation is required before cancellation."
        })
        return

    result = cancel_appointment_tool(phone, True)

    resources.pop("confirmed_phone", None)

    await params.result_callback(result)
