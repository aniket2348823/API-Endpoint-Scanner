import asyncio
import difflib
import random
from backend.core.hive import BaseAgent, EventType, HiveEvent
from backend.core.protocol import JobPacket, ResultPacket, AgentID, TaskPriority
# Import Modules
from backend.modules.logic.tycoon import TheTycoon
from backend.modules.logic.doppelganger import Doppelganger

class GammaAgent(BaseAgent):
    """
    AGENT GAMMA: THE AUDITOR
    Role: Logic Verification.
    Capabilities:
    - Diff-Based Anomaly Detection (Baseline vs Attack).
    - Verification Mode.
    """
    def __init__(self, bus):
        super().__init__("agent_gamma", bus)
        self.arsenal = {
            "logic_tycoon": TheTycoon(),
            "logic_doppelganger": Doppelganger()
        }
        self.baseline_cache = {}

    async def setup(self):
        self.bus.subscribe(EventType.JOB_ASSIGNED, self.handle_job)

    async def handle_job(self, event: HiveEvent):
        # ... (Argument parsing)
        payload = event.payload
        try:
            packet = JobPacket(**payload)
        except: return

        if packet.config.agent_id != AgentID.GAMMA:
            return

        print(f"[{self.name}] Auditing Job {packet.id}")

        # Cyber-Organism Protocol: Verification Mode
        # If this is a re-scan request (e.g. from Beta finding), we lower aggression
        if packet.config.aggression > 5 and packet.priority == TaskPriority.CRITICAL:
            print(f"[{self.name}] [VERIFY] MODE. Lowering aggression to 1 for confirmation.")
            packet.config.aggression = 1 
        
        # SOTA: ANOMALY DIFFING
        # If we have a baseline response, compare it
        baseline = self.baseline_cache.get(packet.target.url)
        
        module_id = packet.config.module_id
        if module_id in self.arsenal:
            module = self.arsenal[module_id]
            result = await module.execute(packet)
            
            # Post-Execution Analysis
            # If ResultPacket contains data, we diff it against baseline
            if result.data and "raw_response" in result.data:
                response_text = result.data["raw_response"]
                if not baseline:
                    # First run is baseline
                    self.baseline_cache[packet.target.url] = response_text
                else:
                    # Compare
                    similarity = difflib.SequenceMatcher(None, baseline, response_text).ratio()
                    if similarity < 0.95 and similarity > 0.5:
                        # Subtle change detected (Not a 404, but different content)
                        print(f"[{self.name}] [DIFF] ANOMALY DETECTED (Sim: {similarity:.2f}). Possible Leak.")
                        
                        await self.bus.publish(HiveEvent(
                            type=EventType.VULN_CONFIRMED,
                            source=self.name,
                            payload={
                                "type": "LOGIC_ANOMALY",
                                "id": f"AG-{random.randint(10,99)}", 
                                "url": packet.target.url,
                                "similarity": similarity,
                                "payload": packet.target.payload
                            }
                        ))
            
            await self.bus.publish(HiveEvent(
                type=EventType.JOB_COMPLETED,
                source=self.name,
                payload=result.dict()
            ))
