import asyncio
import aiohttp
import time
from backend.core.base import BaseArsenalModule
from backend.core.protocol import JobPacket, ResultPacket, Vulnerability

class Chronomancer(BaseArsenalModule):
    """
    MODULE: CHRONOMANCER
    Logic: Race Conditions (Concurrency Exploitation).
    Cyber-Organism Protocol: Gate Synchronization (Single Packet Flood).
    """
    async def execute(self, packet: JobPacket) -> ResultPacket:
        target = packet.target
        vulns = []
        
        # Cyber-Organism Protocol: 20 Parallel Connections
        connections = 20
        gate = asyncio.Event()
        
        async def single_racer(session, idx):
            # Wait for the gate to open (Synchronized Launch)
            await gate.wait()
            
            start_t = time.perf_counter()
            try:
                # We send the request immediately upon gate open
                # In a lower-level implementation, we'd send headers first, wait, then body.
                # For `aiohttp`, we simulate by gathering execution exactly here.
                async with session.post(target.url, json=target.payload, headers=target.headers) as resp:
                     await resp.read() # Read body to complete request
                     return resp.status, time.perf_counter() - start_t
            except Exception as e:
                return 500, 0

        async with aiohttp.ClientSession() as session:
            tasks = [single_racer(session, i) for i in range(connections)]
            
            # Open the gate!
            # Give tasks a moment to hit the .wait() line
            await asyncio.sleep(0.1) 
            gate.set()
            
            results = await asyncio.gather(*tasks)
            
            # Analysis: Did we get multiple successes?
            success_count = sum(1 for status, _ in results if status == 200)
            
            # If target logic was "Redeem Coupon", and we got 20 successes...
            if success_count > 1:
                vulns.append(Vulnerability(
                    name="Race Condition (Gate Sync)",
                    severity="HIGH",
                    description=f"Executed {connections} requests. {success_count} succeeded simultaneously.",
                    evidence=f"Success Rate: {success_count}/{connections}"
                ))

        return ResultPacket(
            job_id=packet.id,
            source_agent=packet.config.agent_id,
            status="VULN_FOUND" if vulns else "SUCCESS",
            execution_time_ms=0,
            vulnerabilities=vulns
        )
