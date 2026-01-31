import aiohttp
from backend.core.base import BaseArsenalModule
from backend.core.protocol import JobPacket, ResultPacket, Vulnerability, AgentID

class TheSkipper(BaseArsenalModule):
    """
    MODULE: THE SKIPPER
    Logic: Workflow Bypass (State Machine Violation).
    Cyber-Organism Protocol: Step Jumping & Referer Spoofing.
    """
    async def execute(self, packet: JobPacket) -> ResultPacket:
        # Expecting workflow_steps in params, e.g., ["/cart", "/checkout", "/payment", "/success"]
        # If not provided, assumption is we skip to /success
        target = packet.target
        vulns = []
        
        # Determine success endpoint
        success_url = target.url # Assuming the target passed IS the success endpoint or checks against it
        if "success" not in success_url and "confirm" not in success_url:
            # Fallback deduction or use params
            pass 
            
        async with aiohttp.ClientSession() as session:
            # 1. Step Jumping (Direct Access)
            async with session.get(success_url, headers=target.headers) as resp:
                if resp.status == 200:
                    vulns.append(Vulnerability(
                        name="Workflow Bypass (Direct Access)", 
                        severity="HIGH", 
                        description="Accessed final step directly.",
                        evidence="Direct Access Successful"
                    ))
                
                # 2. Header Spoofing (Referer)
                elif resp.status == 403 or resp.status == 302:
                    # Retry with Referer
                    headers_spoof = target.headers.copy()
                    headers_spoof["Referer"] = target.url.replace("success", "payment") # Mock previous step
                    
                    async with session.get(success_url, headers=headers_spoof) as resp_spoof:
                        if resp_spoof.status == 200:
                             vulns.append(Vulnerability(
                                 name="Workflow Bypass (Referer Spoofing)", 
                                 severity="CRITICAL", 
                                 description="Accessed final step by spoofing Referer header.",
                                 evidence=f"Referer: {headers_spoof['Referer']}"
                             ))

        return ResultPacket(
            job_id=packet.id,
            source_agent=packet.config.agent_id,
            status="VULN_FOUND" if vulns else "SUCCESS",
            execution_time_ms=0,
            vulnerabilities=vulns,
            data={"victorious_sequence": [target.url, success_url]} if vulns else {}
        )
