from fastapi import APIRouter, HTTPException, BackgroundTasks
from backend.schemas.payloads import AttackPayload
from backend.core.orchestrator import HiveOrchestrator
from backend.api.socket_manager import manager
from datetime import datetime
import uuid
from backend.core.state import stats_db

router = APIRouter()

@router.post("/fire")
async def fire_attack(payload: AttackPayload, background_tasks: BackgroundTasks):
    """
    Triggers the Antigravity V5 Singularity Swarm.
    Replaces legacy Gatekeeper Engine.
    """
    scan_id = str(uuid.uuid4())
    
    # 1. Prepare Configuration
    target_config = {
        "url": payload.target_url,
        "method": payload.method,
        "headers": payload.headers,
        "payload": payload.body, # Original body for Tycoon/Escalator
        "velocity": payload.velocity,
        "modules": payload.modules,
        "filters": payload.filters
    }
    
    # 2. Initial DB Registration (Orchestrator updates this too, but we reserve the slot)
    # We do a minimal placeholder here to ensure immediate UI feedback
    # 2. Initial DB Registration (Sync)
    # Use Manager to ensure persistence to disk immediately
    from backend.core.state import stats_db_manager
    start_time = datetime.now()
    scan_record = {
        "id": scan_id,
        "status": "Initializing",
        "name": target_config['url'],
        "scope": target_config['url'],
        "modules": target_config['modules'] if target_config['modules'] else ["Singularity V5"],
        "timestamp": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "results": []
    }
    stats_db_manager.register_scan(scan_record)
    
    # 3. Launch The Hive (Background Task)
    # The Orchestrator manages the entire lifecycle (Agents, EventBus, Reporting)
    background_tasks.add_task(HiveOrchestrator.bootstrap_hive, target_config, scan_id)
    
    # 4. Immediate Response
    return {
        "status": "Swarm Online",
        "scan_id": scan_id,
        "message": "The Singularity has been unleashed. Monitor the 'Live Graph' for real-time telemetry."
    }
