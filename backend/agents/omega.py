import asyncio
import random
from backend.core.hive import BaseAgent, EventType, HiveEvent
from backend.core.protocol import JobPacket, ResultPacket, AgentID, TaskPriority, ModuleConfig, TaskTarget

class OmegaAgent(BaseAgent):
    """
    AGENT OMEGA: THE STRATEGIST
    Advanced Capabilities:
    1. Nash Equilibrium Strategy (Randomized mixed strategies)
    2. Dynamic Campaign Chaining
    """
    def __init__(self, bus):
        super().__init__("agent_omega", bus)

    async def setup(self):
        # Listen for TARGET_ACQUIRED to start campaigns
        self.bus.subscribe(EventType.TARGET_ACQUIRED, self.handle_target)

    async def handle_target(self, event: HiveEvent):
        """
        Triggered when the system identifies a new target.
        """
        payload = event.payload
        target_url = payload.get("url")
        if target_url:
            await self.initiate_campaign(target_url)

    async def initiate_campaign(self, target_url: str):
        # 1. STRATEGY GENERATION (Nash Equilibrium + Context)
        
        # Cyber-Organism Protocol: E-Commerce Detection
        ecommerce_keywords = ["shop", "store", "buy", "cart", "checkout", "order"]
        is_ecommerce = any(k in target_url.lower() for k in ecommerce_keywords)
        
        if is_ecommerce:
            strategy = "E_COMMERCE_BLITZ"
            print(f"[{self.name}]: [E-COMMERCE] DETECTED. Deploying 'The Tycoon' & 'The Skipper'.")
        else:
            strategy = self._generate_mixed_strategy()
        
        await self.bus.publish(HiveEvent(
            type=EventType.LOG,
            source=self.name,
            payload={"message": f"👑 OMEGA: Initiating Campaign '{target_url}' with Strategy: {strategy}"}
        ))

        # 2. CAMPAIGN CHAINING
        target = TaskTarget(url=target_url)

        if strategy == "E_COMMERCE_BLITZ":
            # Specialized Packet for Tycoon (Financial)
            tycoon_packet = JobPacket(
                priority=TaskPriority.HIGH,
                target=target,
                config=ModuleConfig(
                    module_id="logic_tycoon", 
                    agent_id=AgentID.GAMMA,
                    aggression=8,
                    ai_mode=True
                )
            )
            # Specialized Packet for Skipper (Workflow)
            skipper_packet = JobPacket(
                 priority=TaskPriority.HIGH,
                 target=target,
                 config=ModuleConfig(
                     module_id="logic_skipper",
                     agent_id=AgentID.ALPHA,
                     aggression=7,
                     ai_mode=True
                 )
            )
            await self.dispatch_job(tycoon_packet)
            await self.dispatch_job(skipper_packet)
            
        else:
            # Standard Mixed Strategy flows...
            # Step A: Recon (Agent Alpha)
            recon_packet = JobPacket(
                priority=TaskPriority.HIGH,
                target=target,
                config=ModuleConfig(
                    module_id="logic_skipper", 
                    agent_id=AgentID.ALPHA,
                    aggression=5,
                    ai_mode=True
                )
            )
            await self.dispatch_job(recon_packet)
            
            # Step B: Logic Attack (Agent Gamma)
            logic_packet = JobPacket(
                priority=TaskPriority.NORMAL,
                target=target,
                config=ModuleConfig(
                    module_id="logic_tycoon", 
                    agent_id=AgentID.GAMMA,
                    aggression=8,
                    ai_mode=True
                )
            )
            await self.dispatch_job(logic_packet)

    async def dispatch_job(self, packet: JobPacket):
        # Convert Pydantic to Dict for JSON serialization in EventBus if needed
        # Or pass object if handlers handle it. HiveEvent payload is Dict.
        await self.bus.publish(HiveEvent(
            type=EventType.JOB_ASSIGNED,
            source=self.name,
            payload=packet.dict() # SERIALIZE FOR TRANSPORT
        ))

    def _generate_mixed_strategy(self):
        strategies = ["BLITZKRIEG", "LOW_AND_SLOW", "DECEPTION"]
        return random.choices(strategies, weights=[0.2, 0.5, 0.3], k=1)[0]
