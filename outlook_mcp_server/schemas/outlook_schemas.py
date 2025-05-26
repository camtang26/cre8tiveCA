from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class SendOutlookEmailInput(BaseModel):
    recipientEmail: EmailStr = Field(..., description="The recipient's email address.")
    emailSubject: str = Field(..., description="The subject line of the email.")
    emailBodyHtml: str = Field(..., description="The HTML content of the email body.")
    saveToSentItems: Optional[bool] = Field(default=True, description="Whether to save the email in the Sent Items folder.")

class SendOutlookEmailOutput(BaseModel):
    success: bool
    message: str
    details: Optional[str] = None # For any error details or API responses