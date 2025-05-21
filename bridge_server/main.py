import logging
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from datetime import datetime, timezone # Added
import pytz # Added

# Schemas for webhook validation
from bridge_server.schemas.webhook_schemas import CalComWebhookPayload, OutlookEmailWebhookPayload

# MCP client utility functions
from bridge_server.mcp_clients.cal_com_client import call_cal_com_create_booking_tool, CreateCalComBookingClientInput, CreateCalComBookingClientOutput
from bridge_server.mcp_clients.outlook_client import call_outlook_send_email_tool, SendOutlookEmailClientInput, SendOutlookEmailClientOutput

# Configuration (MCP server URLs)
from bridge_server.core.config import CAL_COM_MCP_SERVER_URL, OUTLOOK_MCP_SERVER_URL

logging.basicConfig(level=logging.INFO) # Basic logging for the bridge server
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Bridge Server for ElevenLabs Agent",
    description="Receives webhooks from ElevenLabs and calls appropriate MCP tools.",
    version="0.1.0"
)

@app.on_event("startup")
async def startup_event():
    logger.info("Bridge Server starting up...")
    logger.info(f"Cal.com MCP Server URL: {CAL_COM_MCP_SERVER_URL}")
    logger.info(f"Outlook MCP Server URL: {OUTLOOK_MCP_SERVER_URL}")
    if not CAL_COM_MCP_SERVER_URL or not OUTLOOK_MCP_SERVER_URL:
        logger.error("One or more MCP Server URLs are not configured. Check .env file.")
        # Depending on strictness, you might want to raise an exception or prevent startup
    # You could add a quick check here to see if the MCP servers are reachable if desired

@app.post("/webhook/cal/schedule_consultation")
async def webhook_schedule_consultation(payload: CalComWebhookPayload, request: Request, background_tasks: BackgroundTasks):
    """
    Webhook endpoint to receive Cal.com scheduling requests from ElevenLabs.
    It then calls the Cal.com MCP server.
    """
    logger.info(f"Received Cal.com scheduling webhook. Payload: {payload.model_dump_json(indent=2)}")
    
    # Map webhook payload to the input schema of the Cal.com MCP client function
    # The CreateCalComBookingClientInput model in cal_com_client.py now expects fields
    # like localDate, localTime, attendeeName, etc.

    # Basic date/time splitting from ISO 8601 format.
    # This assumes payload.date_time is a valid ISO 8601 string like "2025-12-10T14:00:00Z"
    # For more robust parsing, especially with various timezone offsets, a library might be better,
    # but for "YYYY-MM-DDTHH:MM:SSZ" format, string splitting is straightforward.
    try:
        from datetime import datetime, timezone
        import pytz

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

    mcp_input = CreateCalComBookingClientInput(
        localDate=date_part,
        localTime=time_part,
        localTimeZone=payload.attendee_timezone,
        attendeeName=payload.attendee_name,
        attendeeEmail=payload.attendee_email, # Updated field name
        eventTypeId=payload.event_type_id,
        # eventDurationMinutes is not directly available from the new payload,
        # and the Cal.com API call for booking doesn't strictly need it if event type has fixed duration.
        # If it were needed, it would have to be calculated from start_time_utc and end_time_utc.
        # For now, we rely on the event_type_id defining the duration.
        # guests and metadata from the webhook payload are now part of CreateCalComBookingClientInput
        guests=payload.guests if payload.guests else [],
        metadata=payload.metadata if payload.metadata else {},
        language=payload.language if payload.language else "en"
    )

    # Call the MCP tool in the background to avoid blocking the webhook response
    # background_tasks.add_task(call_cal_com_create_booking_tool, mcp_input)
    
    # Or, if you need to wait for the result to respond to ElevenLabs:
    try:
        result: CreateCalComBookingClientOutput = await call_cal_com_create_booking_tool(mcp_input)
        if result.success:
            logger.info(f"Successfully processed Cal.com booking via MCP. Message: {result.message}")
            # Adapt this response to what ElevenLabs expects for a successful tool call
            return JSONResponse(
                status_code=200,
                content={"status": "success", "message": result.message, "details": result.booking_details.model_dump() if result.booking_details else None}
            )
        else:
            logger.error(f"Error processing Cal.com booking via MCP. Message: {result.message}")
            # Adapt this error response
            return JSONResponse(
                status_code=500, # Or a more appropriate error code
                content={"status": "error", "message": result.message, "details": result.error_details}
            )
    except Exception as e:
        logger.exception("Unhandled exception during Cal.com MCP call from webhook.")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Internal server error in Bridge: {str(e)}"}
        )

@app.post("/webhook/outlook/send_email")
async def webhook_send_email(payload: OutlookEmailWebhookPayload, request: Request, background_tasks: BackgroundTasks):
    """
    Webhook endpoint to receive Outlook email sending requests from ElevenLabs.
    It then calls the Outlook MCP server.
    """
    logger.info(f"Received Outlook email webhook. Payload: {payload.model_dump_json(indent=2)}")

    mcp_input = SendOutlookEmailClientInput(
        recipientEmail=payload.recipient_email, # Ensure field names match, using alias if needed
        emailSubject=payload.email_subject,
        emailBodyHtml=payload.email_body_html,
        saveToSentItems=payload.save_to_sent_items
    )

    # Call the MCP tool
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

@app.get("/")
async def root_info():
    return {"message": "Bridge Server is running. Webhook endpoints at /webhook/cal/schedule_consultation and /webhook/outlook/send_email"}

# To run this Bridge Server (example, adjust port as needed, e.g., 8000):
# 1. Ensure Cal.com MCP server is running (e.g., on port 8001)
# 2. Ensure Outlook MCP server is running (e.g., on port 8002)
# 3. Ensure .env file in bridge_server/ has CAL_COM_MCP_SERVER_URL and OUTLOOK_MCP_SERVER_URL
# 4. From the PARENT directory of bridge_server (i.e., your project root):
#    uvicorn bridge_server.main:app --port 8000 --reload