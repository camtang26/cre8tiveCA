import asyncio
import json
import logging
from typing import Dict, Any, Optional

from mcp import types
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from bridge_server.core.config import CAL_COM_MCP_SERVER_URL
# We'll need to define the input/output Pydantic models that the Cal.com MCP tool expects/returns.
# For now, let's assume they are similar to what we might pass or get.
# These should ideally mirror or be compatible with cal_com_mcp_server.schemas.cal_com_schemas
from pydantic import BaseModel, EmailStr, Field # Assuming similar structure

logger = logging.getLogger(__name__)

# --- Placeholder Pydantic Models (mirroring Cal.com MCP server's schemas) ---
# These should ideally be shared or imported if possible, or defined to be compatible.
# This model should match the fields of cal_com_mcp_server.schemas.cal_com_schemas.CreateCalComBookingInput

class CreateCalComBookingClientInput(BaseModel):
    localDate: str = Field(..., description="Local date for the booking (YYYY-MM-DD)")
    localTime: str = Field(..., description="Local time for the booking (HH:MM, 24-hour format)")
    localTimeZone: str = Field(..., description="Local IANA timezone string (e.g., Australia/Sydney)")
    attendeeName: str = Field(..., description="Full name of the attendee")
    attendeeEmail: EmailStr = Field(..., description="Email address of the attendee")
    eventDurationMinutes: Optional[int] = Field(None, description="Duration of the event in minutes. Optional, as event type may have fixed duration.")
    eventTypeId: int = Field(..., description="The Cal.com Event Type ID.") # Made non-optional as it's crucial
    guests: Optional[list[EmailStr]] = Field(default_factory=list, description="List of guest email addresses.")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata for the booking.")
    language: Optional[str] = Field("en", description="Language for the booking notifications.")

class BookingOutputDetailsClient(BaseModel):
    uid: Optional[str] = None
    title: Optional[str] = None
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    timeZone: Optional[str] = None
    status: Optional[str] = None
    errorMessage: Optional[str] = None

class CreateCalComBookingClientOutput(BaseModel):
    success: bool
    message: str
    booking_details: Optional[BookingOutputDetailsClient] = None
    error_details: Optional[str] = None
# --- End Placeholder Pydantic Models ---


async def call_cal_com_create_booking_tool(
    payload: CreateCalComBookingClientInput
) -> CreateCalComBookingClientOutput:
    """
    Calls the 'create_cal_com_booking_mcp_tool' on the Cal.com MCP server.
    """
    if not CAL_COM_MCP_SERVER_URL:
        logger.error("CAL_COM_MCP_SERVER_URL is not configured.")
        return CreateCalComBookingClientOutput(
            success=False,
            message="Bridge server configuration error: Cal.com MCP server URL not set."
        )

    tool_name = "create_cal_com_booking_mcp" # Corrected to match server's registered tool name
    tool_payload_dict = payload.model_dump(exclude_none=True)
    # Wrap the payload in a dictionary with the key "args", as the server tool expects this
    # when its Pydantic model argument is named 'args'.
    tool_args_wrapped = {"args": tool_payload_dict}

    logger.info(f"Calling Cal.com MCP tool '{tool_name}' at {CAL_COM_MCP_SERVER_URL} with wrapped args: {tool_args_wrapped}")

    try:
        async with streamablehttp_client(url=CAL_COM_MCP_SERVER_URL) as (
            read_stream,
            write_stream,
            _,
        ):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                logger.debug("MCP Client session initialized with Cal.com MCP Server.")

                call_result: types.CallToolResult = await session.call_tool(
                    name=tool_name,
                    arguments=tool_args_wrapped # Send the wrapped arguments
                )
                logger.debug(f"Raw CallToolResult from Cal.com MCP: {call_result}")

                if call_result.isError:
                    error_message = "Unknown error from Cal.com MCP tool."
                    if call_result.content:
                        # Assuming error message is in the first TextContent item
                        error_item = call_result.content[0]
                        if isinstance(error_item, types.TextContent):
                            error_message = error_item.text
                    logger.error(f"Error from Cal.com MCP tool '{tool_name}': {error_message}")
                    return CreateCalComBookingClientOutput(success=False, message=error_message)

                if not call_result.content:
                    logger.error(f"No content received from Cal.com MCP tool '{tool_name}'.")
                    return CreateCalComBookingClientOutput(success=False, message="No content received from Cal.com MCP tool.")

                # Assuming the tool returns a single JSON string in TextContent
                response_item = call_result.content[0]
                if isinstance(response_item, types.TextContent):
                    response_data = json.loads(response_item.text)
                    logger.info(f"Successfully called Cal.com MCP tool '{tool_name}'. Response: {response_data}")
                    # Validate and parse with the Pydantic output model
                    return CreateCalComBookingClientOutput(**response_data)
                else:
                    logger.error(f"Unexpected content type from Cal.com MCP tool: {type(response_item)}")
                    return CreateCalComBookingClientOutput(success=False, message="Unexpected response format from Cal.com MCP tool.")

    except json.JSONDecodeError as e:
        logger.exception(f"JSON decoding error for Cal.com MCP tool response: {e}")
        return CreateCalComBookingClientOutput(success=False, message=f"Invalid JSON response from Cal.com MCP tool: {e}")
    except ConnectionRefusedError:
        logger.error(f"Connection refused by Cal.com MCP server at {CAL_COM_MCP_SERVER_URL}.")
        return CreateCalComBookingClientOutput(success=False, message="Connection refused by Cal.com MCP server.")
    except Exception as e:
        logger.exception(f"An unexpected error occurred while calling Cal.com MCP tool '{tool_name}': {e}")
        return CreateCalComBookingClientOutput(
            success=False,
            message=f"An unexpected error occurred: {str(e)}"
        )

if __name__ == '__main__':
    # Example usage (for testing this client function directly)
    async def test_run():
        logging.basicConfig(level=logging.DEBUG)
        # Ensure Cal.com MCP server is running on localhost:8001
        # and has a tool named 'create_cal_com_booking_mcp_tool'
        sample_payload = CreateCalComBookingClientInput(
            user_name="Test User Bridge",
            user_email="test.user.bridge@example.com",
            event_type_id=1837761, # Replace with a valid one if needed for testing
            date_time="2025-12-01T10:00:00Z", # Ensure this is a valid future time slot
            duration_minutes=30,
            time_zone="UTC",
            additional_notes="Test booking via bridge client."
        )
        result = await call_cal_com_create_booking_tool(sample_payload)
        print("\n--- Test Run Result ---")
        print(f"Success: {result.success}")
        print(f"Message: {result.message}")
        if result.booking_details:
            print(f"Booking Details: {result.booking_details.model_dump_json(indent=2)}")
        if result.error_details:
            print(f"Error Details: {result.error_details}")

    asyncio.run(test_run())