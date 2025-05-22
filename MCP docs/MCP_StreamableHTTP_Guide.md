# Guide: Setting Up MCP Streamable-HTTP with Python SDK v1.9.0

This document details the process, challenges, and solutions encountered while setting up and testing an MCP server and client using the `streamable-http` transport with the `mcp` Python SDK version 1.9.0. This was specifically applied to the `jsonplaceholder_wrapper_server.py` and its corresponding client `test_jsonplaceholder_client.py`.

## 1. Objective

The primary goal was to reliably run `jsonplaceholder_wrapper_server.py` using the `streamable-http` transport and ensure its `fetch_todos` tool could be successfully called and tested by `test_jsonplaceholder_client.py`, including handling of successful responses and server-indicated errors.

## 2. Background & Initial Challenges

*   Previous attempts to use HTTP-based transports with `mcp` SDK v1.7.1 for other example servers proved difficult, with unclear mechanisms for configuring host/port for HTTP_RPC.
*   The `mcp` Python SDK was upgraded to `mcp[cli]==1.9.0` to leverage its "Streamable HTTP" transport, which promised a more straightforward way to run MCP servers over HTTP.

## 3. Environment & Dependencies

A correctly configured Python virtual environment is crucial.

*   **Virtual Environment:** Ensure your project's virtual environment (e.g., `.venv`) is activated.
*   **Python:** A modern version of Python 3.
*   **Key Libraries:**
    *   `mcp[cli]==1.9.0`
    *   `uvicorn` (often pulled in by `mcp[cli]`, but good to ensure it's present for ASGI servers)
    *   `httpx` (for the client and potentially by the server components)
    *   `click<8.2.0` (This was a fix for the `mcp` CLI tool itself, not directly for server/client execution, but important for overall SDK stability at the time of writing).

**Command to install/ensure dependencies (in activated venv):**
```bash
uv pip install "mcp[cli]==1.9.0" uvicorn httpx "click<8.2.0"
```

## 4. Server-Side Setup (`jsonplaceholder_wrapper_server.py`)

The `jsonplaceholder_wrapper_server.py` was configured to serve its `fetch_todos` tool over `streamable-http`.

### 4.1. Server Startup Method

After some iteration and resolving virtual environment issues (see below), the reliable method to start the server is using `mcp.run()`:

```python
# mcp_servers/jsonplaceholder_wrapper_server.py (relevant part)
from mcp import FastMCP, tool
import httpx # For the tool's implementation
# ... (Tool definition for fetch_todos) ...

mcp = FastMCP(
    name="JsonPlaceholderWrapperServer",
    description="A server that wraps the JSONPlaceholder API for todos.",
    host="localhost", # Default, can be configured
    port=8003,        # Example port
)

@mcp.tool()
async def fetch_todos(limit: int = 10) -> list[dict]:
    # ... (tool implementation as before) ...
    if not (1 <= limit <= 200):
        # This error message is important for client-side error handling validation
        raise ValueError("Limit must be between 1 and 200.")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://jsonplaceholder.typicode.com/todos?_limit={limit}")
        response.raise_for_status()
        return response.json()

if __name__ == "__main__":
    print(
        f"Attempting to start JsonPlaceholderWrapperServer (streamable-http) "
        f"on {mcp.settings.host}:{mcp.settings.port} via mcp.run(transport='streamable-http')..."
    )
    try:
        # This is the key line for starting with streamable-http
        mcp.run(transport="streamable-http")
    except Exception as e:
        print(f"Failed to start server: {e}")
        # Fallback or further error handling can be added here
```

### 4.2. Initial Server Startup Challenges & Resolution

*   **"Unknown transport: streamable-http" error with `mcp.run()`:** This occurred intermittently and was traced back to issues with the Python virtual environment.
*   **Client-side `RuntimeError: Task group is not initialized`:** This happened when attempting to run the server programmatically with `uvicorn.run(mcp.streamable_http_app())` before venv issues were fully resolved.
*   **Resolution:**
    1.  Ensured the project's virtual environment (`OpenManus\.venv`) was correctly activated.
    2.  Checked for and resolved any filesystem permission issues (e.g., a venv folder being read-only).
    3.  Reinstalled dependencies (`mcp[cli]==1.9.0`, `uvicorn`, `httpx`) into the correct, active venv.
    After these steps, `mcp.run(transport="streamable-http")` became reliable.

## 5. Client-Side Implementation (`test_jsonplaceholder_client.py`)

The client script was developed to connect to the server, list its tools, call `fetch_todos` under various conditions, and validate the responses.

### 5.1. Establishing a Connection

*   **Initial Problem:** `TypeError: ClientSession.__init__() got an unexpected keyword argument 'server_url'`.
*   **Discovery:** `mcp.client.session.ClientSession` requires `read_stream` and `write_stream` arguments, not a direct URL for `streamable-http`. The `mcp.client.streamable_http.streamablehttp_client` asynchronous context manager provides these.
*   **Correct Connection Pattern:**

```python
# mcp_clients/test_jsonplaceholder_client.py (relevant part)
import asyncio
import json
import logging
from mcp import types
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

SERVER_URL = "http://localhost:8003/mcp" # Matches server's host, port, and /mcp path

async def main():
    # ... (logging setup) ...
    try:
        async with streamablehttp_client(url=SERVER_URL) as (
            read_stream,
            write_stream,
            _, # get_session_id_callback - not used here
        ):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                # ... proceed with session operations ...
    # ... (error handling) ...
```

### 5.2. Listing Tools

*   **Initial Problem:** `AttributeError: 'tuple' object has no attribute 'name'` when iterating over the result of `session.list_tools()`.
*   **Discovery:** `await session.list_tools()` returns an `mcp.types.ListToolsResult` object. The actual list of tool definitions is in its `.tools` attribute.
*   **Correct Pattern:**

```python
list_tools_response = await session.list_tools()
actual_tools_list = list_tools_response.tools # Access .tools attribute
tool_names = [tool.name for tool in actual_tools_list]
assert "fetch_todos" in tool_names
```

### 5.3. Calling Tools and Parsing Successful Results

*   **Initial Problem:** `TypeError: 'CallToolResult' object is not subscriptable` when trying to access parts of the `session.call_tool()` result directly.
*   **Discovery 1 (Result Object):** `await session.call_tool()` returns an `mcp.types.CallToolResult` object. The primary data is within its `.content` attribute, which is a list.
*   **Discovery 2 (Content Item Type - CRUCIAL):** When a tool returns text-based data (like our JSON strings), the items within `CallToolResult.content` are instances of `mcp.types.TextContent`. These objects have a `.text` attribute containing the actual string data. This was a key finding, as initial assumptions based on some type hints might lead one to expect `mcp.types.TextResourceContents`.
*   **Correct Parsing Pattern:**

```python
call_default_result = await session.call_tool("fetch_todos", {})
todos_default = []
if call_default_result.content:
    for item in call_default_result.content:
        if isinstance(item, types.TextContent): # Check for TextContent
            todo_data = json.loads(item.text) # Parse the .text attribute
            todos_default.append(todo_data)
        else:
            logger.warning(f"Item is not TextContent: {repr(item)}")

assert len(todos_default) == 10 # Or other expected length
# ... further assertions on todo_data ...
```

### 5.4. Handling Server-Indicated Errors

When a tool execution on the server side raises an exception (e.g., `ValueError` in `fetch_todos` for an invalid limit), the `mcp` server communicates this back to the client.

*   **Initial Misconception:** It was initially assumed that `await session.call_tool()` would *raise an exception* on the client side if the server indicated an error. This is **incorrect** for errors explicitly handled and returned by the server as part of the MCP tool call response.
*   **Discovery (Server Error Reporting):** When the server's tool raises an exception that the server framework catches and reports as a tool execution error, the `JSONRPCResponse` from the server will have `isError: true` and its `result.content` will contain the error message (typically as a `TextContent` item). The client's `session.call_tool()` **does not raise an exception** in this scenario. Instead, it returns a `CallToolResult` object where:
    *   `result.isError` will be `True`.
    *   `result.content` will be a list containing one or more `TextContent` items, with the `.text` attribute holding the error message string from the server.
*   **Correct Error Handling Pattern:**

```python
invalid_limit = 0
call_invalid_result = await session.call_tool(
    "fetch_todos", {"limit": invalid_limit}
)

assert call_invalid_result.isError is True, \
    "Expected isError to be True for invalid limit call"
assert call_invalid_result.content and len(call_invalid_result.content) > 0, \
    "Expected error content for invalid limit call"

error_content_item = call_invalid_result.content[0]
assert isinstance(error_content_item, types.TextContent), \
    "Error content should be TextContent"

expected_server_error_message = "Limit must be between 1 and 200" # Matches ValueError in server
actual_error_message = error_content_item.text
assert expected_server_error_message in actual_error_message, \
    f"Expected error message '{expected_server_error_message}' not found in '{actual_error_message}'"
logger.info(f"Successfully received expected error content for invalid limit: {actual_error_message}")
```

## 6. Logging for Debugging

Extensive logging was invaluable. Setting the log levels for `mcp` and `httpx` (the underlying HTTP client for `streamablehttp_client`) to `DEBUG` provided deep insight into the request/response cycle and internal SDK behavior.

```python
# In client script
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.getLogger("mcp").setLevel(logging.DEBUG)
logging.getLogger("httpx").setLevel(logging.DEBUG)
```

## 7. Conclusion

By systematically addressing connection methods, result parsing, and error handling, and by understanding the specific types and behaviors of the `mcp` Python SDK v1.9.0 (particularly `TextContent` vs. `TextResourceContents` and how server errors are propagated), it's possible to reliably use the `streamable-http` transport. Careful attention to the virtual environment and dependencies is also paramount. This detailed debugging journey should serve as a useful reference for future MCP development with this SDK version.
