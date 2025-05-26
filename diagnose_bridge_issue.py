#!/usr/bin/env python3
"""
Diagnose Bridge Server Connection Issues
"""

import requests
import json
from datetime import datetime

def diagnose_issue():
    """Diagnose why the bridge server is returning 500 errors"""
    
    print("🔍 Diagnosing Bridge Server Issues")
    print("=" * 60)
    
    # Test 1: Check if bridge server is truly connected to MCP servers
    print("\n1️⃣ Testing Bridge Server Environment...")
    bridge_url = "https://elevenlabs-bridge-server.onrender.com"
    
    # Simple payload that should work if connection is good
    minimal_cal_payload = {
        "start_time_utc": "2025-12-20T15:00:00Z",
        "attendee_timezone": "UTC",
        "attendee_name": "Diagnostic Test",
        "attendee_email": "test@diagnostic.com",
        "event_type_id": 1837761
    }
    
    print("\n📋 Sending minimal Cal.com payload:")
    print(json.dumps(minimal_cal_payload, indent=2))
    
    try:
        response = requests.post(
            f"{bridge_url}/webhook/cal/schedule_consultation",
            json=minimal_cal_payload,
            timeout=60  # Longer timeout for cold starts
        )
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
        
        # Check if it's a connection issue
        if "TaskGroup" in response.text:
            print("\n⚠️  DIAGNOSIS: Bridge server is having async/connection issues with MCP servers")
            print("Possible causes:")
            print("1. MCP servers are in cold start state")
            print("2. Network connectivity between services")
            print("3. MCP client connection timeout")
            
    except Exception as e:
        print(f"\n❌ Request failed: {e}")
    
    # Test 2: Check MCP servers directly
    print("\n\n2️⃣ Checking MCP Servers Directly...")
    
    mcp_servers = [
        ("Cal.com MCP", "https://cal-mcp.onrender.com/health"),
        ("Outlook MCP", "https://outlook-mcp-server.onrender.com/health")
    ]
    
    for name, url in mcp_servers:
        try:
            response = requests.get(url, timeout=10)
            print(f"\n{name}:")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.json()}")
        except Exception as e:
            print(f"\n{name}: ❌ Error - {e}")
    
    # Recommendations
    print("\n\n💡 RECOMMENDATIONS:")
    print("1. Check bridge server logs in Render dashboard for detailed error messages")
    print("2. Ensure MCP server URLs in environment variables are correct:")
    print("   - CAL_COM_MCP_SERVER_URL=https://cal-mcp.onrender.com/mcp")
    print("   - OUTLOOK_MCP_SERVER_URL=https://outlook-mcp-server.onrender.com/mcp")
    print("3. Try redeploying the bridge server to refresh connections")
    print("4. Consider adding longer timeouts for MCP client connections")
    
    print("\n📝 To view bridge server logs:")
    print("1. Go to Render Dashboard")
    print("2. Click on 'elevenlabs-bridge-server'")
    print("3. Navigate to 'Logs' tab")
    print("4. Look for connection errors or timeout messages")

if __name__ == "__main__":
    diagnose_issue()