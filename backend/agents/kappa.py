import asyncio
import json
import os
from backend.core.hive import BaseAgent, EventType, HiveEvent
from backend.core.protocol import JobPacket, ResultPacket, AgentID

class KappaAgent(BaseAgent):
    """
    AGENT KAPPA: THE LIBRARIAN
    Role: Knowledge & Memory.
    Capabilities:
    - Persistent Memory (JSON Store).
    - Auto-Report Generation (Stub for PDF).
    - Collaborative Filtering (Recommendation).
    """
    def __init__(self, bus):
        super().__init__("agent_kappa", bus)
        # GAP FIX: Correct Path inside project
        self.memory_file = "d:/Antigravity 2/API Endpoint Scanner/brain/memory.json"
        
        # Initialize Truth Kernel
        try:
            from backend.ai.gi5 import GI5Engine
            self.truth_kernel = GI5Engine()
        except:
            self.truth_kernel = None
            
        self._ensure_memory()

    def _ensure_memory(self):
        # Create directory if needed
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, "w") as f:
                json.dump([], f)

    async def setup(self):
        # Listen for success stories to archive
        self.bus.subscribe(EventType.JOB_COMPLETED, self.archive_victory)
        # GAP FIX: Listen for raw recon data to audit
        self.bus.subscribe(EventType.VULN_CANDIDATE, self.audit_candidate)

    async def audit_candidate(self, event: HiveEvent):
        """
        Antigravity V12: The Forensic Truth Kernel Audit
        """
        payload = event.payload
        print(f"[{self.name}] 🕵️ Auditing Candidate: {payload.get('description', 'Unknown')}")
        
        if self.truth_kernel and self.truth_kernel.enabled:
            # Generate Forensic Report Block
            forensic_data = self.truth_kernel.generate_forensic_report_block(payload)
            payload['forensic_analysis'] = forensic_data
            payload['verified'] = True
            
            # Archive verified finding
            self._save_record(payload)
            
            # Announce Verification
            await self.bus.publish(HiveEvent(
                type=EventType.VULN_CONFIRMED,
                source=self.name,
                payload=payload
            ))
        else:
            # Fallback for offline mode
            self._save_record(payload)

    async def archive_victory(self, event: HiveEvent):
        payload = event.payload
        # Determine if success
        status = payload.get("status")
        if status == "VULN_FOUND":
            print(f"[{self.name}] 📜 Archiving Vulnerability found by {event.source}")
            self._save_record(payload)
            
            # Emit Archive Log for Report
            await self.bus.publish(HiveEvent(
                type=EventType.LOG,
                source=self.name,
                payload=f"Vector {payload.get('payload', {}).get('type', 'logic_overflow')} stored in Hive Memory."
            ))

    def _save_record(self, record):
        try:
            with open(self.memory_file, "r+") as f:
                data = json.load(f)
                data.append(record)
                f.seek(0)
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[{self.name}] Memory Write Error: {e}")

    async def recall_tactics(self, query: str):
        # Simulating Semantic Search
        print(f"[{self.name}] Searching archives for: {query}")
        with open(self.memory_file, "r") as f:
            data = json.load(f)
        # Simple filter
        return [r for r in data if query in str(r)]
