from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any

from cal_com_mcp_server.core.config import DEFAULT_EVENT_TYPE_ID, DEFAULT_EVENT_DURATION_MINUTES

class CreateCalComBookingInput(BaseModel):
    localDate: str = Field(..., description="Local date for the booking (YYYY-MM-DD)")
    localTime: str = Field(..., description="Local time for the booking (HH:MM, 24-hour format)")
    localTimeZone: str = Field(..., description="Local IANA timezone string (e.g., Australia/Sydney)")
    attendeeName: str = Field(..., description="Full name of the attendee")
    attendeeEmail: EmailStr = Field(..., description="Email address of the attendee")
    eventDurationMinutes: Optional[int] = Field(default=DEFAULT_EVENT_DURATION_MINUTES, description="Duration of the event in minutes")
    eventTypeId: Optional[int] = Field(default=DEFAULT_EVENT_TYPE_ID, description="The Cal.com Event Type ID")

class BookingOutputDetails(BaseModel):
    # Define fields based on expected Cal.com API response or your custom needs
    # This is a placeholder; adjust based on actual booking_result structure
    uid: Optional[str] = None
    title: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    # ... other relevant fields from Cal.com booking response
    error_step: Optional[str] = None
    api_response: Optional[Any] = None


class CreateCalComBookingOutput(BaseModel):
    success: bool
    message: str
    bookingDetails: Optional[BookingOutputDetails] = None