import sys
import os

# Add project root to path
sys.path.append("d:/Antigravity 2/API Endpoint Scanner")

try:
    from backend.ai.gi5 import GI5Engine
    print("Successfully imported GI5Engine")
    
    gi5 = GI5Engine(api_key="verify_only")
    
    # Check if PROMPT is accessible and contains key phrases
    if "ANTIGRAVITY V12 // FORENSIC TRUTH KERNEL" in gi5.V12_SYSTEM_PROMPT:
        print("V12 System Prompt found.")
    else:
        print("ERROR: V12 System Prompt not found in GI5Engine")
        
    if "PHASE 1: THE ACCURACY LAWS" in gi5.V12_SYSTEM_PROMPT:
        print("Phase 1 verified.")
        
    print("Verification script finished.")
except Exception as e:
    print(f"Verification failed: {e}")
