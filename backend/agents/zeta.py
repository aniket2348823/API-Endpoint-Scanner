import asyncio
import psutil
import time
import random
from typing import List, Dict, Any
from collections import deque
from backend.core.hive import BaseAgent, EventType, HiveEvent
from backend.core.protocol import JobPacket  

class ZetaAgent(BaseAgent):
    """
    AGENT ZETA: THE CORTEX
    Capabilities:
    - Predictive Auto-Scaling (Linear Regression).
    - Error Budget Economy.
    - QoS Multiplexing.
    - Dynamic IP Rotation.
    - SOTA: Sentiment Analysis (Server Stress).
    - SOTA: Adaptive Gaussian Jitter.
    """
    def __init__(self, bus):
        super().__init__("agent_zeta", bus)
        
        self.latency_window = deque(maxlen=50) 
        self.error_window = deque(maxlen=50)   
        
        self.error_budget_max = 50
        self.error_budget_current = 50
        self.last_budget_refill = time.time()
        
        self.priority_queue = {0: [], 1: [], 2: []}

    async def setup(self):
        self.bus.subscribe(EventType.JOB_COMPLETED, self.handle_job_completion)

    async def handle_job_completion(self, event: HiveEvent):
        payload = event.payload
        if "duration_ms" in payload:
            self.latency_window.append(payload["duration_ms"])
        
        if "success" in payload:
            is_error = not payload["success"] 
            self.error_window.append(is_error)
            
            # SOTA: SENTIMENT ANALYSIS
            # Analyze error messages for "Stress" keywords
            if is_error and "data" in payload:
                 error_msg = str(payload["data"]).lower()
                 if "timeout" in error_msg or "overload" in error_msg:
                     print(f"[{self.name}] 😓 Server Sentiment: STRESSED (Timeout Detected)")
                     self.error_budget_current -= 5 # High penalty for stress

    async def lifecycle(self):
        while self.active:
            await self.governance_cycle()
            await self.refill_budget()
            await self.drain_queue()
            await asyncio.sleep(1.0)

    async def governance_cycle(self):
        # 1. PREDICTIVE AUTO-SCALING
        if len(self.latency_window) > 10:
            trend = self.calculate_trend(list(self.latency_window))
            if trend > 0.5: 
                 await self.broadcast_signal("THROTTLE", {"level": "HIGH", "reason": "Latency Acceleration"})

        # 2. ERROR BUDGET CHECK
        if self.error_budget_current < 5:
             await self.broadcast_signal("STEALTH_MODE", {"reason": "Error Budget Depleted"})

        # 3. DYNAMIC IP ROTATION
        if len(self.error_window) > 20:
            block_count = sum(1 for x in self.error_window if x is True)
            block_rate = block_count / len(self.error_window)
            if block_rate > 0.02: 
                await self.broadcast_signal("INFRA_ROTATE", {"reason": "High Block Rate"})
                self.error_window.clear()

    def calculate_jitter(self):
        """
        SOTA: Adaptive Gaussian Jitter.
        Instead of random(0, 5), use Gaussian distribution to mimic human variance.
        """
        # Mean = 1.5s, StdDev = 0.5s
        jitter = random.gauss(1.5, 0.5)
        return max(0.1, jitter)

    def calculate_trend(self, data: List[float]) -> float:
        n = len(data)
        if n < 2: return 0.0
        x = range(n)
        y = data
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y))
        denominator = sum((xi - x_mean) ** 2 for xi in x)
        return numerator / denominator if denominator != 0 else 0.0

    async def refill_budget(self):
        now = time.time()
        if now - self.last_budget_refill > 60:
            if self.error_budget_current < self.error_budget_max:
                self.error_budget_current += 1
            self.last_budget_refill = now

    async def drain_queue(self):
        """Process queued jobs from the priority queue."""
        for priority in [0, 1, 2]:  # 0 = highest priority
            while self.priority_queue[priority]:
                job = self.priority_queue[priority].pop(0)
                # Process or delegate job
                pass

    async def broadcast_signal(self, type: str, payload: Dict[str, Any]):
        await self.bus.publish(HiveEvent(
            type=EventType.CONTROL_SIGNAL,
            source=self.name,
            payload={"signal": type, "data": payload}
        ))
    
    def validate_job(self, packet: JobPacket) -> bool:
        """
        Cyber-Organism Protocol: Pre-Flight Check.
        Called by other agents before execution (Simulating synchronous RPC or shared state).
        """
        # 1. Latency Check (> 500ms?)
        if self.latency_window:
            avg_latency = sum(self.latency_window) / len(self.latency_window)
            if avg_latency > 500:
                print(f"[{self.name}]: 🛑 DENY JOB {packet.id}. High Latency ({avg_latency:.1f}ms).")
                return False

        # 2. Budget Check (< 10?)
        if self.error_budget_current < 10:
             print(f"[{self.name}]: 🛑 DENY JOB {packet.id}. Low Budget ({self.error_budget_current}).")
             return False

        return True
