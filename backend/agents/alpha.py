import asyncio
from backend.core.hive import BaseAgent, EventType, HiveEvent
from backend.core.protocol import JobPacket, ResultPacket, AgentID
# Import Modules
from backend.modules.logic.skipper import TheSkipper
from backend.modules.tech.auth_bypass import AuthBypassTester

class AlphaAgent(BaseAgent):
    """
    AGENT ALPHA: THE SCOUT
    Role: Recon & API Detection.
    """
    def __init__(self, bus):
        super().__init__("agent_alpha", bus)
        # Load Arsenal
        self.arsenal = {
            "logic_skipper": TheSkipper(),
            "tech_auth_bypass": AuthBypassTester()
        }

    async def setup(self):
        # Listen for assigned jobs
        self.bus.subscribe(EventType.JOB_ASSIGNED, self.handle_job)

    async def handle_job(self, event: HiveEvent):
        """
        Process incoming job.
        """
        payload = event.payload
        try:
            packet = JobPacket(**payload)
        except Exception as e:
            print(f"[{self.name}] Error parsing job: {e}")
            return

        # Am I the target?
        if packet.config.agent_id != AgentID.ALPHA:
            return

        print(f"[{self.name}] Received Job {packet.id} ({packet.config.module_id})")
        
        # 1. API Detection Logic
        api_indicators = ["/api", "/v1", "graphql", "swagger"]
        is_api = any(ind in packet.target.url.lower() for ind in api_indicators)
        
        if is_api:
            print(f"[{self.name}]: API DETECTED. Dispatching Handover.")
            # Real implementation: Publish a VULN_CANDIDATE event that Beta listens to
            await self.bus.publish(HiveEvent(
                type=EventType.VULN_CANDIDATE,
                source=self.name,
                payload={"url": packet.target.url, "tag": "API"}
            ))

        # Cyber-Organism Protocol: Target Acquisition
        sensitive_paths = ["/order", "/user", "/account", "/profile"]
        if any(p in packet.target.url.lower() for p in sensitive_paths):
            print(f"[{self.name}]: [TARGET] IDOR Target Acquired. Tagging for Doppelganger.")
            
            await self.bus.publish(HiveEvent(
                type=EventType.TARGET_ACQUIRED,
                source=self.name,
                payload={"url": packet.target.url, "method": "POST"}
            ))
            await self.bus.publish(HiveEvent(
                type=EventType.VULN_CANDIDATE,
                source=self.name,
                payload={"url": packet.target.url, "tag": "DOPPELGANGER_CANDIDATE"}
            ))

        # 2. Execute Module
        module_id = packet.config.module_id
        if module_id in self.arsenal:
            module = self.arsenal[module_id]
            result = await module.execute(packet)
            
            # REAL-TIME SYNC
            if result.success:
                severity = "High" if "auth" in module_id else "Medium"
                await self.bus.publish(HiveEvent(
                    type=EventType.VULN_CONFIRMED,
                    source=self.name,
                    payload={
                        "type": module_id.upper(),
                        "url": packet.target.url,
                        "severity": severity,
                        "payload": "Logic Flaw"
                    }
                ))

            # Publish Result
            await self.bus.publish(HiveEvent(
                type=EventType.JOB_COMPLETED,
                source=self.name,
                payload=result.dict()
            ))
        else:
            print(f"[{self.name}] Module {module_id} not found.")
