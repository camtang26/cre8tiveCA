#!/usr/bin/env python3
"""
Test script for Cal.com MCP Server deployment on Render.com
Usage: python test_cal_deployment.py <service-url>
Example: python test_cal_deployment.py https://cal-com-mcp-xxxx.onrender.com
"""

import sys
import asyncio
import httpx
import json
from datetime import datetime

async def test_cal_deployment(base_url: str):
    """Test various endpoints of the deployed Cal.com MCP server"""
    
    print(f"🧪 Testing Cal.com MCP Server at: {base_url}")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Test 1: Root endpoint
        print("\n1️⃣ Testing root endpoint (/)...")
        try:
            response = await client.get(f"{base_url}/")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "Cal.com MCP Server" in data["message"]:
                    print("   ✅ Root endpoint working correctly!")
                else:
                    print("   ⚠️  Unexpected response format")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 2: Health endpoint
        print("\n2️⃣ Testing health endpoint (/health)...")
        try:
            response = await client.get(f"{base_url}/health")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    print("   ✅ Health endpoint working correctly!")
                else:
                    print("   ⚠️  Service might not be fully healthy")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 3: MCP endpoint (basic check)
        print("\n3️⃣ Testing MCP endpoint (/mcp) availability...")
        try:
            # MCP endpoint typically requires specific headers and protocol
            response = await client.get(f"{base_url}/mcp")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 405:  # Method Not Allowed is expected for GET
                print("   ✅ MCP endpoint exists (requires POST with proper protocol)")
            elif response.status_code == 200:
                print(f"   Response: {response.text[:200]}...")
                print("   ✅ MCP endpoint accessible")
            else:
                print(f"   ⚠️  Unexpected status code: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 4: Check if running in fallback mode
        print("\n4️⃣ Checking deployment mode...")
        try:
            response = await client.get(f"{base_url}/")
            data = response.json()
            mode = data.get("mode", "unknown")
            
            if mode == "basic":
                print("   ℹ️  Server running in basic mode (MCP fully functional)")
                print("   ✅ This is the expected mode for successful deployment!")
            elif mode == "fallback":
                print("   ⚠️  Server running in fallback mode (MCP imports failed)")
                print("   ⚠️  Check deployment logs for MCP installation issues")
            else:
                print(f"   ℹ️  Server mode: {mode}")
        except Exception as e:
            print(f"   ❌ Error checking mode: {e}")
        
        # Test 5: Response time check
        print("\n5️⃣ Testing response time...")
        try:
            start_time = datetime.now()
            response = await client.get(f"{base_url}/health")
            end_time = datetime.now()
            
            response_time = (end_time - start_time).total_seconds() * 1000
            print(f"   Response time: {response_time:.2f}ms")
            
            if response_time < 500:
                print("   ✅ Excellent response time!")
            elif response_time < 1000:
                print("   ✅ Good response time")
            else:
                print("   ⚠️  Slow response time (might be cold start)")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Testing complete!")
    print("\nNext steps:")
    print("1. If all tests passed, the Cal.com MCP server is ready for use")
    print("2. Save the service URL for bridge_server configuration")
    print("3. The MCP endpoint URL will be: {base_url}/mcp")

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_cal_deployment.py <service-url>")
        print("Example: python test_cal_deployment.py https://cal-com-mcp-xxxx.onrender.com")
        sys.exit(1)
    
    service_url = sys.argv[1].rstrip('/')
    
    if not service_url.startswith(('http://', 'https://')):
        print("Error: URL must start with http:// or https://")
        sys.exit(1)
    
    asyncio.run(test_cal_deployment(service_url))

if __name__ == "__main__":
    main()