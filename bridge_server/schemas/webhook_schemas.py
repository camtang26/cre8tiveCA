from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any, List

class CalComWebhookPayload(BaseModel):
    """
    Expected payload from ElevenLabs webhook for Cal.com scheduling.
    Updated to match the actual fields sent by the curl command/agent.
    """
    attendee_name: str = Field(..., description="Name of the person attending the event.")
    attendee_email: EmailStr = Field(..., description="Email of the person attending the event.")
    attendee_timezone: Optional[str] = Field("America/New_York", description="Timezone of the attendee (e.g., 'Australia/Brisbane'). Defaults to America/New_York if not provided.")
    event_type_id: int = Field(..., description="Cal.com event type ID.")
    start_time_utc: str = Field(..., description="Requested start date and time for the consultation in UTC (ISO 8601 format, e.g., YYYY-MM-DDTHH:MM:SSZ).")
    end_time_utc: Optional[str] = Field(None, description="Requested end date and time for the consultation in UTC (ISO 8601 format). Optional, as event type might have fixed duration.")
    guests: Optional[List[EmailStr]] = Field(None, description="List of guest email addresses.")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the booking.")
    language: Optional[str] = Field("en", description="Language for the booking notifications (e.g., 'en'). Defaults to 'en'.")
    # additional_notes: Optional[str] = Field(None, description="Any additional notes from the user.") # This was not in the curl


class OutlookEmailWebhookPayload(BaseModel):
    """
    Expected payload from ElevenLabs webhook for sending an Outlook email.
    The agent is expected to compose the email content.
    """
    recipient_email: EmailStr = Field(..., description="Email address of the recipient.")
    email_subject: str = Field(..., description="Subject of the email.")
    email_body_html: str = Field(..., description="HTML content of the email body.")
    save_to_sent_items: Optional[bool] = Field(True, description="Whether to save the email in the sender's Sent Items folder.")
    # We might receive other dynamic parameters from ElevenLabs
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional dynamic parameters from ElevenLabs.")