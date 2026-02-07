from backend.core.base import BaseArsenalModule
from backend.core.protocol import JobPacket, ResultPacket, Vulnerability
import aiohttp
import time

class APIFuzzer(BaseArsenalModule):
    def __init__(self):
        super().__init__()
        self.name = "API Fuzzer"

    async def execute(self, packet: JobPacket) -> ResultPacket:
        start_time = time.time()
        vulnerabilities = []
        
        fuzz_vectors = [
            "A" * 10000, # Buffer Overflow attempt
            "%00",       # Null Byte
            "{{7*7}}",   # SSTI
            "../" * 10   # Path Traversal
        ]
        
        try:
             async with aiohttp.ClientSession() as session:
                for vector in fuzz_vectors:
                    # Append to URL path for simplicity
                    fuzzed_url = f"{packet.target.url}/{vector}"
                    try:
                         async with session.get(fuzzed_url) as response:
                            if response.status == 500:
                                vulnerabilities.append(Vulnerability(
                                    name="Unhandled Exception (Fuzzing)",
                                    severity="LOW",
                                    description="Server returned 500 Internal Server Error on malformed input.",
                                    evidence=f"Input: {vector}, Status: 500",
                                    remediation="Implement global error handling and input validation."
                                ))
                    except Exception:
                        pass
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
