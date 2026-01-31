import asyncio
import logging
from datetime import datetime
from backend.core.hive import EventBus, EventType, HiveEvent
from backend.core.hyper_hive import NeuroNegotiator 
from backend.core.state import stats_db_manager
from backend.core.config import settings
from backend.api.socket_manager import manager

# Import Agents
# Import Agents (Antigravity V5)
from backend.agents.alpha import AlphaAgent
from backend.agents.beta import BetaAgent
from backend.agents.gamma import GammaAgent
from backend.agents.omega import OmegaAgent
from backend.agents.zeta import ZetaAgent
from backend.agents.sigma import SigmaAgent
from backend.agents.kappa import KappaAgent 

from backend.core.memory import recorder # The Hippocampus
from backend.core.reporting import ReportGenerator # The Voice

logger = logging.getLogger("HiveOrchestrator")

class HiveOrchestrator:
    @staticmethod
    async def bootstrap_hive(target_config, scan_id=None):
        """
        Initializes the Antigravity V5 Singularity.
        """
        start_time = datetime.now()
        if not scan_id:
             scan_id = f"HIVE-V5-{int(start_time.timestamp())}"

        # 0. Register Scan (Idempotent Check)
        # Check if already registered by attack.py
        existing = next((s for s in stats_db_manager.get_stats()["scans"] if s["id"] == scan_id), None)
        if not existing:
            scan_record = {
                "id": scan_id,
                "status": "Initializing",
                "name": target_config['url'],
                "scope": target_config['url'],
                "modules": ["Singularity V5"],
                "timestamp": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "results": []
            }
            try:
                stats_db_manager.register_scan(scan_record)
            except Exception:
                pass # DB might be locked
        else:
             # Just update status if needed
             for s in stats_db_manager.get_stats()["scans"]:
                 if s["id"] == scan_id:
                     s["status"] = "Running"
                     break
             stats_db_manager._save()
            
        await manager.broadcast({"type": "SCAN_UPDATE", "payload": {"id": scan_id, "status": "Initializing"}})

        # 1. Create Nervous System
        bus = EventBus()
        
        # --- REPORTING LINK ---
        scan_events = []
        async def event_listener(event: HiveEvent):
            scan_events.append(event.dict())
            
            # REAL-TIME DASHBOARD SYNC
            if event.type == EventType.VULN_CONFIRMED:
                # Update global stats immediately
                severity = event.payload.get('severity', 'Medium')
                stats_db_manager.record_finding(severity)
                
                # Broadcast authoritative stats to UI
                current_stats = stats_db_manager.get_stats()
                await manager.broadcast({
                    "type": "VULN_UPDATE",
                    "payload": current_stats
                })
            
            # REAL-TIME DASHBOARD SYNC
            if event.type == EventType.VULN_CONFIRMED:
                # 1. Update Persistent DB immediately
                payload = event.payload.get('payload', {})
                severity = payload.get('severity', 'High') if isinstance(payload, dict) else 'High'
                stats_db_manager.record_finding(severity)
                
                # 2. Broadcast authoritative stats to UI
                current_stats = stats_db_manager.get_stats()
                await manager.broadcast({
                    "type": "VULN_UPDATE", 
                    "payload": {
                        "metrics": {
                            "vulnerabilities": current_stats["vulnerabilities"],
                            "critical": current_stats["critical"],
                            "active_scans": current_stats["active_scans"], # Keep sync
                            "total_scans": current_stats["total_scans"]
                        },
                        "graph_data": current_stats["history"]
                    }
                })

        # Subscribe Recorder to Everything for maximum fidelity
        for etype in EventType:
            bus.subscribe(etype, event_listener)
        # ----------------------

        # 2. Spawn Agents (Singularity V5)
        # All agents now inherit from Hive BaseAgent and take `bus`
        scout = AlphaAgent(bus)
        breaker = BetaAgent(bus)
        analyst = GammaAgent(bus)
        strategist = OmegaAgent(bus)
        cortex = ZetaAgent(bus)
        
        # AWAKENING: The Smith and The Librarian
        sigma = SigmaAgent(bus)
        kappa = KappaAgent(bus) 

        # 4. Wake Up the Hive
        agents = [scout, breaker, analyst, strategist, cortex, sigma, kappa]
        for agent in agents:
            await agent.start()
            
        await manager.broadcast({"type": "GI5_LOG", "payload": "SINGULARITY V5 ONLINE. The Cortex is watching."})
        await manager.broadcast({"type": "SCAN_UPDATE", "payload": {"id": scan_id, "status": "Running"}})

        # 5. Seed the Mission
        await bus.publish(HiveEvent(
            type=EventType.TARGET_ACQUIRED,
            source="Orchestrator",
            payload={"url": target_config['url']}
        ))

        await manager.broadcast({"type": "GI5_LOG", "payload": "HYPER-MIND ONLINE. Neural Negotiation Active."})
        await manager.broadcast({"type": "SCAN_UPDATE", "payload": {"id": scan_id, "status": "Running"}})

        # 5. Seed the Mission (Redundant Target Acquired removed, single seed is enough usually, but strictly following legacy flow)
        await bus.publish(HiveEvent(
            type=EventType.TARGET_ACQUIRED,
            source="Orchestrator",
            payload={"url": target_config['url'], "tech_stack": ["Unknown"]} 
        ))

        # 6. Run Duration (Max 3 minutes for in-depth scanning)
        scan_duration = settings.SCAN_TIMEOUT  # 180 seconds
        try:
            await asyncio.sleep(scan_duration)
        except asyncio.CancelledError:
            pass
        finally:
            await manager.broadcast({"type": "GI5_LOG", "payload": "Hyper-Mind: Mission Complete. Shutting down."})
            for agent in agents: await agent.stop()
            
            # --- GENERATE GOD MODE REPORT ---
            items_found = [e for e in scan_events if e['type'] == EventType.VULN_CONFIRMED]
            stats_db_manager.complete_scan(scan_id, items_found, scan_duration)
            
            try:
                report_path = ReportGenerator().generate_report(scan_id, scan_events, target_config['url'])
                await manager.broadcast({"type": "GI5_LOG", "payload": f"REPORT GENERATED: {report_path}"})
            except Exception as e:
                logger.error(f"Report Gen Failed: {e}")
            # --------------------------------

            await manager.broadcast({"type": "SCAN_UPDATE", "payload": {"id": scan_id, "status": "Completed"}})
