#!/usr/bin/env python3
"""
Test script for direct API integration locally.
Run from project root: python test_direct_api_local.py
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set integration mode to direct for testing
os.environ["INTEGRATION_MODE"] = "direct"

import logging
logging.basicConfig(level=logging.INFO)

async def test_cal_com_direct():
    """Test Cal.com direct API client."""
    from bridge_server.api_clients.cal_com_direct import CalComDirectClient, CalComBookingInput
    from bridge_server.core.config import CAL_COM_API_KEY, CAL_COM_API_BASE_URL, DEFAULT_EVENT_TYPE_ID
    
    if not CAL_COM_API_KEY:
        print("[FAIL] CAL_COM_API_KEY not set in bridge_server/.env")
        return False
    
    print("\n=== Testing Cal.com Direct API Client ===")
    
    client = CalComDirectClient(
        api_key=CAL_COM_API_KEY,
        api_base_url=CAL_COM_API_BASE_URL
    )
    
    # Create test booking for tomorrow at 2 PM UTC
    tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
    start_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(minutes=30)
    
    booking_input = CalComBookingInput(
        localDate=tomorrow.strftime("%Y-%m-%d"),
        localTime="14:00",
        localTimeZone="America/New_York",
        attendeeName="Test User",
        attendeeEmail="test@example.com",
        eventTypeId=DEFAULT_EVENT_TYPE_ID,
        eventDurationMinutes=30,
        guests=[],
        metadata={"source": "direct_api_test"},
        language="en"
    )
    
    try:
        result = await client.create_booking(booking_input)
        if result.success:
            print(f"[SUCCESS] Cal.com booking created successfully!")
            print(f"   Booking ID: {result.booking_id}")
            print(f"   Booking UID: {result.booking_uid}")
            print(f"   Title: {result.title}")
            print(f"   Start: {result.start_time}")
            print(f"   End: {result.end_time}")
            print(f"   Meet URL: {result.meet_url}")
            return True
        else:
            print(f"[FAIL] Cal.com booking failed: {result.message}")
            print(f"   Details: {result.error_details}")
            return False
    except Exception as e:
        print(f"[FAIL] Exception during Cal.com test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_outlook_direct():
    """Test Outlook direct API client."""
    from bridge_server.api_clients.outlook_direct import OutlookDirectClient, OutlookEmailInput
    from bridge_server.core.config import AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, SENDER_UPN
    
    if not all([AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, SENDER_UPN]):
        print("[FAIL] Azure/Outlook credentials not fully set in bridge_server/.env")
        return False
    
    print("\n=== Testing Outlook Direct API Client ===")
    
    client = OutlookDirectClient(
        tenant_id=AZURE_TENANT_ID,
        client_id=AZURE_CLIENT_ID,
        client_secret=AZURE_CLIENT_SECRET,
        sender_upn=SENDER_UPN
    )
    
    email_input = OutlookEmailInput(
        recipientEmail="test@example.com",
        emailSubject="Test Email from Direct API Integration",
        emailBodyHtml="<html><body><h1>Test Email</h1><p>This is a test email sent via direct Microsoft Graph API integration.</p></body></html>",
        saveToSentItems=False
    )
    
    try:
        result = await client.send_email(email_input)
        if result.success:
            print(f"[SUCCESS] Outlook email sent successfully!")
            print(f"   Message ID: {result.message_id}")
            print(f"   Message: {result.message}")
            return True
        else:
            print(f"[FAIL] Outlook email failed: {result.message}")
            print(f"   Details: {result.error_details}")
            return False
    except Exception as e:
        print(f"[FAIL] Exception during Outlook test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_bridge_server():
    """Test the bridge server with direct API integration."""
    print("\n=== Testing Bridge Server with Direct API ===")
    
    # Check if server is running
    import httpx
    
    try:
        async with httpx.AsyncClient() as client:
            # Test health endpoint
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                data = response.json()
                print(f"[SUCCESS] Bridge server is running")
                print(f"   Integration mode: {data.get('integration_mode')}")
                print(f"   Status: {data.get('status')}")
                
                if data.get('integration_mode') != 'direct':
                    print("[WARNING] Bridge server is not in direct mode!")
                    print("   Set INTEGRATION_MODE=direct in bridge_server/.env")
            else:
                print(f"[FAIL] Bridge server health check failed: {response.status_code}")
                
    except Exception as e:
        print(f"[FAIL] Could not connect to bridge server at localhost:8000")
        print(f"   Make sure to run: uvicorn bridge_server.main:app --port 8000 --reload")
        print(f"   Error: {e}")

async def main():
    """Run all tests."""
    print("Testing Direct API Integration\n")
    
    # Test individual clients
    cal_success = await test_cal_com_direct()
    outlook_success = await test_outlook_direct()
    
    # Test bridge server
    await test_bridge_server()
    
    print("\nTest Summary:")
    print(f"   Cal.com Direct API: {'PASSED' if cal_success else 'FAILED'}")
    print(f"   Outlook Direct API: {'PASSED' if outlook_success else 'FAILED'}")
    
    if cal_success and outlook_success:
        print("\n[SUCCESS] All direct API tests passed! Ready for deployment.")
    else:
        print("\n[FAIL] Some tests failed. Check configuration and try again.")

if __name__ == "__main__":
    asyncio.run(main())