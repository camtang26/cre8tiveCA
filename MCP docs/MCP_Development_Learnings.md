# MCP Development: Best Practices & Lessons Learned (Python SDK)

This document captures key learnings, best practices, and troubleshooting insights gained while developing Model Context Protocol (MCP) servers and clients using the `mcp` Python SDK within the OpenManus project. It complements specific guides like the `MCP_StreamableHTTP_Guide.md`.

## 1. Introduction

The Model Context Protocol is a powerful standard, but working with early or rapidly evolving SDKs like `mcp` for Python can present unique challenges. This guide aims to consolidate practical knowledge to aid future AI models, developers, and new project contributors in understanding and effectively utilizing the SDK.

## 2. SDK Versioning & Evolution

*   **Awareness is Key:** We transitioned from `mcp` SDK v1.7.1 to v1.9.0. This brought significant changes, such as the `streamable-http` transport and modifications to client connection patterns.
*   **Expect Change:** SDK features, function signatures, and internal behaviors can evolve between versions.
*   **Recommendation:**
    1.  Always verify the `mcp` SDK version currently in use in the project's virtual environment (`uv pip show mcp`).
    2.  Prioritize using the [`context7`](#context7-mcp) MCP ([`resolve-library-id`](#context7-mcp) -> [`get-library-docs`](#context7-mcp)) to fetch the most up-to-date documentation for the `mcp` library itself if available.
    3.  If official documentation is sparse for a specific version or feature, be prepared to consult the SDK's source code (see Debugging section).

## 3. Virtual Environment Management

*   **Absolutely Critical:** The consistent use of a dedicated Python virtual environment (e.g., `.venv` created with `python -m venv .venv` or `uv venv`) is non-negotiable. Activate it before any development or execution (`source .venv/bin/activate` or `.venv\Scripts\activate`).
*   **Common Pitfalls & Solutions:**
    *   **Incorrect Activation:** Leads to using global Python/packages, causing "module not found" or version mismatch errors. *Solution:* Always verify venv activation in the terminal prompt.
    *   **Read-Only Venv Folder:** Can prevent dependency updates or cause strange errors. *Solution:* Ensure the venv directory has correct write permissions.
    *   **Global Installs:** `pip install` (or `uv pip install`) without an active venv installs packages globally, which is undesirable. *Solution:* Always activate the venv first.
    *   **IDE Venv Misconfiguration:** Ensure your IDE (e.g., VS Code) is configured to use the project's virtual environment interpreter.

## 4. Dependency Management

*   **Pinning Versions:** For stability, critical dependencies, especially those interacting with evolving libraries like `mcp`, should be pinned.
    *   Example: `click<8.2.0` was necessary for the `mcp` CLI (versions 1.7.1 through 1.9.0) to function correctly due to a `TypeError` in later `click` versions.
*   **Core MCP Dependencies (Python):**
    *   `mcp` (or `mcp[cli]` for the command-line interface).
    *   `uvicorn`: For running ASGI applications like MCP servers using `sse` or `streamable_http_app()`.
    *   `httpx`: Used by `mcp` clients for HTTP-based transports and often useful within tools that make HTTP requests.
*   **Installation:** Use `uv pip install -r requirements.txt` or install individually.
*   **Tracking:** Regularly update `requirements.txt` with `uv pip freeze > requirements.txt` after confirming a stable set of dependencies.

## 5. MCP Server Development (Python SDK)

### 5.1. Transports & Startup

The `mcp` Python SDK supports multiple transports for servers:

*   **`stdio`:**
    *   **Use Case:** Simple, local, single-process servers. Good for basic examples or tightly coupled tools.
    *   **Startup:** Typically `mcp.run()` (default transport if none specified and not an ASGI app).
    *   *Example:* `string_tools_server.py` (from initial project examples).
*   **`sse` (Server-Sent Events):**
    *   **Use Case:** HTTP-based, allows for streaming events from server to client.
    *   **Startup:**
        *   Programmatic with Uvicorn: `uvicorn.run(mcp.sse_app(), host="...", port=...)`.
        *   Via `mcp` CLI (if supported for SSE in that version).
    *   *Example:* `string_tools_server.py` was successfully run this way.
*   **`streamable-http` (SDK v1.9.0+):**
    *   **Use Case:** A more robust HTTP-based transport, intended to supersede older/less clear HTTP RPC mechanisms.
    *   **Preferred Startup:** `mcp.run(transport="streamable-http")`. This handles setting up the ASGI application with Uvicorn internally.
    *   *Example:* `jsonplaceholder_wrapper_server.py` (as detailed in `MCP_StreamableHTTP_Guide.md`).
    *   The `mcp.streamable_http_app()` can also be used to get the ASGI app directly for more custom Uvicorn setups if needed.

### 5.2. Tool Definition

*   Use the `@mcp.tool()` decorator on asynchronous functions.
*   Type hints for arguments and return types are used by the SDK to generate the `inputSchema` and inform clients.
*   Pydantic models can be used for complex input/output schemas.

### 5.3. Error Handling in Tools

*   **Standard Exceptions:** Raise standard Python exceptions (e.g., `ValueError`, `TypeError`, `httpx.HTTPStatusError`) within your tool's logic for expected error conditions.
*   **Server Response:** For transports like `streamable-http`, the `mcp` server framework typically catches these exceptions and translates them into a JSONRPC response where `isError` is `true`, and the `content` contains the exception message. The client does *not* see the Python exception directly but rather this structured error response.

## 6. MCP Client Development (Python SDK)

### 6.1. Transport-Specific Client Helpers

*   **Crucial Distinction:** Each server transport requires a corresponding client helper from the `mcp.client` module to establish the connection and provide the necessary `read_stream` and `write_stream` objects to `ClientSession`.
    *   `stdio`: `from mcp.client.stdio import stdio_client`
    *   `sse`: `from mcp.client.sse import sse_client`
    *   `streamable-http`: `from mcp.client.streamable_http import streamablehttp_client`
*   **Usage:** These are typically asynchronous context managers.

    ```python
    # Example for streamable-http
    from mcp.client.streamable_http import streamablehttp_client
    async with streamablehttp_client(url=SERVER_URL) as (rs, ws, _):
        async with ClientSession(rs, ws) as session:
            pass # Actual client logic here
    ```

### 6.2. `ClientSession` Lifecycle & Operations

1.  **Initialization:** After creating a `ClientSession` instance with the streams, `await session.initialize()` **must** be called.
2.  **Listing Tools:** `list_tools_response = await session.list_tools()`.
    *   This returns an `mcp.types.ListToolsResult` object.
    *   The actual list of `mcp.types.Tool` objects is in `list_tools_response.tools`.
3.  **Calling Tools:** `call_result = await session.call_tool(name="tool_name", arguments={"param": "value"})`.
    *   Returns an `mcp.types.CallToolResult` object.
    *   **Successful Calls:**
        *   `call_result.isError` will be `False`.
        *   `call_result.content` will be a list. For text-based tool outputs, each item in this list is typically an `mcp.types.TextContent` instance.
        *   The actual string data (often JSON) is in `item.text` for each `TextContent` item. This needs to be parsed (e.g., `json.loads(item.text)`).
    *   **Server-Indicated Errors (e.g., invalid arguments, tool execution failure):**
        *   `call_result.isError` will be `True`.
        *   `call_result.content` will contain `TextContent` item(s) where `item.text` is the error message string from the server.
        *   **Important:** `session.call_tool()` itself **does not raise a Python exception** when `isError` is true in the server's response. The client code must explicitly check `call_result.isError`.

### 6.3. Understanding `mcp.types`

*   The `mcp.types` module contains Pydantic models for all MCP message structures.
*   Key models for client-side parsing: `ListToolsResult`, `Tool`, `CallToolResult`, `TextContent`, `BlobResourceContents`.
*   **`TextContent` vs. `TextResourceContents`:** In practice with `CallToolResult.content` for `streamable-http` (SDK v1.9.0), items representing text output from tools were found to be `TextContent` instances, even if some higher-level type hints might suggest `TextResourceContents`. Always verify with `isinstance()` and `type()` during debugging. `TextContent` has the crucial `.text` attribute.

## 7. Debugging Techniques

*   **Enable `DEBUG` Logging:** This is often the most effective first step.
    ```python
    import logging
    logging.basicConfig(level=logging.INFO) # Keep general default
    logger = logging.getLogger(__name__) # Your script's logger
    logger.setLevel(logging.DEBUG)
    logging.getLogger("mcp").setLevel(logging.DEBUG)
    logging.getLogger("httpx").setLevel(logging.DEBUG) # For HTTP transport issues
    ```
*   **Read the SDK Source Code:** When behavior is undocumented or unclear, diving into the `mcp` Python SDK's source files (e.g., in your venv's `site-packages/mcp/`) is invaluable. Key files:
    *   `types.py`: For understanding data structures.
    *   `client/session.py`: For `ClientSession` logic.
    *   `client/<transport_name>.py`: For transport-specific client helpers.
    *   `server.py` / `transports/<transport_name>.py`: For server-side logic.
*   **Incremental Testing:**
    1.  Ensure server starts without errors.
    2.  Test basic client connection and `session.initialize()`.
    3.  Test `session.list_tools()`.
    4.  Test `session.call_tool()` with a simple, known-good case.
    5.  Test parsing of successful `call_tool()` results.
    6.  Test `session.call_tool()` with expected error conditions (e.g., invalid arguments) and verify client-side error handling logic.
*   **Simplify:** If facing a complex bug, create the smallest possible server and client scripts that reproduce the issue.

## 8. External (Non-Python) MCPs

*   The OpenManus project might integrate with MCPs written in other languages (e.g., Node.js for Bright Data).
*   These are typically configured in Roo Code's global `mcp_settings.json` file.
*   Their startup, management, and specific client interaction details will depend on their own implementation and documentation.

By following these practices and leveraging the lessons learned, development with the `mcp` Python SDK can be made more efficient and predictable.
