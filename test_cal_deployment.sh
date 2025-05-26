#!/bin/bash

# Test script for Cal.com MCP Server deployment
# Usage: ./test_cal_deployment.sh <service-url>
# Example: ./test_cal_deployment.sh https://cal-com-mcp-xxxx.onrender.com

if [ $# -eq 0 ]; then
    echo "Usage: $0 <service-url>"
    echo "Example: $0 https://cal-com-mcp-xxxx.onrender.com"
    exit 1
fi

SERVICE_URL="${1%/}"  # Remove trailing slash if present

echo "🧪 Testing Cal.com MCP Server at: $SERVICE_URL"
echo "============================================================"

# Test 1: Root endpoint
echo -e "\n1️⃣ Testing root endpoint (/)..."
echo "Command: curl -s $SERVICE_URL/"
curl -s "$SERVICE_URL/" | python3 -m json.tool || echo "Failed to parse JSON"

# Test 2: Health endpoint
echo -e "\n2️⃣ Testing health endpoint (/health)..."
echo "Command: curl -s $SERVICE_URL/health"
curl -s "$SERVICE_URL/health" | python3 -m json.tool || echo "Failed to parse JSON"

# Test 3: Check HTTP status codes
echo -e "\n3️⃣ Checking HTTP status codes..."
echo "Root endpoint status:"
curl -s -o /dev/null -w "   HTTP Status: %{http_code}\n" "$SERVICE_URL/"

echo "Health endpoint status:"
curl -s -o /dev/null -w "   HTTP Status: %{http_code}\n" "$SERVICE_URL/health"

echo "MCP endpoint status (GET - should be 405 or similar):"
curl -s -o /dev/null -w "   HTTP Status: %{http_code}\n" "$SERVICE_URL/mcp"

# Test 4: Response headers
echo -e "\n4️⃣ Checking response headers..."
echo "Headers from root endpoint:"
curl -s -I "$SERVICE_URL/" | grep -E "(HTTP|content-type|server)" || echo "No headers found"

# Test 5: Quick availability check
echo -e "\n5️⃣ Service availability summary:"
if curl -s -f "$SERVICE_URL/health" > /dev/null; then
    echo "   ✅ Service is UP and responding!"
else
    echo "   ❌ Service might be DOWN or not responding properly"
fi

echo -e "\n============================================================"
echo "🏁 Testing complete!"
echo -e "\nImportant URLs for configuration:"
echo "- Health check: $SERVICE_URL/health"
echo "- MCP endpoint: $SERVICE_URL/mcp"
echo -e "\nUse this MCP URL in bridge_server/.env:"
echo "CAL_COM_MCP_SERVER_URL=$SERVICE_URL/mcp"