from backend.core.base import BaseArsenalModule
from backend.core.protocol import JobPacket, ResultPacket, Vulnerability
import aiohttp
import time

class AuthBypassTester(BaseArsenalModule):
    def __init__(self):
        super().__init__()
        self.name = "Auth Bypass Tester"

    async def execute(self, packet: JobPacket) -> ResultPacket:
        start_time = time.time()
        vulnerabilities = []
        
        # Attack Logic: Method Flipping / Header Stripping
        
        try:
             async with aiohttp.ClientSession() as session:
                # 1. Try accessing without any headers
                async with session.get(packet.target.url) as response:
                     if response.status == 200:
                         # We consider it a vuln if it's an admin/secure path
                         if "admin" in packet.target.url or "api/secure" in packet.target.url:
                             vulnerabilities.append(Vulnerability(
                                name="Broken Access Control (No Auth)",
                                severity="CRITICAL",
                                description="Secure endpoint accessible without credentials.",
                                evidence=f"GET {packet.target.url} returned 200 OK.",
                                remediation="Enforce authentication middleware on all secure routes."
                            ))
        except Exception:
            pass

        return ResultPacket(
            job_id=packet.id if hasattr(packet, 'id') else "unknown",
            source_agent=packet.config.agent_id,
            status="VULN_FOUND" if vulnerabilities else "SUCCESS",
            execution_time_ms=(time.time() - start_time) * 1000,
            data={},
            vulnerabilities=vulnerabilities
        )
