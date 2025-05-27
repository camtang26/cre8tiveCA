"""
Direct Microsoft Graph API client for Outlook - bypasses MCP layer
"""
import httpx
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)

class OutlookEmailInput(BaseModel):
    """Input for sending an email via Outlook"""
    recipientEmail: EmailStr
    emailSubject: str
    emailBodyHtml: str
    saveToSentItems: bool = True

class OutlookEmailOutput(BaseModel):
    """Output from email sending"""
    success: bool
    message: str
    message_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    error_details: Optional[str] = None

class OutlookDirectClient:
    """Direct client for Microsoft Graph API"""
    
    def __init__(
        self, 
        tenant_id: str, 
        client_id: str, 
        client_secret: str, 
        sender_upn: str
    ):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.sender_upn = sender_upn
        self.graph_base_url = "https://graph.microsoft.com/v1.0"
        self._access_token = None
        self._token_expiry = None
    
    async def _get_access_token(self) -> str:
        """Get or refresh the access token"""
        # Check if we have a valid token
        if self._access_token and self._token_expiry and datetime.utcnow() < self._token_expiry:
            return self._access_token
        
        # Get new token
        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    token_url,
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "scope": "https://graph.microsoft.com/.default",
                        "grant_type": "client_credentials"
                    }
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    self._access_token = token_data["access_token"]
                    # Set expiry 5 minutes before actual expiry
                    expires_in = token_data.get("expires_in", 3600)
                    self._token_expiry = datetime.utcnow() + timedelta(seconds=expires_in - 300)
                    return self._access_token
                else:
                    error_msg = f"Failed to get access token: {response.status_code}"
                    try:
                        error_data = response.json()
                        error_msg = f"{error_msg} - {error_data}"
                    except:
                        error_msg = f"{error_msg} - {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                    
            except Exception as e:
                logger.exception("Error getting access token")
                raise
    
    async def send_email(self, email_input: OutlookEmailInput) -> OutlookEmailOutput:
        """Send an email using Microsoft Graph API"""
        try:
            # Get access token
            access_token = await self._get_access_token()
            
            # Prepare email message
            message = {
                "message": {
                    "subject": email_input.emailSubject,
                    "body": {
                        "contentType": "HTML",
                        "content": email_input.emailBodyHtml
                    },
                    "toRecipients": [
                        {
                            "emailAddress": {
                                "address": email_input.recipientEmail
                            }
                        }
                    ]
                },
                "saveToSentItems": email_input.saveToSentItems
            }
            
            # Send the email
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.graph_base_url}/users/{self.sender_upn}/sendMail",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json=message
                )
                
                if response.status_code in [200, 201, 202]:
                    # Success - Graph API returns 202 Accepted for sendMail
                    return OutlookEmailOutput(
                        success=True,
                        message=f"Email sent successfully to {email_input.recipientEmail}",
                        details={
                            "recipient": email_input.recipientEmail,
                            "subject": email_input.emailSubject,
                            "saved_to_sent": email_input.saveToSentItems,
                            "sent_at": datetime.utcnow().isoformat()
                        }
                    )
                else:
                    error_msg = f"Graph API error: {response.status_code}"
                    try:
                        error_data = response.json()
                        error_msg = f"{error_msg} - {error_data}"
                        
                        # Extract specific error message if available
                        if "error" in error_data:
                            error_msg = error_data["error"].get("message", error_msg)
                    except:
                        error_msg = f"{error_msg} - {response.text}"
                    
                    return OutlookEmailOutput(
                        success=False,
                        message="Failed to send email",
                        error_details=error_msg,
                        details={"error": error_msg}
                    )
                    
        except Exception as e:
            logger.exception("Error sending email via Outlook")
            return OutlookEmailOutput(
                success=False,
                message="An error occurred while sending the email",
                error_details=str(e),
                details={"error": str(e)}
            )
    
    async def test_connection(self) -> bool:
        """Test the connection to Microsoft Graph API"""
        try:
            access_token = await self._get_access_token()
            
            # Try to get user info
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.graph_base_url}/users/{self.sender_upn}",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    logger.info(f"Successfully connected to Graph API. User: {user_data.get('displayName', 'Unknown')}")
                    return True
                else:
                    logger.error(f"Failed to connect to Graph API: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False