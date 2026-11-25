
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import json

app = FastAPI(title="CareFlow AI Backend")

# Allow React frontend to communicate with Python backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = Path(__file__).parent / "appointments.json"

DOCTORS = [
    {
        "id": 1,
        "name": "Dr. Aditi Sharma",
        "speciality": "Cardiology",
        "experience": "12 years",
        "slots": ["10:00 AM", "11:30 AM", "02:00 PM"]
    },
    {
        "id": 2,
        "name": "Dr. Rahul Mehta",
        "speciality": "Dermatology",
        "experience": "9 years",
        "slots": ["09:30 AM", "12:00 PM", "04:00 PM"]
    },
    {
        "id": 3,
        "name": "Dr. Neha Patel",
        "speciality": "Neurology",
        "experience": "15 years",
        "slots": ["10:30 AM", "01:00 PM", "03:30 PM"]
    }
]


def load_appointments():
    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")

    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def save_appointments(appointments):
    DATA_FILE.write_text(
        json.dumps(appointments, indent=4),
        encoding="utf-8"
    )


class BookingRequest(BaseModel):
    doctor_id: int
    date: str
    time: str
    phone: str
    phone_confirmed: bool


class CancellationRequest(BaseModel):
    phone: str
    phone_confirmed: bool


@app.get("/")
def home():
    return {"message": "CareFlow AI Backend is running!"}


@app.get("/api/doctors")
def get_doctors():
    return DOCTORS


@app.get("/api/appointments")
def get_appointments():
    return load_appointments()


@app.get("/api/availability")
def check_doctor_availability(speciality: str, date: str):
    appointments = load_appointments()

    available_doctors = []

    for doctor in DOCTORS:
        if speciality.lower() not in ["all", doctor["speciality"].lower()]:
            continue

        available_slots = [
            slot for slot in doctor["slots"]
            if not any(
                appointment["doctor_id"] == doctor["id"]
                and appointment["date"] == date
                and appointment["time"] == slot
                and appointment["status"] == "Booked"
                for appointment in appointments
            )
        ]

        available_doctors.append({
            **doctor,
            "available_slots": available_slots
        })

    return available_doctors


@app.post("/api/book")
def book_appointment(request: BookingRequest):
    if not request.phone_confirmed:
        raise HTTPException(
            status_code=400,
            detail="Phone number must be confirmed before booking."
        )

    if not request.phone.isdigit() or len(request.phone) != 10:
        raise HTTPException(
            status_code=400,
            detail="Enter a valid 10-digit phone number."
        )

    doctor = next(
        (d for d in DOCTORS if d["id"] == request.doctor_id),
        None
    )

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found.")

    if request.time not in doctor["slots"]:
        raise HTTPException(status_code=400, detail="Invalid time slot.")

    appointments = load_appointments()

    for appointment in appointments:
        if (
            appointment["doctor_id"] == request.doctor_id
            and appointment["date"] == request.date
            and appointment["time"] == request.time
            and appointment["status"] == "Booked"
        ):
            raise HTTPException(
                status_code=409,
                detail="This appointment slot is already booked."
            )

    new_appointment = {
        "id": len(appointments) + 1,
        "doctor_id": doctor["id"],
        "doctor_name": doctor["name"],
        "speciality": doctor["speciality"],
        "date": request.date,
        "time": request.time,
        "phone": request.phone,
        "status": "Booked"
    }

    appointments.append(new_appointment)
    save_appointments(appointments)

    return {
        "message": "Appointment booked successfully!",
        "appointment": new_appointment
    }


@app.post("/api/cancel")
def cancel_appointment(request: CancellationRequest):
    if not request.phone_confirmed:
        raise HTTPException(
            status_code=400,
            detail="Phone number must be confirmed before cancellation."
        )

    if not request.phone.isdigit() or len(request.phone) != 10:
        raise HTTPException(
            status_code=400,
            detail="Enter a valid 10-digit phone number."
        )

    appointments = load_appointments()

    active = [
        appointment for appointment in appointments
        if appointment["phone"] == request.phone
        and appointment["status"] == "Booked"
    ]

    if not active:
        raise HTTPException(
            status_code=404,
            detail="No active appointment found for this phone number."
        )

    appointment = active[-1]
    appointment["status"] = "Cancelled"

    save_appointments(appointments)

    return {
        "message": "Appointment cancelled successfully!",
        "appointment": appointment
    }
