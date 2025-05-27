#!/usr/bin/env python3
"""
Simple test to check bridge server behavior
"""

import requests
import time

print("Testing Bridge Server...")
bridge_url = "https://elevenlabs-bridge-server.onrender.com"

# Test 1: Basic health
print("\n1. Testing basic health...")
start = time.time()
try:
    response = requests.get(f"{bridge_url}/", timeout=10)
    print(f"✅ Health check: {response.status_code} in {time.time() - start:.1f}s")
except Exception as e:
    print(f"❌ Health check failed: {e}")

# Test 2: Invalid timezone (should fail fast)
print("\n2. Testing invalid timezone (should fail quickly)...")
start = time.time()
try:
    response = requests.post(
        f"{bridge_url}/webhook/cal/schedule_consultation",
        json={
            "start_time_utc": "2025-12-20T15:00:00Z",
            "attendee_timezone": "Invalid/Timezone",  # Invalid timezone
            "attendee_name": "Test",
            "attendee_email": "test@test.com",
            "event_type_id": 1837761
        },
        timeout=10
    )
    print(f"✅ Invalid timezone test: {response.status_code} in {time.time() - start:.1f}s")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"❌ Invalid timezone test failed: {e}")

# Test 3: Missing fields (should fail fast)
print("\n3. Testing missing fields (should fail quickly)...")
start = time.time()
try:
    response = requests.post(
        f"{bridge_url}/webhook/cal/schedule_consultation",
        json={"attendee_name": "Test"},  # Missing required fields
        timeout=10
    )
    print(f"✅ Missing fields test: {response.status_code} in {time.time() - start:.1f}s")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"❌ Missing fields test failed: {e}")

print("\n" + "="*50)
print("Summary: If tests 2 and 3 passed quickly, the bridge server validation is working.")
print("The timeout issue is likely with MCP server connections on valid requests.")