import asyncio
import logging
import uuid
from typing import Dict, Any, Optional
from pydantic import BaseModel
from enum import Enum
from backend.core.hive import BaseAgent, EventBus

# --- 1. THE LANGUAGE OF NEGOTIATION ---

class ResourceType(str, Enum):
    NETWORK = "NETWORK"   # Sending HTTP requests
    CPU = "CPU"           # Heavy AI math (Embeddings, Diffing)
    DISK = "DISK"         # Writing reports / vector DB

class Bid(BaseModel):
    id: str = str(uuid.uuid4())
    agent_id: str
    resource: ResourceType
    priority: float       # 0.0 to 1.0 (1.0 = CRITICAL)
    reason: str

class Grant(BaseModel):
    bid_id: str
    approved: bool
    token: str            # A security token to prove permission

# --- 2. THE JUDGE (Conflict Resolution) ---

class NeuroNegotiator:
    """
    The AI Judge. 
    It prevents the Scout from DDOSing the target while the Breaker works.
    """
    def __init__(self):
        self._network_lock = asyncio.Lock()
        self._cpu_semaphore = asyncio.Semaphore(2) # Allow 2 concurrent CPU tasks
        self.active_bids: Dict[str, Bid] = {}

    async def request_access(self, bid: Bid) -> bool:
        """
        Agents call this to ask for permission.
        """
        # logging.debug(f"⚖️ JUDGE: Evaluating bid from {bid.agent_id} for {bid.resource} (Prio: {bid.priority})")
        
        # AI DECISION LOGIC (Simplified Game Theory)
        
        if bid.resource == ResourceType.NETWORK:
            # If priority is HIGH (>0.8), we might force-wait others
            # For this MVP, we use a simple lock check + priority gate
            if self._network_lock.locked():
                 # Valid "Budge" logic would go here (preemption)
                 return False 
            return True

        elif bid.resource == ResourceType.CPU:
             if self._cpu_semaphore.locked():
                 return False
             return True

        return True

# --- 3. THE SMART AGENT (Deeply Integrated) ---

class HyperAgent(BaseAgent):
    """
    The Base Class for AI-Integrated Agents (V4).
     Inherits from V3 BaseAgent for EventBus, adds Negotiation.
    """
    def __init__(self, name: str, bus: EventBus, negotiator: NeuroNegotiator):
        super().__init__(name, bus)
        self.negotiator = negotiator
        self.memory = [] # Local Short-Term Memory

    async def act_smart(self, action_name: str, resource: ResourceType, priority: float, func):
        """
        The wrapper that enforces Negotiation.
        """
        bid = Bid(agent_id=self.name, resource=resource, priority=priority, reason=action_name)
        
        # 1. NEGOTIATE
        approved = await self.negotiator.request_access(bid)
        
        if approved:
            try:
                # 2. EXECUTE
                # Ideally we acquire the lock here.
                # For MVP, we assume approval = lock grant for atomic ops
                if resource == ResourceType.NETWORK:
                     async with self.negotiator._network_lock:
                         return await func()
                elif resource == ResourceType.CPU:
                     async with self.negotiator._cpu_semaphore:
                         return await func()
                else:
                     return await func()
            except Exception as e:
                logging.error(f"{self.name} failed: {e}")
        else:
            # 3. ADAPT (AI Backoff)
            # logging.info(f"⏳ {self.name} yielded (Conflict Avoidance).")
            await asyncio.sleep(0.5) # Smart wait
            return None
