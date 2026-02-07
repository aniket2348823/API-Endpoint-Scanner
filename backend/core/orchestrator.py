import asyncio
import logging
from datetime import datetime
from backend.core.hive import EventBus, EventType, HiveEvent
# NeuroNegotiator removed - dead code cleanup V6
from backend.core.state import stats_db_manager
from backend.core.config import settings
from backend.api.socket_manager import manager

# Import Agents
from backend.agents.alpha import AlphaAgent
from backend.agents.beta import BetaAgent
from backend.agents.gamma import GammaAgent
from backend.agents.omega import OmegaAgent
from backend.agents.zeta import ZetaAgent
from backend.agents.sigma import SigmaAgent
from backend.agents.kappa import KappaAgent 
# V6 AGENTS
# V6 AGENTS
from backend.agents.sentinel import AgentTheta # Agent Theta (The Sentinel)
from backend.agents.inspector import AgentIota # Agent Iota (The Inspector)

# recorder removed - unused import cleanup V6
from backend.core.reporting import ReportGenerator # The Voice

logger = logging.getLogger("HiveOrchestrator")

class HiveOrchestrator:
    # Global Registry for API Access (Nervous System)
    active_agents = {}

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
                # payload might be nested or direct
                real_payload = event.payload
                # Check if payload is wrapped in 'payload' key
                if 'payload' in real_payload and isinstance(real_payload['payload'], dict):
                     # Flatten if needed, but usually real_payload is the dict we want
                     pass

                severity = real_payload.get('severity', 'High')
                stats_db_manager.record_finding(severity)
                
                # Broadcast authoritative stats to UI
                current_stats = stats_db_manager.get_stats()
                await manager.broadcast({
                    "type": "VULN_UPDATE", 
                    "payload": {
                        "metrics": {
                            "vulnerabilities": current_stats["vulnerabilities"],
                            "critical": current_stats["critical"],
                            "active_scans": current_stats["active_scans"], 
                            "total_scans": current_stats["total_scans"]
                        },
                        "graph_data": current_stats["history"]
                    }
                })

                # V6: Persist Threat Metrics
                threat_type = real_payload.get("type", "Unknown Threat")
                risk_score = real_payload.get("data", {}).get("risk_score", 0)
                stats_db_manager.record_threat(threat_type, risk_score)

                # Broadcast LIVE THREAT LOG (New Feature)
                await manager.broadcast({
                    "type": "LIVE_THREAT_LOG",
                    "payload": {
                        "agent": event.source, # e.g. "agent_theta" (Prism)
                        "threat_type": threat_type,
                        "url": real_payload.get("url", "Unknown Source"),
                        "severity": severity,
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                        "risk_score": risk_score
                    }
                })

            # REAL-TIME GRAPH ANIMATION (Visual Heartbeat)
            elif event.type == EventType.LOG or event.type == EventType.JOB_ASSIGNED:
                # Map specific agents to visual events
                msg_type = None
                
                if "beta" in event.source.lower() or "breaker" in event.source.lower():
                    msg_type = "ATTACK_HIT" # Purple/Red pulses
                elif "alpha" in event.source.lower() or "scout" in event.source.lower():
                    msg_type = "RECON_PACKET" # Blue/Cyan pulses
                elif "sigma" in event.source.lower():
                     msg_type = "GI5_CRITICAL" # Special AI pulse
                
                if msg_type:
                    # Lightweight broadcast for visual effects
                    await manager.broadcast({
                        "type": msg_type,
                        "payload": {
                            "source": event.source,
                            "timestamp": datetime.now().isoformat()
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
        
        # AWAKENING: The Sentinel and The Inspector (Purple Team Expansion)
        # AWAKENING: The Sentinel and The Inspector (Purple Team Expansion)
        sentinel = AgentTheta(bus)
        inspector = AgentIota(bus) 

        # 4. Wake Up the Hive
        # DATA WIRING: Pass Mission Profile
        mission_profile = {
            "modules": target_config.get("modules", []),
            "filters": target_config.get("filters", []),
            "scope": target_config.get("url", "")
        }
        
        agents = [scout, breaker, analyst, strategist, cortex, sigma, kappa, sentinel, inspector]
        for agent in agents:
            agent.mission_config = mission_profile # Inject Config
            await agent.start()
            
        # Register in Global State
        HiveOrchestrator.active_agents["THETA"] = sentinel
        HiveOrchestrator.active_agents["IOTA"] = inspector
        HiveOrchestrator.active_agents["OMEGA"] = strategist
        HiveOrchestrator.active_agents["ALPHA"] = scout
        HiveOrchestrator.active_agents["BETA"] = breaker
        HiveOrchestrator.active_agents["GAMMA"] = analyst
        HiveOrchestrator.active_agents["ZETA"] = cortex
        HiveOrchestrator.active_agents["SIGMA"] = sigma
        HiveOrchestrator.active_agents["KAPPA"] = kappa
            
        await manager.broadcast({"type": "GI5_LOG", "payload": "SINGULARITY V5 ONLINE. The Cortex is watching."})
        await manager.broadcast({"type": "SCAN_UPDATE", "payload": {"id": scan_id, "status": "Running"}})

        # 5. Seed the Mission
        await bus.publish(HiveEvent(
            type=EventType.TARGET_ACQUIRED,
            source="Orchestrator",
            payload={"url": target_config['url'], "tech_stack": ["Unknown"]} 
        ))

        await manager.broadcast({"type": "GI5_LOG", "payload": "HYPER-MIND ONLINE. Neural Negotiation Active."})

        # 6. Run Duration (Max 3 minutes for in-depth scanning)
        scan_duration = settings.SCAN_TIMEOUT  # 180 seconds
        try:
            await asyncio.sleep(scan_duration)
        except asyncio.CancelledError:
            pass
        finally:
            await manager.broadcast({"type": "GI5_LOG", "payload": "Hyper-Mind: Mission Complete. Shutting down."})
            for agent in agents: await agent.stop()
            # Clear registry
            HiveOrchestrator.active_agents.clear()
            
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
