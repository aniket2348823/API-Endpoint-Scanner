import aiohttp
import asyncio
from typing import Dict, Any, List
from backend.ai.gi5 import GI5Engine

# Initialize Brain
brain = GI5Engine()

class DoppelgangerEngine:
    def __init__(self, target_url: str, method: str, headers: Dict[str, str], body: str):
        self.target_url = target_url
        self.method = method
        self.headers = headers
        self.body = body
        self.concurrency = 10 # Lower default for IDOR to avoid bans

    async def execute(self) -> List[Dict[str, Any]]:
        """
        Executes the AI-Driven IDOR Attack.
        """
        results = []
        
        # 1. Analyze for IDs
        print(f"[*] Doppelganger: Scanning for IDs in {self.target_url}")
        id_info = brain.analyze_id_pattern(self.target_url, self.body)
        
        if not id_info.get('found'):
            print("[-] Doppelganger: No ID pattern found. Aborting.")
            return [{"error": "No ID parameter detected by GI-5"}]

        print(f"[+] GI-5 Identified ID Pattern: {id_info}")

        # 2. Generate Variants
        variants = brain.generate_idor_variants(id_info)
        if not variants:
            print("[-] Doppelganger: Failed to generate variants.")
            return [{"error": "GI-5 could not generate variants"}]

        print(f"[*] Testing {len(variants)} ID variants...")

        # 3. Attack (Async)
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            tasks = []
            for variant_id in variants:
                tasks.append(self._test_variant(session, id_info, variant_id))
            
            attack_results = await asyncio.gather(*tasks)
            results.extend(attack_results)

        return results

    async def _test_variant(self, session, id_info, variant_id):
        # Construct new URL/Body
        target_url = self.target_url
        target_body = self.body

        # Simple replacement logic (can be made robust with regex)
        # Assuming AI gave us the exact parameter value to replace
        original_val = id_info.get('value')
        
        if id_info.get('location') == 'URL_PATH' or id_info.get('location') == 'URL_QUERY':
             target_url = target_url.replace(original_val, str(variant_id))
        elif id_info.get('location') == 'BODY_JSON':
             target_body = target_body.replace(original_val, str(variant_id))

        try:
            async with session.request(self.method, target_url, headers=self.headers, data=target_body) as resp:
                resp_text = await resp.text()
                status = resp.status
                length = len(resp_text)
                
                # Check for Sensitivity
                sensitivity_tags = brain.analyze_sensitivity(resp_text)
                
                verdict = "SAFE"
                if status >= 200 and status < 300:
                    verdict = "POTENTIAL_IDOR"
                
                if sensitivity_tags:
                    verdict = "CRITICAL_LEAK"

                return {
                    "variant_id": variant_id,
                    "status": f"{status} {resp.reason}",
                    "length": length,
                    "verdict": verdict,
                    "data_leak": sensitivity_tags
                }
        except Exception as e:
            return {"error": str(e)}
