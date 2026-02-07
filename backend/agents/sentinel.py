# FILE: backend/agents/sentinel.py
# IDENTITY: AGENT THETA (THE SENTINEL)
# MISSION: Passive DOM Analysis & Prompt Injection Defense.

import re
import asyncio
from typing import Dict, List, Any
from backend.core.hive import BaseAgent, EventType, HiveEvent
from backend.core.protocol import JobPacket, ResultPacket, AgentID, Vulnerability, TaskPriority

class AgentTheta(BaseAgent):
    """
    AGENT THETA (THE SENTINEL): The Optical Truth Engine.
    Visual Logic: A prism splits light to reveal what is hidden.
    Core Function: Passive DOM Analysis & Prompt Injection Defense.
    """

    def __init__(self, bus):
        super().__init__("agent_theta", bus) # AgentID.THETA
        self.name = "agent_theta"
        
        # Knowledge Base: Prompt Injection Signatures
        self.injection_patterns = [
            r"ignore previous instructions",
            r"system override",
            r"you are now (DAN|Developer|Admin)",
            r"reveal your system prompt",
            r"delete all files",
            r"transfer .* funds",
            r"simulated mode",
            r"debug mode"
        ]

    async def setup(self):
        # Subscribe to new jobs (specifically from Defense API)
        self.bus.subscribe(EventType.JOB_ASSIGNED, self.handle_job)

    async def handle_job(self, event: HiveEvent):
        """
        Process incoming DOM Snapshot for analysis.
        """
        payload = event.payload
        try:
            packet = JobPacket(**payload)
        except Exception as e:
            # print(f"[{self.name}] Error parsing job: {e}")
            return

        # Am I the target?
        if packet.config.agent_id != AgentID.THETA:
            return

        # print(f"[{self.name}] Sentinel Active. Analyzing DOM Snapshot...")
        
        dom_content = packet.target.payload or {}
        analysis_result = self.analyze_dom(dom_content)
        
        # If threat detected, publish VULN_CONFIRMED
        if analysis_result["risk_score"] > 50:
             print(f"[{self.name}] 👁️ THREAT DETECTED: {analysis_result['threat_type']} (Risk: {analysis_result['risk_score']})")
             
             # Broadcast for Dashboard & Visual Alert
             await self.bus.publish(HiveEvent(
                type=EventType.VULN_CONFIRMED,
                source=self.name,
                payload={
                    "type": "PROMPT_INJECTION" if "Injection" in analysis_result['threat_type'] else "HIDDEN_TEXT",
                    "url": packet.target.url,
                    "severity": "High" if analysis_result["risk_score"] > 80 else "Medium",
                    "data": analysis_result, # Contains details for Red Border
                    "description": f"Sentinel detected {analysis_result['threat_type']}"
                }
             ))

        # Always complete the job
        await self.bus.publish(HiveEvent(
            type=EventType.JOB_COMPLETED,
            source=self.name,
            payload={
                "job_id": packet.id,
                "status": "SUCCESS",
                "data": analysis_result
            }
        ))

    def analyze_dom(self, dom: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates VisibilityScore and InjectionRiskScore.
        """
        risk_score = 0
        threats = []
        
        # 1. Invisible Text Detection
        # Check suspicious styles
        opacity = float(dom.get("style", {}).get("opacity", 1.0))
        font_size = dom.get("style", {}).get("fontSize", "12px")
        z_index = int(dom.get("style", {}).get("zIndex", 0))
        text = dom.get("innerText", "")
        
        if opacity < 0.1 or z_index < -1000 or font_size == "0px":
             if len(text) > 5: # Ignore empty hidden divs
                 risk_score += 60
                 threats.append("Invisible Content Overlay")

        # 2. Prompt Injection Scanning
        for pattern in self.injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                risk_score += 90
                threats.append(f"Prompt Injection Signature: {pattern}")
                
        return {
            "risk_score": min(risk_score, 100),
            "threat_type": ", ".join(threats) if threats else "Clean",
            "element_api_id": dom.get("antigravity_id") # For frontend highlighting
        }

    async def execute_task(self, packet):
        """
        Synchronous execution for Defense API.
        Returns a ResultPacket with threat analysis.
        """
        from backend.core.protocol import ResultPacket, Vulnerability
        
        dom_content = packet.target.payload or {}
        analysis_result = self.analyze_dom(dom_content)
        
        vulnerabilities = []
        status = "SAFE"
        
        if analysis_result["risk_score"] > 50:
            status = "THREAT_BLOCKED"
            threat_type = "PROMPT_INJECTION" if "Injection" in analysis_result['threat_type'] else "HIDDEN_TEXT"
            vulnerabilities.append(Vulnerability(
                name=threat_type,
                severity="High" if analysis_result["risk_score"] > 80 else "Medium",
                description=f"Sentinel detected {analysis_result['threat_type']}",
                evidence=f"Risk Score: {analysis_result['risk_score']}",
                remediation="Remove hidden or malicious content from the page."
            ))
            
            # Also broadcast to EventBus for Dashboard
            await self.bus.publish(HiveEvent(
                type=EventType.VULN_CONFIRMED,
                source=self.name,
                payload={
                    "type": threat_type,
                    "url": packet.target.url,
                    "severity": vulnerabilities[0].severity,
                    "data": analysis_result,
                    "description": vulnerabilities[0].description
                }
            ))
        
        return ResultPacket(
            job_id=packet.id if hasattr(packet, 'id') else "unknown",
            source_agent=self.name,
            status=status,
            vulnerabilities=vulnerabilities,
            execution_time_ms=0,
            data=analysis_result
        )
