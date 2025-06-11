"""
Direct Cal.com API client - bypasses MCP layer
"""
import httpx
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import pytz
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)

class CalComBookingInput(BaseModel):
    """Input for creating a Cal.com booking"""
    localDate: str  # YYYY-MM-DD
    localTime: str  # HH:MM
    localTimeZone: str  # IANA timezone
    attendeeName: str
    attendeeEmail: EmailStr
    eventTypeId: int
    eventDurationMinutes: Optional[int] = 30
    guests: Optional[List[EmailStr]] = []
    metadata: Optional[Dict[str, Any]] = {}
    language: Optional[str] = "en"

class CalComBookingOutput(BaseModel):
    """Output from Cal.com booking creation"""
    success: bool
    message: str
    booking_id: Optional[str] = None
    booking_uid: Optional[str] = None
    title: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    meet_url: Optional[str] = None
    booking_details: Optional[Dict[str, Any]] = None
    error_details: Optional[str] = None

class CalComDirectClient:
    """Direct client for Cal.com API v2"""
    
    def __init__(self, api_key: str, api_base_url: str = "https://api.cal.com/v2"):
        self.api_key = api_key
        self.api_base_url = api_base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "cal-api-version": "2024-08-13"  # Required for Cal.com API v2
        }
    
    def _convert_to_utc(self, local_date: str, local_time: str, timezone_str: str) -> datetime:
        """Convert local date/time to UTC"""
        try:
            tz = pytz.timezone(timezone_str)
            local_dt = datetime.strptime(f"{local_date} {local_time}", "%Y-%m-%d %H:%M")
            local_dt = tz.localize(local_dt)
            return local_dt.astimezone(pytz.UTC)
        except Exception as e:
            logger.error(f"Error converting to UTC: {e}")
            raise
    
    # REMOVED: check_availability method - Cal.com API already validates availability during booking creation
    # This eliminates an unnecessary API call and improves performance
    
    async def create_booking(self, booking_input: CalComBookingInput) -> CalComBookingOutput:
        """Create a booking in Cal.com"""
        try:
            # Convert local time to UTC
            start_utc = self._convert_to_utc(
                booking_input.localDate,
                booking_input.localTime,
                booking_input.localTimeZone
            )
            
            # Calculate end time
            duration_minutes = booking_input.eventDurationMinutes or 30
            end_utc = start_utc + timedelta(minutes=duration_minutes)
            
            # Skip availability check - Cal.com API will validate during booking creation
            # This improves performance by eliminating an extra API call
            
            # Prepare booking data for Cal.com API v2
            booking_data = {
                "eventTypeId": booking_input.eventTypeId,
                "start": start_utc.isoformat(),
                "attendee": {
                    "name": booking_input.attendeeName,
                    "email": booking_input.attendeeEmail,
                    "timeZone": booking_input.localTimeZone,
                    "language": booking_input.language or "en"
                },
                "metadata": booking_input.metadata or {}
            }
            
            # Add guests if provided
            if booking_input.guests:
                booking_data["guests"] = booking_input.guests
            
            # Create the booking with optimized timeout and connection pooling
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(10.0, connect=5.0),  # Reduced from 30s
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            ) as client:
                response = await client.post(
                    f"{self.api_base_url}/bookings",
                    headers=self.headers,
                    json=booking_data
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    booking_info = result.get("data", result)
                    
                    return CalComBookingOutput(
                        success=True,
                        message="Booking created successfully",
                        booking_id=str(booking_info.get("id", "")),
                        booking_uid=booking_info.get("uid", ""),
                        title=booking_info.get("title", "Meeting"),
                        start_time=start_utc.isoformat(),
                        end_time=end_utc.isoformat(),
                        meet_url=booking_info.get("meetingUrl", ""),
                        booking_details={
                            "id": booking_info.get("id"),
                            "uid": booking_info.get("uid"),
                            "title": booking_info.get("title"),
                            "startTime": start_utc.isoformat(),
                            "endTime": end_utc.isoformat(),
                            "attendees": [{
                                "name": booking_input.attendeeName,
                                "email": booking_input.attendeeEmail
                            }],
                            "status": "accepted",
                            "eventTypeId": booking_input.eventTypeId
                        }
                    )
                else:
                    error_msg = f"Cal.com API error: {response.status_code}"
                    try:
                        error_data = response.json()
                        error_msg = f"{error_msg} - {error_data}"
                    except:
                        error_msg = f"{error_msg} - {response.text}"
                    
                    return CalComBookingOutput(
                        success=False,
                        message="Failed to create booking",
                        error_details=error_msg
                    )
                    
        except Exception as e:
            logger.exception("Error creating Cal.com booking")
            return CalComBookingOutput(
                success=False,
                message="An error occurred while creating the booking",
                error_details=str(e)
            )