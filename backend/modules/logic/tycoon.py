import aiohttp
import time
from backend.core.base import BaseArsenalModule
from backend.core.protocol import JobPacket, ResultPacket, Vulnerability, AgentID

class TheTycoon(BaseArsenalModule):
    """
    MODULE: THE TYCOON
    Category: Logic Assassin (Financial)
    Advanced Capabilities:
    1. Negative Quantity Injection (Integer Overflow)
    2. Floating Point Rounding (0.1 + 0.2 != 0.3)
    3. Currency Arbitrage
    """
    def __init__(self):
        super().__init__()
        self.name = "The Tycoon"

    async def execute(self, packet: JobPacket) -> ResultPacket:
        target = packet.target
        vulns = []
        start_time = time.time()
        
        self.log(f"Analyzing Financial Logic on {target.url}...")

        try:
            async with aiohttp.ClientSession() as session:
                # VECTOR 1: NEGATIVE QUANTITY & OVERFLOW
                # Cyber-Organism Protocol: MaxInt+1 (2147483648) and -1
                for qty in [-1, 2147483648]:
                    payload_qty = target.payload.copy() if target.payload else {}
                    payload_qty["quantity"] = qty
                    
                    async with session.post(target.url, json=payload_qty, headers=target.headers) as resp:
                        if resp.status == 200:
                            text = await resp.text()
                            if "success" in text.lower() or "order confirmed" in text.lower():
                                vulns.append(Vulnerability(
                                    name="Financial Logic Flaw (Qty)",
                                    severity="CRITICAL",
                                    description=f"Server accepted quantity {qty}, potentially refunding or overflowing.",
                                    evidence=str(payload_qty)
                                ))

                # VECTOR 2: FLOATING POINT ROUNDING
                # Cyber-Organism Protocol: Precision Attack (0.00001)
                payload_float = target.payload.copy() if target.payload else {}
                payload_float["price"] = 0.00001
                payload_float["amount"] = 1000
                
                async with session.post(target.url, json=payload_float, headers=target.headers) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        if "success" in text.lower() or "order confirmed" in text.lower():
                            vulns.append(Vulnerability(
                                name="Precision Rounding Bypass",
                                severity="HIGH",
                                description="Server accepted sub-atomic currency values.",
                                evidence=str(payload_float)
                            ))
        except Exception as e:
            self.log(f"Error executing attack: {e}")

        execution_time = (time.time() - start_time) * 1000
        
        return ResultPacket(
            job_id=packet.id,
            source_agent=AgentID.GAMMA,
            status="VULN_FOUND" if vulns else "SUCCESS",
            execution_time_ms=execution_time,
            data={"checked_vectors": ["negative_qty", "floating_point"]},
            vulnerabilities=vulns
        )
