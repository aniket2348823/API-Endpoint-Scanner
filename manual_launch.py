import requests
import json
import time

url = "http://127.0.0.1:8000/api/attack/fire"
payload = {
    "target_url": "http://test-launch.com/api",
    "method": "GET",
    "headers": {"User-Agent": "Manual-Launcher"},
    "velocity": 50,
    "body": ""
}

print(f"🚀 MANUAL LAUNCH SEQUENCE: Sending POST to {url}...")
try:
    res = requests.post(url, json=payload)
    print(f"✅ Status: {res.status_code}")
    print(f"📥 Response: {res.text}")
except Exception as e:
    print(f"❌ Failed: {e}")
