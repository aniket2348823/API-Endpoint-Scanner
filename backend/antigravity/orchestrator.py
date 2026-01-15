import asyncio
import time
import uuid
import re
from urllib.parse import urlparse, urljoin
from concurrent.futures import ProcessPoolExecutor

from .transport import TransportLayer
from .discovery import DiscoveryEngine
from .analysis import Soft404Detector, PIIScanner, MassAssignmentDetector, SQLInjectionDetector, XSSDetector, BayesianClassifier
from .context import ContextEngine
from .exploitation import Chronomancer, Doppelganger, DynamicWAFMutator, ProtocolDesyncDetector
from .stateful_logic import StatefulLogicExplorer

class ScanOrchestrator:
    def __init__(self, target_url, on_log=None, on_finding=None):
        self.target = target_url
        self.domain = urlparse(target_url).netloc
        self.transport = TransportLayer()
        self.discovery = None 
        
        # Analysis Modules
        self.soft404 = Soft404Detector()
        self.pii_scanner = PIIScanner()
        self.mass_assignment = MassAssignmentDetector()
        self.sqli_detector = SQLInjectionDetector()
        self.xss_detector = XSSDetector()
        self.context_engine = ContextEngine()
        self.bayesian = BayesianClassifier()
        
        # Singularity/Omniscient Modules
        self.chronomancer = Chronomancer()
        self.doppelganger = Doppelganger(high_priv_token="initial_token_placeholder") 
        self.mutator = DynamicWAFMutator(self.bayesian)
        self.desync_detector = ProtocolDesyncDetector()
        self.stateful_explorer = None # Init after session

        self.queue = asyncio.Queue()
        self.visited = set()
        self.findings = []
        self.logs = []
        self.running = False
        
        self.on_log = on_log
        self.on_finding = on_finding
        
        # Reactor Pattern: Executor for CPU-bound tasks
        self.executor = ProcessPoolExecutor(max_workers=4)

    def log(self, msg):
        self.logs.append(msg)
        if self.on_log:
            self.on_log(msg)

    def _add_finding(self, finding):
        # Enforce strict JSON Schema structure where possible, but keep retro-compatibility keys if needed
        # The prompt asks for: {"Type":..., "Endpoint":..., "Severity":..., "Evidence":...}
        safe_finding = {
            "Type": finding.get("Type", finding.get("name", finding.get("type", "Unknown"))),
            "Endpoint": finding.get("Endpoint", finding.get("url", finding.get("endpoint", "Unknown"))),
            "Severity": finding.get("Severity", finding.get("severity", "Info")),
            "Evidence": finding.get("Evidence", finding.get("description", finding.get("evidence", "No evidence detected")))
        }
        
        self.findings.append(safe_finding)
        if self.on_finding:
            self.on_finding(safe_finding)

    async def run_scan(self):
        self.running = True
        self.log(f"Starting Antigravity Omniscient Sovereign Scan on {self.target}")
        await self.transport.start()
        self.discovery = DiscoveryEngine(self.transport.session)
        self.stateful_explorer = StatefulLogicExplorer(self.transport.session)
        
        try:
            # 1. Calibrate Soft 404 (Phase 3)
            self.log("Phase 3: Signal Processing Calibration...")
            random_guid = str(uuid.uuid4())
            error_url = urljoin(self.target, f"/api/v1/{random_guid}")
            
            resp = await self.transport.safe_request('GET', error_url)
            if resp and resp['status'] == 200:
                self.soft404.calibrate(resp['text'])
                self.log(f"Soft 404 Baseline established.")
            else:
                 self.log(f"Soft 404 Calibration note: {resp['status'] if resp else 'None'} returned for nonce.")

            # 2. Add Target to Queue
            await self.queue.put(self.target)
            
            # 3. Phase 1: Passive Intelligence (Wayback Mining)
            self.log("Phase 1: Passive Intelligence (Wayback Mining)...")
            wayback_items = await self.discovery.fetch_wayback_urls(self.target)
            self.log(f"Found {len(wayback_items)} historical endpoints.")
            for item in wayback_items:
                url = item['url']
                if url not in self.visited:
                    await self.queue.put(url)
            
            # 4. Phase 2: Contextual Discovery
            self.log("Phase 2: Contextual Discovery...")
            landing_resp = await self.transport.safe_request('GET', self.target)
            if landing_resp and landing_resp['status'] == 200:
                wordlist = self.context_engine.generate_wordlist(landing_resp['text'])
                self.log(f"Generated Context Wordlist: {wordlist[:5]}...")
                for word in wordlist:
                    api_patterns = [f"/api/{word}", f"/v1/{word}", f"/api/v1/{word}"]
                    for pat in api_patterns:
                        fuzz_url = urljoin(self.target, pat)
                        if fuzz_url not in self.visited:
                            await self.queue.put(fuzz_url)

            # --- Omniscient Upgrade: Phase 4 (Stateful Logic) ---
            self.log("Phase 4: Stateful Logic Exploration...")
            flow_findings = await self.stateful_explorer.explore_flow(self.target)
            for ff in flow_findings:
                self._add_finding(ff)
                # Add discovered flow endpoints to queue
                if ff['Endpoint'] not in self.visited:
                    await self.queue.put(ff['Endpoint'])

            # 5. Start Workers
            num_workers = 10
            workers = [asyncio.create_task(self.worker(f"Worker-{i}")) for i in range(num_workers)]
            
            await self.queue.join()
            
            for w in workers:
                w.cancel()
                
        except Exception as e:
            self.log(f"Critical Scan Error: {e}")
        finally:
            await self.transport.close()
            self.executor.shutdown(wait=False)
            self.running = False
            self.log("Scan Completed.")
            
        return {
            "target": self.target,
            "findings": self.findings,
            "logs": self.logs
        }

    async def worker(self, name):
        loop = asyncio.get_running_loop()
        while True:
            try:
                url = await self.queue.get()
                if url in self.visited:
                    self.queue.task_done()
                    continue
                
                self.visited.add(url)
                
                if urlparse(url).netloc != self.domain:
                    self.queue.task_done()
                    continue

                # Fetch (Reactor)
                resp = await self.transport.safe_request('GET', url)
                if not resp:
                    self.queue.task_done()
                    continue
                
                # --- Omniscient Upgrade: Adversarial Payload Mutation (WAF Evasion) ---
                if resp['status'] == 403:
                    self.log(f"[{name}] WAF Block detected (403). Initiating Dynamic WAF Evolution...")
                    
                    # Recursive Mutation Loop (v30.0)
                    bypass_result = await self.mutator.mutate_until_bypass(url, self.transport.session, self.executor)
                    
                    if bypass_result['status'] == 'Bypassed':
                        self._add_finding({
                            "Type": "WAF Evasion (Dynamic Evolution)",
                            "Endpoint": url,
                            "Severity": "Critical",
                            "Evidence": f"Bypassed WAF after {bypass_result['attempts']} mutations. Payload: {bypass_result['payload']}"
                        })

                # --- Aether Upgrade: Protocol Desynchronization ---
                if 'api' in url:
                    desync_hit = await self.desync_detector.check_desync(url, self.transport.session)
                    if desync_hit:
                        self._add_finding(desync_hit)
                
                # Phase 3: Soft 404 Filter
                if resp['status'] == 200:
                    is_soft = await loop.run_in_executor(
                        self.executor, 
                        self.soft404.is_soft_404, 
                        resp['text']
                    )
                    if is_soft:
                        self.queue.task_done()
                        continue
                
                self.log(f"[{name}] Analyzing: {url} ({resp['status']})")

                # Phase 1: Deep JS Mining
                if url.endswith('.js') or 'javascript' in resp.get('headers', {}).get('Content-Type', ''):
                    js_findings = await self.discovery.deep_mine_js(url, resp['text'])
                    for jf in js_findings:
                        if jf['type'] == 'Discovered Endpoint':
                            if jf['evidence'] not in self.visited:
                                await self.queue.put(jf['evidence'])
                        else:
                             self._add_finding(jf)
                
                # Phase 1.5: HTML Spidering (Basic)
                if 'text/html' in resp.get('headers', {}).get('Content-Type', ''):
                    # Simple regex for finding hrefs to avoid bs4 overhead in async loop, or use bs4 if preferred
                    # Using regex for speed and simplicity in this demo context
                    hrefs = re.findall(r'href=[\'"]?([^\'" >]+)', resp['text'])
                    for href in hrefs:
                        full_url = urljoin(url, href)
                        # Only follow same-domain links
                        if urlparse(full_url).netloc == self.domain:
                            if full_url not in self.visited:
                                await self.queue.put(full_url)


                # Phase 4 / Phase 3 Singularity Exploitation
                
                # A. Mass Assignment
                if resp['status'] == 200 and ('json' in resp.get('headers', {}).get('Content-Type', '') or '/api/' in url):
                     fuzz_url = f"{url}{'&' if '?' in url else '?'}admin=true&role=admin"
                     fuzz_resp = await self.transport.safe_request('GET', fuzz_url)
                     if fuzz_resp:
                         ma_hits = await loop.run_in_executor(
                             self.executor,
                             self.mass_assignment.check,
                             resp, fuzz_resp, url
                         )
                         for hit in ma_hits:
                             self._add_finding(hit)
                     
                     # Chronomancer
                     if 'coupon' in url or 'transfer' in url or 'order' in url or 'gift' in url:
                         payload = {"claim": True}
                         race_hit = await self.chronomancer.execute_race_condition(
                             url, self.transport.session, payload
                         )
                         if race_hit:
                             self._add_finding(race_hit)

                # B. SQL Injection
                sqli_payload = "' OR 1=1 --"
                sqli_url = f"{url}{'&' if '?' in url else '?'}q={sqli_payload}"
                sqli_resp = await self.transport.safe_request('GET', sqli_url)
                if sqli_resp:
                    sqli_hits = await loop.run_in_executor(
                        self.executor,
                        self.sqli_detector.check,
                        sqli_resp['text'], url, sqli_payload
                    )
                    for hit in sqli_hits:
                        self._add_finding(hit)

                # C. XSS
                xss_payload = '"><script>confirm(1337)</script>'
                xss_url = f"{url}{'&' if '?' in url else '?'}q={xss_payload}"
                xss_resp = await self.transport.safe_request('GET', xss_url)
                if xss_resp:
                    xss_hits = self.xss_detector.check(xss_resp['text'], url, payload=xss_payload)
                    for hit in xss_hits:
                        self._add_finding(hit)

                # D. IDOR / Doppelganger
                idor_match = re.search(r'/(\d+)(?:/|$)', urlparse(url).path)
                if idor_match:
                     original_id = int(idor_match.group(1))
                     if original_id > 0:
                        target_id = original_id - 1
                        idor_url = url.replace(f"/{original_id}", f"/{target_id}")
                        idor_resp = await self.transport.safe_request('GET', idor_url)
                        if idor_resp and idor_resp['status'] == 200 and not await loop.run_in_executor(self.executor, self.soft404.is_soft_404, idor_resp['text']):
                             self._add_finding({
                                 "Type": "Horizontal Privilege Escalation (IDOR)",
                                 "Endpoint": idor_url,
                                 "Severity": "HIGH",
                                 "Evidence": f"Retrieved data for ID {target_id}"
                             })

                # E. PII Leak
                pii_hits = await loop.run_in_executor(
                    self.executor,
                    self.pii_scanner.scan_content,
                    resp['text'], url
                )
                for hit in pii_hits:
                    self._add_finding(hit)

            except Exception as e:
                pass
            finally:
                self.queue.task_done()
