import aiohttp
import asyncio
import json
from typing import Dict, Any, List
from backend.ai.gi5 import GI5Engine

# Initialize Brain
brain = GI5Engine()

class ChaosEngine:
    def __init__(self, target_url: str, method: str, headers: Dict[str, str], body: Any):
        self.target_url = target_url
        self.method = method
        self.headers = headers
        self.body = body # Can be dict or string
        self.concurrency = 5

    async def execute(self) -> List[Dict[str, Any]]:
        """
        Executes Advanced Business Logic Fuzzing.
        """
        results = []
        
        # Parse Body to Dict if needed
        payload_dict = {}
        if isinstance(self.body, str):
            try:
                payload_dict = json.loads(self.body)
            except:
                pass # Body is likely raw or empty
        elif isinstance(self.body, dict):
            payload_dict = self.body

        if not payload_dict:
            print("[-] ChaosEngine: No JSON body to fuzz. Skipping.")
            return []

        # 1. Semantic Analysis
        print(f"[*] ChaosEngine: Analyzing semantics for {self.target_url}...")
        semantics = brain.analyze_semantics(payload_dict)
        print(f"[+] Semantics Inferred: {semantics}")

        # 2. Generate Mutations
        mutations = brain.generate_chaos_mutations(payload_dict, semantics)
        if not mutations:
             print("[-] ChaosEngine: AI suggested no logic mutations.")
             return []

        print(f"[*] ChaosEngine: Testing {len(mutations)} logic variants...")

        # 3. Attack Loop
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            tasks = []
            for mut in mutations:
                tasks.append(self._test_mutation(session, mut))
            
            attack_results = await asyncio.gather(*tasks)
            results.extend(attack_results)

        return results

    async def _test_mutation(self, session, mutation):
        name = mutation.get('name', 'Unknown')
        payload = mutation.get('json', {})
        
        # Convert payload back to string
        data_str = json.dumps(payload)
        
        try:
            async with session.request(self.method, self.target_url, headers=self.headers, data=data_str) as resp:
                resp_text = await resp.text()
                status = resp.status
                
                # Logic Analysis
                verdict = "SECURE"
                
                # If we injected a privileged field (Mass Assignment) and got 200 OK, it's suspicious
                # If we sent a negative price and got 200 OK, it's suspicious
                if status >= 200 and status < 300:
                    verdict = "POTENTIAL_LOGIC_FLAW"
                    
                    # Deep Inspection by AI
                    # "Did the server actually accept the negative value?"
                    # For MVP, we flag 200s on heavy mutations as critical attention items
                
                # Check for stack traces (500s)
                if status == 500:
                    verdict = "SERVER_ERROR (DOS RISK)"

                return {
                    "variant": name,
                    "status": f"{status} {resp.reason}",
                    "verdict": verdict,
                    "payload": str(payload)[:50] + "..."
                }

        except Exception as e:
            return {"error": str(e)}
