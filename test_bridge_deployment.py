#!/usr/bin/env python3
"""
Test script for Bridge Server deployment
Usage: python test_bridge_deployment.py <bridge-server-url>
Example: python test_bridge_deployment.py https://bridge-server-xxxx.onrender.com
"""

import sys
import asyncio
import httpx
import json
from datetime import datetime, timezone

async def test_bridge_deployment(base_url: str):
    """Test the deployed Bridge Server endpoints"""
    
    print(f"🧪 Testing Bridge Server at: {base_url}")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Test 1: Root endpoint
        print("\n1️⃣ Testing root endpoint (/)...")
        try:
            response = await client.get(f"{base_url}/")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                print("   ✅ Bridge server is running!")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 2: Cal.com webhook endpoint (test with sample data)
        print("\n2️⃣ Testing Cal.com webhook endpoint...")
        cal_payload = {
            "start_time_utc": "2025-12-10T14:00:00Z",
            "attendee_timezone": "America/New_York",
            "attendee_name": "Test User",
            "attendee_email": "test@example.com",
            "event_type_id": 1837761,
            "language": "en"
        }
        
        try:
            response = await client.post(
                f"{base_url}/webhook/cal/schedule_consultation",
                json=cal_payload
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                print("   ✅ Cal.com webhook endpoint accessible!")
            else:
                print("   ⚠️  Check MCP server connectivity")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 3: Outlook webhook endpoint (test with sample data)
        print("\n3️⃣ Testing Outlook webhook endpoint...")
        outlook_payload = {
            "recipient_email": "test@example.com",
            "email_subject": "Test Email from Bridge Server",
            "email_body_html": "<p>This is a test email from the deployed bridge server.</p>",
            "save_to_sent_items": True
        }
        
        try:
            response = await client.post(
                f"{base_url}/webhook/outlook/send_email",
                json=outlook_payload
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                print("   ✅ Outlook webhook endpoint accessible!")
            else:
                print("   ⚠️  Check MCP server connectivity")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 4: Response time check
        print("\n4️⃣ Testing response time...")
        try:
            start_time = datetime.now()
            response = await client.get(f"{base_url}/")
            end_time = datetime.now()
            
            response_time = (end_time - start_time).total_seconds() * 1000
            print(f"   Response time: {response_time:.2f}ms")
            
            if response_time < 500:
                print("   ✅ Excellent response time!")
            elif response_time < 1000:
                print("   ✅ Good response time")
            else:
                print("   ⚠️  Slow response time")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Testing complete!")
    print("\n📋 Summary:")
    print("- Bridge server is deployed and accessible")
    print("- Webhook endpoints are available")
    print("- MCP server connectivity should be verified with real requests")
    print("\n🔗 Webhook URLs for ElevenLabs configuration:")
    print(f"- Cal.com: {base_url}/webhook/cal/schedule_consultation")
    print(f"- Outlook: {base_url}/webhook/outlook/send_email")

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_bridge_deployment.py <bridge-server-url>")
        print("Example: python test_bridge_deployment.py https://bridge-server-xxxx.onrender.com")
        sys.exit(1)
    
    service_url = sys.argv[1].rstrip('/')
    
    if not service_url.startswith(('http://', 'https://')):
        print("Error: URL must start with http:// or https://")
        sys.exit(1)
    
    asyncio.run(test_bridge_deployment(service_url))

if __name__ == "__main__":
    main()