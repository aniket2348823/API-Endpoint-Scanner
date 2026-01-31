import socket
import time
import ssl
import asyncio
import numpy as np
from urllib.parse import urlparse
from backend.ai.gi5 import GI5Engine
from typing import List, Dict, Any

# Initialize Brain
brain = GI5Engine()

class ChronomancerEngine:
    def __init__(self, target_url, method, headers, body, concurrency=50):
        self.target_url = target_url
        self.method = method
        self.headers = headers
        self.body = body
        self.concurrency = min(concurrency, 60) # Win Limit Safety
        
        self.parsed_url = urlparse(target_url)
        self.host = self.parsed_url.hostname
        self.port = self.parsed_url.port or (443 if self.parsed_url.scheme == 'https' else 80)
        self.sockets = []

    def _construct_payload(self) -> bytes:
        """Constructs RAW HTTP Request."""
        path = self.parsed_url.path or "/"
        if self.parsed_url.query:
            path += f"?{self.parsed_url.query}"
        
        request = f"{self.method} {path} HTTP/1.1\r\n"
        for k, v in self.headers.items():
            request += f"{k}: {v}\r\n"
        
        if "Host" not in self.headers:
            request += f"Host: {self.host}\r\n"
        if "Content-Length" not in self.headers and self.body:
            request += f"Content-Length: {len(self.body)}\r\n"
            
        request += "\r\n"
        if self.body:
            request += self.body
            
        return request.encode('utf-8')

    def _calibrate_predictive_jitter(self) -> float:
        """
        NEUROMANCER PROTOCOL:
        Uses Statistical Analysis (Mean + StdDev + Z-Score) to predict optimal jitter.
        """
        latencies = []
        
        # 1. Fire Probes
        for _ in range(10):
            try:
                start = time.perf_counter()
                s = socket.create_connection((self.host, self.port), timeout=2)
                if self.parsed_url.scheme == 'https':
                    context = ssl.create_default_context()
                    s = context.wrap_socket(s, server_hostname=self.host)
                s.close()
                end = time.perf_counter()
                latencies.append(end - start)
            except:
                pass
        
        if not latencies:
            return 0.05 # Conservative Fallback
            
        # 2. NumPy Analysis
        arr = np.array(latencies)
        
        # 3. Z-Score Outlier Rejection
        mean = np.mean(arr)
        std = np.std(arr)
        
        if std > 0:
            z_scores = np.abs((arr - mean) / std)
            clean_arr = arr[z_scores < 2] # Keep only data within 2 sigmas
        else:
            clean_arr = arr
            
        if len(clean_arr) == 0: clean_arr = arr
        
        final_mean = np.mean(clean_arr)
        final_std = np.std(clean_arr)
        
        # 4. Target Calculation: Mean + 1.5 * StdDev
        # We want to wait until the "tail" of the network distribution to sync close to server processing
        target_jitter = final_mean + (1.5 * final_std)
        
        # Cap limits for sanity
        target_jitter = max(0.01, min(target_jitter, 2.0))
        
        print(f"[+] Chronomancer: Latency u={final_mean*1000:.2f}ms o={final_std*1000:.2f}ms -> Jitter={target_jitter*1000:.2f}ms")
        return target_jitter

    def execute(self) -> List[Dict[str, Any]]:
        """
        Executes the Timed Race Attack.
        """
        full_payload = self._construct_payload()
        
        # Last-Byte Split
        if len(full_payload) > 1:
            prime_payload = full_payload[:-1]
            fire_payload = full_payload[-1:]
        else:
            prime_payload = full_payload
            fire_payload = b""

        results = []

        try:
            # 1. PREDICT JITTER
            jitter = self._calibrate_predictive_jitter()

            # 2. OPEN SOCKETS (The Wormhole)
            open_success = 0
            for i in range(self.concurrency):
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    
                    if self.parsed_url.scheme == 'https':
                        context = ssl.create_default_context()
                        s = context.wrap_socket(s, server_hostname=self.host)
                    
                    s.settimeout(2.0)
                    s.connect((self.host, self.port))
                    if prime_payload:
                        s.sendall(prime_payload)
                    self.sockets.append(s)
                    open_success += 1
                except Exception as e:
                    # Silent fail on individual sockets to keep speed up
                    pass

            if not self.sockets:
                return [{"error": "Failed to establish sockets via Chronomancer."}]

            # 3. THE WAIT (Sync Phase)
            time.sleep(jitter)

            # 4. FIRE (Flux Phase)
            # This loop must be tight. No print statements inside.
            for s in self.sockets:
                try:
                    s.send(fire_payload)
                except:
                    pass

            # 5. READ & ANALYZE
            # Differential Analysis: Detect if any response differs from the majority
            raw_responses = []
            
            for i, s in enumerate(self.sockets):
                try:
                    s.settimeout(2.0)
                    response = s.recv(4096).decode('utf-8', errors='ignore')
                    status_line = response.split('\r\n')[0] if response else "No Response"
                    
                    sensitivity = []
                    if response:
                        sensitivity = brain.analyze_sensitivity(response)
                    
                    result_obj = {
                        "socket_id": i, 
                        "status": status_line,
                        "data_leak": sensitivity,
                        "length": len(response)
                    }
                    results.append(result_obj)
                    raw_responses.append(result_obj)
                    
                except Exception as e:
                    results.append({"socket_id": i, "status": "Timeout/Error"})
                finally:
                    s.close()
                    
            self.sockets = [] # Cleanup
            
            # DIFFERENTIAL ANALYSIS LOGIC
            # If 49 requests are "Length 500" and 1 is "Length 5000", that 1 is the exploit.
            # We flag it.
            lengths = [r.get('length', 0) for r in raw_responses if isinstance(r, dict)]
            if lengths:
                avg_len = np.mean(lengths)
                std_len = np.std(lengths)
                
                if std_len > 0:
                    for r in raw_responses:
                        l = r.get('length', 0)
                        if abs(l - avg_len) > (3 * std_len):
                            # This is a statistical anomaly -> Potential Race Win
                            r['verdict'] = "VULNERABLE (RACE ANOMALY)"
                            if not r.get('data_leak'):
                                r['data_leak'] = ["ANOMALY_DETECTED"]

        except Exception as e:
            return [{"error": str(e)}]
        
        return results
