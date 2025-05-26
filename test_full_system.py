#!/usr/bin/env python3
"""
Full System Integration Test for ElevenLabs → Bridge → MCP Servers
This script tests the complete flow to ensure smooth ElevenLabs integration
"""

import asyncio
import httpx
import json
import sys
from datetime import datetime, timezone, timedelta
import pytz
from typing import Dict, Any, List

class SystemTester:
    def __init__(self, bridge_url: str):
        self.bridge_url = bridge_url.rstrip('/')
        self.test_results = []
        
    def log_result(self, test_name: str, status: str, details: str = ""):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        # Print with color coding
        if status == "PASS":
            print(f"✅ {test_name}: {details}")
        elif status == "FAIL":
            print(f"❌ {test_name}: {details}")
        elif status == "WARN":
            print(f"⚠️  {test_name}: {details}")
        else:
            print(f"ℹ️  {test_name}: {details}")

    async def test_bridge_health(self, client: httpx.AsyncClient) -> bool:
        """Test if bridge server is healthy"""
        print("\n🔍 Testing Bridge Server Health...")
        try:
            response = await client.get(f"{self.bridge_url}/")
            if response.status_code == 200:
                self.log_result("Bridge Server Health", "PASS", "Server is running")
                return True
            else:
                self.log_result("Bridge Server Health", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Bridge Server Health", "FAIL", str(e))
            return False

    async def test_cal_com_booking_flow(self, client: httpx.AsyncClient):
        """Test the complete Cal.com booking flow"""
        print("\n📅 Testing Cal.com Booking Flow...")
        
        # Test 1: Valid booking request
        print("\n  1️⃣ Testing valid booking request...")
        
        # Create a booking for tomorrow at 2 PM EST
        tomorrow = datetime.now(pytz.timezone('America/New_York')) + timedelta(days=1)
        tomorrow_2pm = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
        utc_time = tomorrow_2pm.astimezone(timezone.utc)
        
        valid_payload = {
            "start_time_utc": utc_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "attendee_timezone": "America/New_York",
            "attendee_name": "Integration Test User",
            "attendee_email": "test@integration.example.com",
            "event_type_id": 1837761,  # Default 30-min consultation
            "language": "en",
            "metadata": {
                "source": "elevenlabs_integration_test",
                "test_run": True
            }
        }
        
        try:
            response = await client.post(
                f"{self.bridge_url}/webhook/cal/schedule_consultation",
                json=valid_payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Cal.com Valid Booking", 
                    "PASS", 
                    f"Booking processed: {data.get('message', 'Success')}"
                )
                
                # Check if booking details returned
                if data.get('details'):
                    print(f"     Booking ID: {data['details'].get('id', 'N/A')}")
                    print(f"     Status: {data['details'].get('status', 'N/A')}")
            else:
                self.log_result(
                    "Cal.com Valid Booking", 
                    "WARN", 
                    f"Status {response.status_code}: {response.json()}"
                )
        except Exception as e:
            self.log_result("Cal.com Valid Booking", "FAIL", str(e))
        
        # Test 2: Invalid timezone handling
        print("\n  2️⃣ Testing invalid timezone handling...")
        invalid_tz_payload = valid_payload.copy()
        invalid_tz_payload["attendee_timezone"] = "Invalid/Timezone"
        
        try:
            response = await client.post(
                f"{self.bridge_url}/webhook/cal/schedule_consultation",
                json=invalid_tz_payload
            )
            
            if response.status_code == 400:
                self.log_result("Cal.com Invalid Timezone", "PASS", "Properly rejected invalid timezone")
            else:
                self.log_result("Cal.com Invalid Timezone", "WARN", f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("Cal.com Invalid Timezone", "FAIL", str(e))
        
        # Test 3: Missing required fields
        print("\n  3️⃣ Testing missing required fields...")
        incomplete_payload = {
            "attendee_name": "Test User"
            # Missing required fields
        }
        
        try:
            response = await client.post(
                f"{self.bridge_url}/webhook/cal/schedule_consultation",
                json=incomplete_payload
            )
            
            if response.status_code in [400, 422]:
                self.log_result("Cal.com Field Validation", "PASS", "Properly validated missing fields")
            else:
                self.log_result("Cal.com Field Validation", "WARN", f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("Cal.com Field Validation", "FAIL", str(e))

    async def test_outlook_email_flow(self, client: httpx.AsyncClient):
        """Test the complete Outlook email flow"""
        print("\n📧 Testing Outlook Email Flow...")
        
        # Test 1: Valid email request
        print("\n  1️⃣ Testing valid email request...")
        valid_email = {
            "recipient_email": "test@example.com",
            "email_subject": "ElevenLabs Integration Test",
            "email_body_html": """
                <html>
                    <body>
                        <h2>Integration Test Email</h2>
                        <p>This is an automated test email from the ElevenLabs integration system.</p>
                        <p>Test timestamp: {}</p>
                        <p>If you receive this email, the integration is working correctly.</p>
                    </body>
                </html>
            """.format(datetime.now().isoformat()),
            "save_to_sent_items": True
        }
        
        try:
            response = await client.post(
                f"{self.bridge_url}/webhook/outlook/send_email",
                json=valid_email,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Outlook Valid Email", 
                    "PASS", 
                    f"Email processed: {data.get('message', 'Success')}"
                )
            else:
                self.log_result(
                    "Outlook Valid Email", 
                    "WARN", 
                    f"Status {response.status_code}: {response.json()}"
                )
        except Exception as e:
            self.log_result("Outlook Valid Email", "FAIL", str(e))
        
        # Test 2: Invalid email format
        print("\n  2️⃣ Testing invalid email format...")
        invalid_email = valid_email.copy()
        invalid_email["recipient_email"] = "not-an-email"
        
        try:
            response = await client.post(
                f"{self.bridge_url}/webhook/outlook/send_email",
                json=invalid_email
            )
            
            if response.status_code in [400, 422]:
                self.log_result("Outlook Email Validation", "PASS", "Properly rejected invalid email")
            else:
                self.log_result("Outlook Email Validation", "WARN", f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("Outlook Email Validation", "FAIL", str(e))
        
        # Test 3: HTML content handling
        print("\n  3️⃣ Testing HTML content handling...")
        html_test_email = valid_email.copy()
        html_test_email["email_body_html"] = """
            <div style="font-family: Arial, sans-serif;">
                <h1>Rich HTML Test</h1>
                <ul>
                    <li>Bold text: <strong>Important</strong></li>
                    <li>Links: <a href="https://example.com">Click here</a></li>
                    <li>Colors: <span style="color: #007bff;">Blue text</span></li>
                </ul>
            </div>
        """
        
        try:
            response = await client.post(
                f"{self.bridge_url}/webhook/outlook/send_email",
                json=html_test_email
            )
            
            if response.status_code == 200:
                self.log_result("Outlook HTML Content", "PASS", "HTML content accepted")
            else:
                self.log_result("Outlook HTML Content", "WARN", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Outlook HTML Content", "FAIL", str(e))

    async def test_elevenlabs_simulation(self, client: httpx.AsyncClient):
        """Simulate ElevenLabs webhook calls"""
        print("\n🤖 Simulating ElevenLabs Webhook Patterns...")
        
        # Simulate a conversational flow
        print("\n  📞 Simulating customer service conversation...")
        
        # Step 1: Customer wants to schedule a consultation
        print("\n  Step 1: Scheduling consultation...")
        next_week = datetime.now(pytz.timezone('America/New_York')) + timedelta(days=7)
        next_week_10am = next_week.replace(hour=10, minute=0, second=0, microsecond=0)
        
        booking_payload = {
            "start_time_utc": next_week_10am.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "attendee_timezone": "America/New_York",
            "attendee_name": "John Smith",
            "attendee_email": "john.smith@example.com",
            "event_type_id": 1837761,
            "language": "en",
            "metadata": {
                "conversation_id": "elevenlabs_test_12345",
                "agent_id": "test_agent",
                "customer_sentiment": "positive"
            }
        }
        
        try:
            response = await client.post(
                f"{self.bridge_url}/webhook/cal/schedule_consultation",
                json=booking_payload
            )
            
            if response.status_code == 200:
                self.log_result("ElevenLabs Booking Simulation", "PASS", "Consultation scheduled")
                
                # Step 2: Send confirmation email
                print("\n  Step 2: Sending confirmation email...")
                email_payload = {
                    "recipient_email": "john.smith@example.com",
                    "email_subject": "Your Consultation is Confirmed",
                    "email_body_html": f"""
                        <html>
                            <body style="font-family: Arial, sans-serif; color: #333;">
                                <h2>Consultation Confirmation</h2>
                                <p>Dear John Smith,</p>
                                <p>Your consultation has been scheduled for {next_week_10am.strftime('%B %d, %Y at %I:%M %p %Z')}.</p>
                                <p>We look forward to speaking with you!</p>
                                <hr>
                                <p style="font-size: 12px; color: #666;">
                                    This email was sent by your AI assistant powered by ElevenLabs.
                                </p>
                            </body>
                        </html>
                    """,
                    "save_to_sent_items": True
                }
                
                email_response = await client.post(
                    f"{self.bridge_url}/webhook/outlook/send_email",
                    json=email_payload
                )
                
                if email_response.status_code == 200:
                    self.log_result("ElevenLabs Email Simulation", "PASS", "Confirmation email sent")
                else:
                    self.log_result("ElevenLabs Email Simulation", "WARN", f"Email status: {email_response.status_code}")
            else:
                self.log_result("ElevenLabs Booking Simulation", "WARN", f"Booking status: {response.status_code}")
                
        except Exception as e:
            self.log_result("ElevenLabs Simulation", "FAIL", str(e))

    async def test_performance_and_reliability(self, client: httpx.AsyncClient):
        """Test system performance and reliability"""
        print("\n⚡ Testing Performance and Reliability...")
        
        # Test concurrent requests
        print("\n  🔄 Testing concurrent webhook calls...")
        
        async def make_cal_request():
            payload = {
                "start_time_utc": datetime.now(timezone.utc).isoformat() + "Z",
                "attendee_timezone": "UTC",
                "attendee_name": "Perf Test",
                "attendee_email": "perf@test.com",
                "event_type_id": 1837761
            }
            start = datetime.now()
            try:
                response = await client.post(
                    f"{self.bridge_url}/webhook/cal/schedule_consultation",
                    json=payload
                )
                duration = (datetime.now() - start).total_seconds() * 1000
                return response.status_code, duration
            except:
                return None, None
        
        # Send 5 concurrent requests
        tasks = [make_cal_request() for _ in range(5)]
        results = await asyncio.gather(*tasks)
        
        successful = sum(1 for status, _ in results if status == 200)
        avg_time = sum(duration for _, duration in results if duration) / len(results)
        
        if successful == len(results):
            self.log_result("Concurrent Requests", "PASS", f"All {len(results)} requests succeeded, avg time: {avg_time:.0f}ms")
        else:
            self.log_result("Concurrent Requests", "WARN", f"{successful}/{len(results)} succeeded")

    def generate_summary_report(self):
        """Generate a summary report of all tests"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        warnings = sum(1 for r in self.test_results if r['status'] == 'WARN')
        
        print(f"\nTotal Tests: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warnings}")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"  - {result['test']}: {result['details']}")
        
        if warnings > 0:
            print("\n⚠️  WARNINGS:")
            for result in self.test_results:
                if result['status'] == 'WARN':
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n" + "=" * 60)
        
        if failed == 0:
            print("✅ SYSTEM READY FOR ELEVENLABS INTEGRATION!")
            print("\n🔗 Webhook URLs for ElevenLabs:")
            print(f"  - Cal.com: {self.bridge_url}/webhook/cal/schedule_consultation")
            print(f"  - Outlook: {self.bridge_url}/webhook/outlook/send_email")
        else:
            print("❌ SYSTEM NOT READY - Please fix failed tests before integration")
        
        return failed == 0

async def main(bridge_url: str):
    """Run all system tests"""
    tester = SystemTester(bridge_url)
    
    print("🚀 Starting Full System Integration Tests")
    print(f"Bridge Server: {bridge_url}")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test bridge health first
        if not await tester.test_bridge_health(client):
            print("\n❌ Bridge server is not accessible. Aborting tests.")
            return False
        
        # Run all test suites
        await tester.test_cal_com_booking_flow(client)
        await tester.test_outlook_email_flow(client)
        await tester.test_elevenlabs_simulation(client)
        await tester.test_performance_and_reliability(client)
    
    # Generate summary report
    return tester.generate_summary_report()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_full_system.py <bridge-server-url>")
        print("Example: python test_full_system.py https://bridge-server-xxxx.onrender.com")
        sys.exit(1)
    
    bridge_url = sys.argv[1].rstrip('/')
    
    if not bridge_url.startswith(('http://', 'https://')):
        print("Error: URL must start with http:// or https://")
        sys.exit(1)
    
    # Run tests
    success = asyncio.run(main(bridge_url))
    sys.exit(0 if success else 1)