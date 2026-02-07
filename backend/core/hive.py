import asyncio
import logging
from typing import Callable, Dict, List, Any, Awaitable
from pydantic import BaseModel, Field
from enum import Enum
import uuid
from datetime import datetime

# --- 1. THE VOCABULARY (Strict Schemas) ---

class EventType(str, Enum):
    SYSTEM_START = "SYSTEM_START"
    LOG = "LOG"
    TARGET_ACQUIRED = "TARGET_ACQUIRED"
    VULN_CANDIDATE = "VULN_CANDIDATE"
    VULN_CONFIRMED = "VULN_CONFIRMED"
    AGENT_STATUS = "AGENT_STATUS"
    JOB_ASSIGNED = "JOB_ASSIGNED"
    JOB_COMPLETED = "JOB_COMPLETED"
    CONTROL_SIGNAL = "CONTROL_SIGNAL"

class HiveEvent(BaseModel):
    """
    The fundamental unit of communication.
    Every whisper in the hive must follow this structure.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    type: EventType
    source: str  # The Agent Name
    payload: Dict[str, Any] = {}

# --- 2. THE NERVOUS SYSTEM (Event Bus) ---

class EventBus:
    """
    The central message broker. 
    Decouples agents so they never talk directly.
    """
    def __init__(self):
        self.subscribers: Dict[EventType, List[Callable[[HiveEvent], Awaitable[None]]]] = {}
        self.history: List[HiveEvent] = [] # Optional: For replay/debugging

    def subscribe(self, event_type: EventType, handler: Callable[[HiveEvent], Awaitable[None]]):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
        # logging.debug(f"🔌 Handler subscribed to {event_type}")

    async def publish(self, event: HiveEvent):
        """
        Broadcasts an event to all interested agents.
        Fire-and-forget: Tasks are spawned immediately.
        """
        # logging.info(f"📢 [{event.source}] published {event.type}") # Verbose logging
        
        if event.type in self.subscribers:
            handlers = self.subscribers[event.type]
            for handler in handlers:
                # CRITICAL FIX: Use create_task so one slow agent doesn't block the bus
                asyncio.create_task(self._safe_execute(handler, event))

    async def _safe_execute(self, handler, event):
        try:
            await handler(event)
        except Exception as e:
            logging.error(f"[CRITICAL] Handler failed processing {event.type}: {e}")

# --- 3. THE DNA (Base Agent) ---

class BaseAgent:
    """
    The template for all Hive Agents.
    Enforces a standard lifecycle: Wake -> Think -> Act.
    """
    def __init__(self, name: str, bus: EventBus):
        self.name = name
        self.bus = bus
        self.active = False
        self.status = "IDLE"

    async def start(self):
        """Wakes the agent up."""
        self.active = True
        self.status = "ACTIVE"
        logging.info(f"🤖 {self.name} is ONLINE.")
        
        # Subscribe to relevant events
        await self.setup()
        
        # Announce presence
        await self.bus.publish(HiveEvent(
            type=EventType.AGENT_STATUS,
            source=self.name,
            payload={"status": "ONLINE"}
        ))

        # Start the internal thinking loop (if needed)
        asyncio.create_task(self.lifecycle())

    async def stop(self):
        """Puts the agent to sleep."""
        self.active = False
        self.status = "OFFLINE"
        logging.info(f"💤 {self.name} is OFFLINE.")

    # --- ABSTRACT METHODS (Subclasses MUST implement these) ---

    async def setup(self):
        """Register subscriptions here."""
        pass

    async def lifecycle(self):
        """
        The Agent's internal 'Heartbeat'. 
        Some agents react (Event-driven), others act (Loop-driven).
        """
        pass

    async def think(self, context: Any):
        """
        The AI Integration Slot.
        Override this with specific logic (LLM, Heuristic, etc).
        """
        pass

    async def execute_task(self, packet):
        """
        Synchronous task execution for Defense API.
        Subclasses (Theta, Iota) should override this.
        """
        from backend.core.protocol import ResultPacket, Vulnerability
        
        # Default implementation - subclasses should override
        return ResultPacket(
            job_id=packet.id if hasattr(packet, 'id') else "unknown",
            source_agent=self.name,
            status="SAFE",
            vulnerabilities=[],
            execution_time_ms=0,
            data={}
        )
