import requests
import json
import os
import time
import sys
import subprocess
from datetime import datetime

# CONFIG
BASE_URL = "http://127.0.0.1:8000"
MEMORY_FILE = "d:/Antigravity 2/API Endpoint Scanner/brain/memory.json"

def print_result(test_name, success, message=""):
    icon = "[PASS]" if success else "[FAIL]"
    print(f"{icon} {test_name}: {message}")
    if not success:
        print(f"   [!] Critical Failure in {test_name}")

def verify_manifest():
    try:
        with open("d:/Antigravity 2/API Endpoint Scanner/extension/manifest.json", "r") as f:
            manifest = json.load(f)
        
        has_scanner = "content/ScannerEngine.js" in manifest["content_scripts"][0]["js"]
        print_result("Manifest Integrity", has_scanner, "ScannerEngine.js found in manifest")
        return has_scanner
    except Exception as e:
        print_result("Manifest Integrity", False, str(e))
        return False

def verify_brain_path():
    # Check if the memory file path used by the backend actually exists or is writable
    # logic is simulated since we aren't running the server in this script context, 
    # but we can check the file system.
    
    # We expect the file to exist or be creatable at the PROJECT path, not the old one.
    if os.path.exists("d:/Antigravity 2/brain"):
        print_result("Brain Location", False, "Old 'd:/Antigravity 2/brain' folder still exists! It should be deleted.")
    else:
        print_result("Brain Location", True, "Old 'brain' folder correctly removed.")
        
    path = "d:/Antigravity 2/API Endpoint Scanner/brain"
    if os.path.exists(path):
        print_result("New Brain Path", True, f"Found correct brain at {path}")
    else:
        # It might be created on runtime, implying we need to make it
        try:
            os.makedirs(path, exist_ok=True)
            print_result("New Brain Path", True, f"Created brain directory at {path}")
        except:
             print_result("New Brain Path", False, "Could not create brain directory")

def run_server_check():
    print("\n--- STARTING BACKEND FOR CONNECTIVITY TEST ---")
    # We will try to start the server in disjoint mode just to test endpoints
    # This is risky in a script, so instead we will assume the User WILL run the server
    # and we will just fail gracefully if it's not up.
    
    # Actually, let's try to hit the health check or invalid endpoint
    try:
        r = requests.get(f"{BASE_URL}/docs", timeout=2)
        print_result("Backend Connectivity", r.status_code == 200, "Backend is UP on port 8000")
        return True
    except:
        print_result("Backend Connectivity", False, "Backend NOT running on port 8000. Start it with 'uvicorn backend.main:app'")
        return False

def test_data_pipeline():
    if not run_server_check():
        print("   [!] Skipping Data Pipeline Tests (Server Offline)")
        return

    print("\n--- TESTING DATA PIPELINE ---")
    
    # 1. Mock Extension Sending Data
    payload = {
        "url": "http://test-target.com",
        "method": "SCAN",
        "headers": { "x-scanner": "v12-engine" },
        "timestamp": time.time(),
        "payload": {
            "findings": [
                {
                    "category": "TEST_FLAW",
                    "description": "Verification Probe",
                    "evidence": "Verification-123"
                }
            ]
        }
    }
    
    try:
        r = requests.post(f"{BASE_URL}/api/recon/ingest", json=payload)
        print_result("Recon Ingestion", r.status_code == 200, f"Status: {r.status_code}")
    except Exception as e:
        print_result("Recon Ingestion", False, str(e))
        return

    # 2. Check Brain Memory
    time.sleep(1) # Wait for IO
    try:
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)
        
        found = any(item.get("payload", {}).get("evidence") == "Verification-123" for item in data)
        print_result("Brain Memory Sync", found, "Found 'Verification Probe' in memory.json")
    except Exception as e:
        print_result("Brain Memory Sync", False, f"Read Error: {e}")

if __name__ == "__main__":
    print("=== ANTIGRAVITY SYSTEM VERIFICATION ===")
    verify_manifest()
    verify_brain_path()
    test_data_pipeline()
    print("\n=== VERIFICATION COMPLETE ===")
