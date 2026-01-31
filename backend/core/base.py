import asyncio
import logging
from abc import ABC, abstractmethod
from backend.core.protocol import JobPacket, ResultPacket, AgentStatus

class BaseAgent(ABC):
    """
    The Thinking Entity. 
    It has an Inbox (Queue) and an Outbox.
    """
    def __init__(self, name: str, event_bus):
        self.name = name
        self.bus = event_bus
        self.inbox = asyncio.Queue()
        self.status = AgentStatus.IDLE
        self.arsenal = {} # Loaded Modules

    async def start(self):
        logging.info(f"🤖 {self.name} Online.")
        while True:
            # Listen for tasks
            packet = await self.inbox.get()
            self.status = AgentStatus.WORKING
            
            try:
                await self.process(packet)
            except Exception as e:
                logging.error(f"💥 {self.name} Crashed: {e}")
            finally:
                self.status = AgentStatus.IDLE
                self.inbox.task_done()

    @abstractmethod
    async def process(self, packet: JobPacket):
        """The specific logic of the agent."""
        pass

class BaseArsenalModule(ABC):
    """
    The Weapon Template.
    """
    def __init__(self):
        self.name = "Unknown Module"
        self.description = "Generic Module"

    @abstractmethod
    async def execute(self, packet: JobPacket) -> ResultPacket:
        """
        Must return a ResultPacket.
        """
        pass
    
    def log(self, msg):
        logging.info(f"[{self.name}] {msg}")
