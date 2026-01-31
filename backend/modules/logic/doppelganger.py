import aiohttp
import difflib
from backend.core.base import BaseArsenalModule
from backend.core.protocol import JobPacket, ResultPacket, Vulnerability

class Doppelganger(BaseArsenalModule):
    """
    MODULE: DOPPELGANGER
    Logic: Insecure Direct Object Reference (IDOR).
    Cyber-Organism Protocol: Cosine Similarity Diffing.
    """
    async def execute(self, packet: JobPacket) -> ResultPacket:
        # Requires user_a_token and user_b_token in config
        # For this prototype, we assume they are passed in params or accessible
        # For simplicity, we assume target.headers has User A token, and we swap it.
        target = packet.target
        vulns = []
        
        user_a_token = target.headers.get("Authorization")
        if not user_a_token:
            return ResultPacket(job_id=packet.id, source_agent=packet.config.agent_id, status="FAILURE", execution_time_ms=0, data={"error": "No Auth Token"})

        # Simulated User B Token (In real app, this comes from Config)
        user_b_token = "Bearer MOCK_USER_B_TOKEN"
        
        async with aiohttp.ClientSession() as session:
            # 1. Baseline Request (User A requesting User A's resource)
            async with session.get(target.url, headers=target.headers) as resp:
                baseline_text = await resp.text()
            
            # 2. Attack Request (User B requesting User A's resource)
            headers_b = target.headers.copy()
            headers_b["Authorization"] = user_b_token
            
            async with session.get(target.url, headers=headers_b) as resp:
                attack_text = await resp.text()
                
                if resp.status == 200:
                    # Cyber-Organism Protocol: Diffing
                    # If Attack response is VERY similar to Baseline, it means User B saw exactly what User A sees.
                    ratio = difflib.SequenceMatcher(None, baseline_text, attack_text).ratio()
                    
                    if ratio > 0.95:
                         vulns.append(Vulnerability(
                             name="IDOR (Broken Access Control)",
                             severity="CRITICAL",
                             description=f"User B access confirmed. Similarity Score: {ratio*100:.2f}%",
                             evidence=f"Diff Ratio: {ratio}"
                         ))

        return ResultPacket(
            job_id=packet.id,
            source_agent=packet.config.agent_id,
            status="VULN_FOUND" if vulns else "SUCCESS",
            execution_time_ms=0,
            vulnerabilities=vulns
        )
