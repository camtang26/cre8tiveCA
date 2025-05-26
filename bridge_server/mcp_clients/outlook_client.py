import asyncio
import json
import logging
from typing import Dict, Any, Optional

from mcp import types
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from bridge_server.core.config import OUTLOOK_MCP_SERVER_URL
# Assuming similar Pydantic models as defined in outlook_mcp_server.schemas.outlook_schemas
from pydantic import BaseModel, EmailStr, Field # Assuming similar structure

logger = logging.getLogger(__name__)

# --- Placeholder Pydantic Models (mirroring Outlook MCP server's schemas) ---
# These should ideally be shared or imported if possible, or defined to be compatible.

class SendOutlookEmailClientInput(BaseModel):
    recipient_email: EmailStr = Field(..., alias="recipientEmail")
    email_subject: str = Field(..., alias="emailSubject")
    email_body_html: str = Field(..., alias="emailBodyHtml")
    save_to_sent_items: Optional[bool] = Field(True, alias="saveToSentItems")

class SendOutlookEmailClientOutput(BaseModel):
    success: bool
    message: str
    details: Optional[str] = None
# --- End Placeholder Pydantic Models ---


async def call_outlook_send_email_tool(
    payload: SendOutlookEmailClientInput
) -> SendOutlookEmailClientOutput:
    """
    Calls the 'send_outlook_email_mcp_tool' on the Outlook MCP server.
    """
    if not OUTLOOK_MCP_SERVER_URL:
        logger.error("OUTLOOK_MCP_SERVER_URL is not configured.")
        return SendOutlookEmailClientOutput(
            success=False,
            message="Bridge server configuration error: Outlook MCP server URL not set."
        )

    tool_name = "send_outlook_email_mcp" # Corrected to match the server's registered tool name
    # Use model_dump with by_alias=True if your Pydantic models use aliases
    # that match the MCP tool's expected argument names.
    tool_args_dict = payload.model_dump(by_alias=True, exclude_none=True)
    # Wrap the payload in a dictionary with the key "args", as the server tool expects this
    # when its Pydantic model argument is named 'args'.
    tool_args_wrapped = {"args": tool_args_dict}

    logger.info(f"Calling Outlook MCP tool '{tool_name}' at {OUTLOOK_MCP_SERVER_URL} with wrapped args: {tool_args_wrapped}")

    try:
        async with streamablehttp_client(url=OUTLOOK_MCP_SERVER_URL) as (
            read_stream,
            write_stream,
            _,
        ):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                logger.debug("MCP Client session initialized with Outlook MCP Server.")

                call_result: types.CallToolResult = await session.call_tool(
                    name=tool_name,
                    arguments=tool_args_wrapped # Send the wrapped arguments
                )
                logger.debug(f"Raw CallToolResult from Outlook MCP: {call_result}")

                if call_result.isError:
                    error_message = "Unknown error from Outlook MCP tool."
                    if call_result.content:
                        error_item = call_result.content[0]
                        if isinstance(error_item, types.TextContent):
                            # Attempt to parse as JSON if it's a structured error
                            try:
                                error_data = json.loads(error_item.text)
                                error_message = error_data.get("message", error_item.text)
                            except json.JSONDecodeError:
                                error_message = error_item.text
                    logger.error(f"Error from Outlook MCP tool '{tool_name}': {error_message}")
                    return SendOutlookEmailClientOutput(success=False, message=error_message)

                if not call_result.content:
                    logger.error(f"No content received from Outlook MCP tool '{tool_name}'.")
                    return SendOutlookEmailClientOutput(success=False, message="No content received from Outlook MCP tool.")

                response_item = call_result.content[0]
                if isinstance(response_item, types.TextContent):
                    response_data = json.loads(response_item.text)
                    logger.info(f"Successfully called Outlook MCP tool '{tool_name}'. Response: {response_data}")
                    return SendOutlookEmailClientOutput(**response_data)
                else:
                    logger.error(f"Unexpected content type from Outlook MCP tool: {type(response_item)}")
                    return SendOutlookEmailClientOutput(success=False, message="Unexpected response format from Outlook MCP tool.")

    except json.JSONDecodeError as e:
        logger.exception(f"JSON decoding error for Outlook MCP tool response: {e}")
        return SendOutlookEmailClientOutput(success=False, message=f"Invalid JSON response from Outlook MCP tool: {e}")
    except ConnectionRefusedError:
        logger.error(f"Connection refused by Outlook MCP server at {OUTLOOK_MCP_SERVER_URL}.")
        return SendOutlookEmailClientOutput(success=False, message="Connection refused by Outlook MCP server.")
    except Exception as e:
        logger.exception(f"An unexpected error occurred while calling Outlook MCP tool '{tool_name}': {e}")
        return SendOutlookEmailClientOutput(
            success=False,
            message=f"An unexpected error occurred: {str(e)}"
        )

if __name__ == '__main__':
    async def test_run():
        logging.basicConfig(level=logging.DEBUG)
        # Ensure Outlook MCP server is running on localhost:8002 (or configured port)
        # and has a tool named 'send_outlook_email_mcp_tool'
        sample_payload = SendOutlookEmailClientInput(
            recipientEmail="test.bridge@example.com", # Use a test recipient
            emailSubject="Test Email via Bridge Client",
            emailBodyHtml="<p>This is a <b>test email</b> sent via the Bridge Server's Outlook client utility.</p>",
            saveToSentItems=True
        )
        result = await call_outlook_send_email_tool(sample_payload)
        print("\n--- Test Run Result (Outlook Client) ---")
        print(f"Success: {result.success}")
        print(f"Message: {result.message}")
        if result.details:
            print(f"Details: {result.details}")

    asyncio.run(test_run())