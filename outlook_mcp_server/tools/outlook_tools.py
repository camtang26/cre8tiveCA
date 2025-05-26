from mcp.server.fastmcp import FastMCP, Context as MCPContext

try:
    from ..schemas.outlook_schemas import SendOutlookEmailInput, SendOutlookEmailOutput
    from ..core.graph_api_utils import send_email_via_graph_api
except ImportError:
    # Fallback for when running as main module
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from schemas.outlook_schemas import SendOutlookEmailInput, SendOutlookEmailOutput
    from core.graph_api_utils import send_email_via_graph_api

outlook_mcp_instance = FastMCP(
    name="outlook_tools_server",
    description="Tools for Microsoft Outlook integration via Graph API",
    host="localhost",
    port=8002
)

@outlook_mcp_instance.tool(
    name="send_outlook_email_mcp",
    description="Sends an email using Microsoft Graph API."
    # Input and output schemas are inferred from type hints
)
async def send_outlook_email_mcp_tool(args: SendOutlookEmailInput, ctx: MCPContext) -> SendOutlookEmailOutput:
    """
    MCP Tool to send an email via Microsoft Graph API.
    """
    await ctx.info(f"Attempting to send email to: {args.recipientEmail} with subject: {args.emailSubject}")

    result = await send_email_via_graph_api(
        recipient_email=str(args.recipientEmail), # Ensure EmailStr is string
        subject=args.emailSubject,
        body_html=args.emailBodyHtml,
        save_to_sent_items=args.saveToSentItems
    )

    if result.get("success"):
        await ctx.info(f"Email send request accepted for {args.recipientEmail}")
        return SendOutlookEmailOutput(
            success=True,
            message=result.get("message", "Email send request accepted.")
        )
    else:
        error_msg = result.get("error", "Unknown error sending email.")
        error_details = result.get("details", "No additional details.")
        await ctx.error(f"Failed to send email to {args.recipientEmail}: {error_msg} - Details: {error_details}") # ctx.error is also async
        return SendOutlookEmailOutput(
            success=False,
            message=error_msg,
            details=str(error_details) # Ensure details are string
        )