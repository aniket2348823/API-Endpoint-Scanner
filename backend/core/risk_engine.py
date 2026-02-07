# FILE: backend/core/risk_engine.py
# ROLE: THE JUDGE
# RESPONSIBILITY: Centralized Risk Scoring Logic

class RiskEngine:
    """
    The Risk Engine calculates a deterministic 0-100 score for any given threat.
    It standardizes judgment across all agents.
    """

    @staticmethod
    def calculate_risk(threat_type: str, context: dict) -> int:
        base_score = 0
        
        # 1. BASELINE SCORES
        if threat_type == "PROMPT_INJECTION":
            base_score = 95
        elif threat_type == "INVISIBLE_TEXT":
            base_score = 75
        elif threat_type == "DECEPTIVE_UI":
            base_score = 85
        elif threat_type == "PHISHING":
            base_score = 99
        elif threat_type == "ROACH_MOTEL":
            base_score = 80
        else:
            base_score = 50 # Unknown/Suspicious

        # 2. CONTEXTUAL MODIFIERS
        # Example: If on a banking site, risk is higher? (Future feature)
        # For now, we return base score.
        
        return min(base_score, 100)

    @staticmethod
    def get_verdict(risk_score: int) -> str:
        if risk_score >= 80:
            return "BLOCK"
        elif risk_score >= 50:
            return "WARN"
        else:
            return "ALLOW"
