import httpx
import json
from .config import (
    AZURE_TENANT_ID,
    AZURE_CLIENT_ID,
    AZURE_CLIENT_SECRET,
    SENDER_UPN,
    GRAPH_API_BASE_URL,
    GRAPH_API_SCOPES
)

# In-memory cache for the access token (in a real app, consider a more robust cache)
_cached_token = None

async def get_graph_api_access_token() -> str | None:
    """
    Retrieves an access token for Microsoft Graph API using client credentials flow.
    Caches the token in memory.
    """
    global _cached_token
    # Basic check if token exists and is not (naively) expired. 
    # A real implementation should check token expiry time.
    if _cached_token:
        # Here you would normally decode the token and check its 'exp' claim
        # For simplicity, we're not doing that. Assume it's valid if it exists.
        return _cached_token

    if not all([AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET]):
        print("Azure AD credentials not fully configured for Graph API.")
        return None

    token_url = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/v2.0/token"
    
    payload = {
        "client_id": AZURE_CLIENT_ID,
        "scope": " ".join(GRAPH_API_SCOPES), # Scopes are space-separated
        "client_secret": AZURE_CLIENT_SECRET,
        "grant_type": "client_credentials",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=payload, headers=headers)
            response.raise_for_status()
            token_data = response.json()
            _cached_token = token_data.get("access_token")
            # You might also want to store token_data.get("expires_in") to manage expiry
            return _cached_token
    except httpx.HTTPStatusError as e:
        print(f"HTTP error getting Graph API token: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        print(f"Error getting Graph API token: {e}")
        return None

async def send_email_via_graph_api(
    recipient_email: str,
    subject: str,
    body_html: str,
    save_to_sent_items: bool = True
) -> dict:
    """
    Sends an email using Microsoft Graph API.
    """
    if not SENDER_UPN:
        return {"success": False, "error": "Sender UPN (SENDER_UPN) not configured."}

    access_token = await get_graph_api_access_token()
    if not access_token:
        return {"success": False, "error": "Failed to obtain Graph API access token."}

    send_mail_url = f"{GRAPH_API_BASE_URL}/users/{SENDER_UPN}/sendMail"
    
    email_payload = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "HTML", # Assuming HTML body as per your prompt
                "content": body_html,
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": recipient_email,
                    }
                }
            ],
            # Add ccRecipients or bccRecipients if needed
        },
        "saveToSentItems": str(save_to_sent_items).lower() # API expects string "true" or "false"
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(send_mail_url, json=email_payload, headers=headers)
            
            # A 202 Accepted means the request was accepted for processing
            if response.status_code == 202:
                return {"success": True, "message": "Email send request accepted."}
            else:
                response.raise_for_status() # Will raise for other 4xx/5xx errors
                # Should not be reached if raise_for_status works as expected for non-202
                return {"success": False, "error": f"Unexpected status code: {response.status_code}", "details": response.text}

    except httpx.HTTPStatusError as e:
        error_details = e.response.text
        try:
            error_details = e.response.json()
        except:
            pass
        print(f"HTTP error sending email: {e.response.status_code} - {error_details}")
        return {"success": False, "error": f"Graph API Error: {e.response.status_code}", "details": error_details}
    except Exception as e:
        print(f"Error sending email: {e}")
        return {"success": False, "error": str(e)}