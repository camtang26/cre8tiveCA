#!/usr/bin/env python3
"""Quick test of bridge server health endpoint"""
import httpx
import asyncio

async def test_health():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8000/health")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_health())