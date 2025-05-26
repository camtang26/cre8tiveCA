from mcp.server.fastmcp import FastMCP, Context as MCPContext # Renaming to avoid conflict if we use FastAPI's ContextVar
from mcp.types import TextContent # Corrected import for TextContent
import datetime # Import the full datetime module
from datetime import timedelta

try:
    from ..core.config import DEFAULT_EVENT_TYPE_ID, DEFAULT_EVENT_DURATION_MINUTES
    from ..core.cal_api_utils import (
        convert_to_utc,
        check_availability,
        create_cal_booking_api_call,
    )
    from ..schemas.cal_com_schemas import CreateCalComBookingInput, CreateCalComBookingOutput, BookingOutputDetails
except ImportError:
    # Fallback for when running as main module
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.config import DEFAULT_EVENT_TYPE_ID, DEFAULT_EVENT_DURATION_MINUTES
    from core.cal_api_utils import (
        convert_to_utc,
        check_availability,
        create_cal_booking_api_call,
    )
    from schemas.cal_com_schemas import CreateCalComBookingInput, CreateCalComBookingOutput, BookingOutputDetails


# Create an MCP server instance using FastMCP
# This instance will be imported into main.py
cal_com_mcp_instance = FastMCP(
    name="cal_com_tools_server", # Can be different from the main server name in main.py if needed
    description="Tools for Cal.com integration",
    host="localhost", # Default host
    port=8001        # Default port for this server
)

# Pydantic models are already imported above with relative paths

@cal_com_mcp_instance.tool(
    name="create_cal_com_booking_mcp",
    description="Schedules a booking on Cal.com. It converts local time to UTC, checks availability, and then creates the booking."
    # input_schema and output_schema are removed; FastMCP infers from type hints
)
async def create_cal_com_booking_mcp_tool(args: CreateCalComBookingInput, ctx: MCPContext) -> CreateCalComBookingOutput:
    """
    MCP Tool to handle Cal.com booking process:
    1. Convert local time to UTC.
    2. Check slot availability.
    3. Create booking if available.
    """
    # Access arguments via Pydantic model attributes
    local_date = args.localDate
    local_time = args.localTime
    local_tz = args.localTimeZone
    attendee_name = args.attendeeName
    attendee_email = args.attendeeEmail
    duration_minutes = args.eventDurationMinutes # Will use default from Pydantic model if not provided
    event_type_id = args.eventTypeId         # Will use default from Pydantic model if not provided

    utc_start_iso = await convert_to_utc(local_date, local_time, local_tz)
    if not utc_start_iso:
        return {
            "success": False,
            "message": "Failed to convert provided local time to UTC.",
            "bookingDetails": {"error_step": "utc_conversion"},
        }

    try:
        # Calculate UTC end time
        start_dt_obj = datetime.datetime.fromisoformat(utc_start_iso.replace("Z", "+00:00"))
        end_dt_obj = start_dt_obj + timedelta(minutes=duration_minutes)
        utc_end_iso = end_dt_obj.strftime("%Y-%m-%dT%H:%M:%SZ")
    except ValueError as e:
        return {
            "success": False,
            "message": f"Invalid UTC start time format for duration calculation: {utc_start_iso}. Error: {e}",
            "bookingDetails": {"error_step": "duration_calculation", "utc_start_iso": utc_start_iso},
        }

    is_available = await check_availability(
        utc_start_time_iso=utc_start_iso,
        utc_end_time_iso=utc_end_iso,
        event_type_id=event_type_id
    )

    if not is_available:
        return {
            "success": False,
            "message": f"The requested time slot ({local_date} {local_time} {local_tz}) is not available for event type ID {event_type_id}.",
            "bookingDetails": {"error_step": "availability_check", "requested_slot_utc": utc_start_iso},
        }

    booking_result = await create_cal_booking_api_call(
        utc_start_time_iso=utc_start_iso,
        event_type_id=event_type_id,
        attendee_name=attendee_name,
        attendee_email=attendee_email,
        attendee_timezone=local_tz # Cal.com API for booking uses local timezone for attendee
    )

    if booking_result.get("success"):
        return {
            "success": True,
            "message": "Booking successfully created.",
            "bookingDetails": booking_result.get("data"),
        }
    else:
        return {
            "success": False,
            "message": f"Failed to create booking: {booking_result.get('error', 'Unknown error')}",
            "bookingDetails": {
                "error_step": "booking_creation", 
                "api_response": booking_result.get("details", booking_result.get("error"))
            },
        }

# Example of how the MCP server might return content for the LLM
# This is a helper and not directly part of the tool's return dict for programmatic use,
# but shows how an MCP server might structure a text response.
def format_tool_response_for_llm(tool_result: dict) -> list[TextContent]:
    if tool_result["success"]:
        details = tool_result.get("bookingDetails", {})
        booking_id = details.get("uid", "N/A")
        booking_title = details.get("title", "N/A")
        booking_start = details.get("start", "N/A")
        return [TextContent(text=f"Successfully created booking: {booking_title} (ID: {booking_id}) starting at {booking_start}.")]
    else:
        error_step = tool_result.get("bookingDetails", {}).get("error_step", "Unknown step")
        return [TextContent(text=f"Booking failed. Reason: {tool_result['message']} (Error at step: {error_step})")]