#!/usr/bin/env python3
"""
Quick System Test - Validates basic functionality
"""

import requests
import json
import sys
from datetime import datetime, timedelta
import pytz

def test_system(bridge_url: str):
    """Quick test of the system"""
    bridge_url = bridge_url.rstrip('/')
    
    print(f"🚀 Quick System Test")
    print(f"Bridge URL: {bridge_url}")
    print("=" * 50)
    
    # Test 1: Bridge server health
    print("\n1️⃣ Testing Bridge Server...")
    try:
        response = requests.get(f"{bridge_url}/", timeout=10)
        if response.status_code == 200:
            print("✅ Bridge server is running")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Bridge server error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot reach bridge server: {e}")
        return False
    
    # Test 2: Cal.com webhook (dry run)
    print("\n2️⃣ Testing Cal.com Webhook...")
    tomorrow = datetime.now(pytz.timezone('America/New_York')) + timedelta(days=1)
    tomorrow_3pm = tomorrow.replace(hour=15, minute=0, second=0, microsecond=0)
    
    cal_payload = {
        "start_time_utc": tomorrow_3pm.astimezone(pytz.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "attendee_timezone": "America/New_York",
        "attendee_name": "Quick Test User",
        "attendee_email": "quicktest@example.com",
        "event_type_id": 1837761,
        "language": "en"
    }
    
    try:
        response = requests.post(
            f"{bridge_url}/webhook/cal/schedule_consultation",
            json=cal_payload,
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Cal.com webhook is functional")
        else:
            print("⚠️  Cal.com webhook returned non-200 status")
    except Exception as e:
        print(f"❌ Cal.com webhook error: {e}")
    
    # Test 3: Outlook webhook (dry run)
    print("\n3️⃣ Testing Outlook Webhook...")
    email_payload = {
        "recipient_email": "test@example.com",
        "email_subject": "Quick System Test",
        "email_body_html": f"<p>Quick test at {datetime.now()}</p>",
        "save_to_sent_items": True
    }
    
    try:
        response = requests.post(
            f"{bridge_url}/webhook/outlook/send_email",
            json=email_payload,
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Outlook webhook is functional")
        else:
            print("⚠️  Outlook webhook returned non-200 status")
    except Exception as e:
        print(f"❌ Outlook webhook error: {e}")
    
    print("\n" + "=" * 50)
    print("📋 Webhook URLs for ElevenLabs:")
    print(f"Cal.com: {bridge_url}/webhook/cal/schedule_consultation")
    print(f"Outlook: {bridge_url}/webhook/outlook/send_email")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python quick_system_test.py <bridge-server-url>")
        sys.exit(1)
    
    test_system(sys.argv[1])