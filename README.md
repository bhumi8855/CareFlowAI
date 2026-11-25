# CareFlowAI – Voice AI Doctor Appointment Assistant

CareFlowAI is a voice-enabled doctor appointment assistant built using React, FastAPI, Pipecat, Gemini, and ElevenLabs.

## Features

- Real-time browser voice call interface.
- Speech-to-text using ElevenLabs.
- AI conversation using Google Gemini.
- Text-to-speech using ElevenLabs.
- Doctor and speciality availability checking.
- Appointment booking and cancellation tools.
- Spoken phone-number confirmation before booking or cancellation.
- Dashboard displaying doctors, slots, and appointments.
- Mock appointment data stored in JSON.

## Technology Stack

- Frontend: React, Vite, JavaScript
- Backend: Python, FastAPI
- Voice orchestration: Pipecat
- STT/TTS: ElevenLabs
- LLM: Google Gemini (`gemini-3.5-flash-lite`)
- Storage: JSON

## Architecture

Browser microphone → Pipecat WebRTC → ElevenLabs STT → Gemini LLM → Appointment function tools → ElevenLabs TTS → Browser audio.

## Project Structure

```text
CareFlowAI/
├── backend/
│   ├── main.py
│   ├── bot.py
│   ├── voice_tools.py
│   ├── appointment_tools.py
│   ├── appointments.json
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── .gitignore
└── README.md
```

## Prerequisites

- Python 3.13
- Node.js and npm
- Gemini API key
- ElevenLabs API key and voice ID

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/bhumi8855/CareFlowAI.git
cd CareFlowAI
```

### 2. Configure the backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Add your API credentials to `backend/.env`:

```env
GEMINI_API_KEY=your_gemini_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=your_elevenlabs_voice_id
```

### 3. Start the FastAPI backend

From the backend directory:

```bash
uvicorn main:app --reload --port 8000
```

### 4. Start the Pipecat voice server

Open another terminal:

```bash
cd CareFlowAI/backend
venv\Scripts\activate
python bot.py
```

The voice server runs on port 7860.

### 5. Start the frontend

Open a third terminal:

```bash
cd CareFlowAI/frontend
npm install
npm run dev
```

Open the local Vite URL shown in the terminal, usually `http://localhost:5173`.

Allow microphone access when prompted.

## Appointment Tools

- `check_doctor_availability`: Checks available doctors and slots.
- `book_appointment`: Books an appointment after phone-number confirmation.
- `cancel_appointment`: Cancels an appointment after phone-number confirmation.

The assistant asks the caller to speak their phone number, repeats it for confirmation, and only proceeds after explicit confirmation.

## Data Storage

Doctor information and appointment records use mock data. Appointment records are persisted in `appointments.json`.

## Notes

This is an internship assignment prototype. The project uses mock doctor and appointment data rather than a live hospital database. Voice integration and end-to-end function-call behavior may require further validation.
