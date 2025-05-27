#!/bin/bash
# Test script that warms up all services first

echo "🔥 Warming up MCP services..."
echo "This may take 30-60 seconds for cold starts..."

# Warm up Cal.com MCP
echo -n "Warming up Cal.com MCP... "
curl -s https://cal-mcp.onrender.com/health > /dev/null &
CAL_PID=$!

# Warm up Outlook MCP
echo -n "Warming up Outlook MCP... "
curl -s https://outlook-mcp-server.onrender.com/health > /dev/null &
OUTLOOK_PID=$!

# Wait for both to complete
wait $CAL_PID
echo "✅"
wait $OUTLOOK_PID
echo "✅"

echo "Waiting 5 seconds for services to stabilize..."
sleep 5

echo ""
echo "🧪 Running system tests..."
python3 quick_system_test.py https://elevenlabs-bridge-server.onrender.com