import logging
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import pytz

# Schemas for webhook validation
from schemas.webhook_schemas import CalComWebhookPayload, OutlookEmailWebhookPayload

# Configuration
from core.config import (
    CAL_COM_MCP_SERVER_URL, OUTLOOK_MCP_SERVER_URL,
    CAL_COM_API_KEY, CAL_COM_API_BASE_URL, DEFAULT_EVENT_TYPE_ID,
    AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, SENDER_UPN,
    INTEGRATION_MODE
)

# Import based on integration mode
if INTEGRATION_MODE == "mcp":
    # MCP client utility functions
    from mcp_clients.cal_com_client import call_cal_com_create_booking_tool, CreateCalComBookingClientInput, CreateCalComBookingClientOutput
    from mcp_clients.outlook_client import call_outlook_send_email_tool, SendOutlookEmailClientInput, SendOutlookEmailClientOutput
else:
    # Direct API clients
    from api_clients.cal_com_direct import CalComDirectClient, CalComBookingInput, CalComBookingOutput
    from api_clients.outlook_direct import OutlookDirectClient, OutlookEmailInput, OutlookEmailOutput

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Bridge Server for ElevenLabs Agent",
    description="Receives webhooks from ElevenLabs and calls appropriate tools (MCP or Direct API).",
    version="0.2.0"
)

# Initialize direct API clients if in direct mode
if INTEGRATION_MODE == "direct":
    cal_com_client = CalComDirectClient(
        api_key=CAL_COM_API_KEY,
        api_base_url=CAL_COM_API_BASE_URL
    )
    outlook_client = OutlookDirectClient(
        tenant_id=AZURE_TENANT_ID,
        client_id=AZURE_CLIENT_ID,
        client_secret=AZURE_CLIENT_SECRET,
        sender_upn=SENDER_UPN
    )

@app.on_event("startup")
async def startup_event():
    logger.info("Bridge Server starting up...")
    logger.info(f"Integration mode: {INTEGRATION_MODE}")
    
    if INTEGRATION_MODE == "mcp":
        logger.info(f"Cal.com MCP Server URL: {CAL_COM_MCP_SERVER_URL}")
        logger.info(f"Outlook MCP Server URL: {OUTLOOK_MCP_SERVER_URL}")
        if not CAL_COM_MCP_SERVER_URL or not OUTLOOK_MCP_SERVER_URL:
            logger.error("One or more MCP Server URLs are not configured. Check .env file.")
    else:
        logger.info("Using direct API integration")
        if not CAL_COM_API_KEY:
            logger.error("Cal.com API key not configured. Check .env file.")
        if not all([AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, SENDER_UPN]):
            logger.error("Azure/Outlook credentials not fully configured. Check .env file.")

@app.post("/webhook/cal/schedule_consultation")
async def webhook_schedule_consultation(payload: CalComWebhookPayload, request: Request, background_tasks: BackgroundTasks):
    """
    Webhook endpoint to receive Cal.com scheduling requests from ElevenLabs.
    Routes to either MCP server or direct API based on configuration.
    """
    logger.info(f"Received Cal.com scheduling webhook. Payload: {payload.model_dump_json(indent=2)}")
    
    # Parse and convert timezone
    try:
        # Parse the incoming UTC datetime string
        utc_dt = datetime.strptime(payload.start_time_utc, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        
        # Convert UTC datetime to the attendee's local timezone
        attendee_tz_str = payload.attendee_timezone
        try:
            attendee_tz = pytz.timezone(attendee_tz_str)
        except pytz.UnknownTimeZoneError:
            logger.error(f"Unknown attendee_timezone: {attendee_tz_str}")
            return JSONResponse(status_code=400, content={"status": "error", "message": f"Unknown attendee_timezone: {attendee_tz_str}"})

        local_dt = utc_dt.astimezone(attendee_tz)
        
        date_part = local_dt.strftime("%Y-%m-%d")
        time_part = local_dt.strftime("%H:%M")
        
        logger.info(f"Original UTC: {payload.start_time_utc}, Attendee TZ: {attendee_tz_str}, Converted Local DT: {local_dt.isoformat()}, Date Part: {date_part}, Time Part: {time_part}")

    except ValueError as e:
        logger.error(f"Error parsing start_time_utc '{payload.start_time_utc}' or converting timezone: {e}")
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": f"Invalid start_time_utc format or timezone issue: {payload.start_time_utc}. Expected ISO 8601 like YYYY-MM-DDTHH:MM:SSZ."}
        )

    # Route based on integration mode
    if INTEGRATION_MODE == "mcp":
        # MCP approach
        mcp_input = CreateCalComBookingClientInput(
            localDate=date_part,
            localTime=time_part,
            localTimeZone=payload.attendee_timezone,
            attendeeName=payload.attendee_name,
            attendeeEmail=payload.attendee_email,
            eventTypeId=payload.event_type_id,
            guests=payload.guests if payload.guests else [],
            metadata=payload.metadata if payload.metadata else {},
            language=payload.language if payload.language else "en"
        )
        
        try:
            result: CreateCalComBookingClientOutput = await call_cal_com_create_booking_tool(mcp_input)
            if result.success:
                logger.info(f"Successfully processed Cal.com booking via MCP. Message: {result.message}")
                return JSONResponse(
                    status_code=200,
                    content={"status": "success", "message": result.message, "details": result.booking_details.model_dump() if result.booking_details else None}
                )
            else:
                logger.error(f"Error processing Cal.com booking via MCP. Message: {result.message}")
                return JSONResponse(
                    status_code=500,
                    content={"status": "error", "message": result.message, "details": result.error_details}
                )
        except Exception as e:
            logger.exception("Unhandled exception during Cal.com MCP call from webhook.")
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": f"Internal server error in Bridge: {str(e)}"}
            )
    
    else:
        # Direct API approach
        direct_input = CalComBookingInput(
            eventTypeId=payload.event_type_id or DEFAULT_EVENT_TYPE_ID,
            start=payload.start_time_utc,
            end=payload.end_time_utc,
            attendee=CalComBookingInput.Attendee(
                name=payload.attendee_name,
                email=payload.attendee_email,
                timeZone=payload.attendee_timezone,
                language=payload.language or "en"
            ),
            guests=payload.guests or [],
            metadata=payload.metadata or {}
        )
        
        try:
            result: CalComBookingOutput = await cal_com_client.create_booking(direct_input)
            if result.success:
                logger.info(f"Successfully processed Cal.com booking via direct API. Message: {result.message}")
                return JSONResponse(
                    status_code=200,
                    content={
                        "status": "success", 
                        "message": result.message, 
                        "details": {
                            "id": result.booking_id,
                            "uid": result.booking_uid,
                            "title": result.title,
                            "start_time": result.start_time,
                            "end_time": result.end_time,
                            "meet_url": result.meet_url
                        } if result.booking_id else None
                    }
                )
            else:
                logger.error(f"Error processing Cal.com booking via direct API. Message: {result.message}")
                return JSONResponse(
                    status_code=500,
                    content={"status": "error", "message": result.message, "details": result.error_details}
                )
        except Exception as e:
            logger.exception("Unhandled exception during Cal.com direct API call from webhook.")
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": f"Internal server error in Bridge: {str(e)}"}
            )

@app.post("/webhook/outlook/send_email")
async def webhook_send_email(payload: OutlookEmailWebhookPayload, request: Request, background_tasks: BackgroundTasks):
    """
    Webhook endpoint to receive Outlook email sending requests from ElevenLabs.
    Routes to either MCP server or direct API based on configuration.
    """
    logger.info(f"Received Outlook email webhook. Payload: {payload.model_dump_json(indent=2)}")

    # Route based on integration mode
    if INTEGRATION_MODE == "mcp":
        # MCP approach
        mcp_input = SendOutlookEmailClientInput(
            recipientEmail=payload.recipient_email,
            emailSubject=payload.email_subject,
            emailBodyHtml=payload.email_body_html,
            saveToSentItems=payload.save_to_sent_items
        )

        try:
            result: SendOutlookEmailClientOutput = await call_outlook_send_email_tool(mcp_input)
            if result.success:
                logger.info(f"Successfully processed Outlook email sending via MCP. Message: {result.message}")
                return JSONResponse(
                    status_code=200,
                    content={"status": "success", "message": result.message}
                )
            else:
                logger.error(f"Error processing Outlook email sending via MCP. Message: {result.message}")
                return JSONResponse(
                    status_code=500,
                    content={"status": "error", "message": result.message, "details": result.details}
                )
        except Exception as e:
            logger.exception("Unhandled exception during Outlook MCP call from webhook.")
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": f"Internal server error in Bridge: {str(e)}"}
            )
    
    else:
        # Direct API approach
        direct_input = OutlookEmailInput(
            recipientEmail=payload.recipient_email,
            emailSubject=payload.email_subject,
            emailBodyHtml=payload.email_body_html,
            saveToSentItems=payload.save_to_sent_items
        )
        
        try:
            result: OutlookEmailOutput = await outlook_client.send_email(direct_input)
            if result.success:
                logger.info(f"Successfully sent email via direct API. Message: {result.message}")
                return JSONResponse(
                    status_code=200,
                    content={"status": "success", "message": result.message, "messageId": result.message_id}
                )
            else:
                logger.error(f"Error sending email via direct API. Message: {result.message}")
                return JSONResponse(
                    status_code=500,
                    content={"status": "error", "message": result.message, "details": result.error_details}
                )
        except Exception as e:
            logger.exception("Unhandled exception during Outlook direct API call from webhook.")
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": f"Internal server error in Bridge: {str(e)}"}
            )

@app.get("/")
async def root_info():
    mode_info = f" (Mode: {INTEGRATION_MODE})"
    return {"message": f"Bridge Server is running{mode_info}. Webhook endpoints at /webhook/cal/schedule_consultation and /webhook/outlook/send_email"}

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "integration_mode": INTEGRATION_MODE,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# To run this Bridge Server:
# 1. Set INTEGRATION_MODE in .env to either "mcp" or "direct"
# 2. For MCP mode: Ensure MCP servers are running and URLs are set
# 3. For Direct mode: Ensure API credentials are set in .env
# 4. From the project root: uvicorn bridge_server.main:app --port 8000 --reload