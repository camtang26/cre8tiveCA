# cre8tiveCA

MCP (Model Context Protocol) servers and a bridge server for integrating ElevenLabs agent with Cal.com and Microsoft Outlook.

## Project Structure

-   `bridge_server/`: FastAPI server that acts as a webhook receiver from ElevenLabs and an MCP client to the other servers.
-   `cal_com_mcp_server/`: FastMCP server providing tools to interact with the Cal.com API.
-   `outlook_mcp_server/`: FastMCP server providing tools to interact with Microsoft Graph API for Outlook.
-   `memory-bank/`: Contains markdown files for project context, decisions, and progress tracking.

## Setup and Deployment

Details for local setup and deployment to Render.com will be added here.