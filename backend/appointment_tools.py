
from fastapi import HTTPException

from main import (
    DOCTORS,
    load_appointments,
    check_doctor_availability,
    book_appointment as backend_book_appointment,
    cancel_appointment as backend_cancel_appointment,
    BookingRequest,
    CancellationRequest,
)


def check_doctor_availability_tool(speciality: str, date: str):
    """Find doctors and available appointment slots."""
    return check_doctor_availability(speciality, date)


def book_appointment_tool(
    doctor_id: int,
    date: str,
    time: str,
    phone: str,
    phone_confirmed: bool,
):
    """Book an appointment after the caller confirms their phone number."""
    try:
        request = BookingRequest(
            doctor_id=doctor_id,
            date=date,
            time=time,
            phone=phone,
            phone_confirmed=phone_confirmed,
        )
        return backend_book_appointment(request)

    except HTTPException as error:
        return {
            "success": False,
            "message": error.detail,
        }


def cancel_appointment_tool(
    phone: str,
    phone_confirmed: bool,
):
    """Cancel the latest active appointment after phone confirmation."""
    try:
        request = CancellationRequest(
            phone=phone,
            phone_confirmed=phone_confirmed,
        )
        return backend_cancel_appointment(request)

    except HTTPException as error:
        return {
            "success": False,
            "message": error.detail,
        }
