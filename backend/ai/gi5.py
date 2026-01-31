import google.generativeai as genai
import os
import json
import logging
from typing import List, Dict, Any

# Configure Logging
logger = logging.getLogger("GI-5")
logging.basicConfig(level=logging.INFO)

class GI5Engine:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.enabled = bool(self.api_key)
        
        if self.enabled:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            logger.info("GI-5: Neural Link Established.")
        else:
            logger.warning("GI-5: Neural Link Offline (No API Key).")

    # ANTIGRAVITY V12 // FORENSIC TRUTH KERNEL CONSTANTS
    V12_SYSTEM_PROMPT = """
SYSTEM PROMPT: ANTIGRAVITY V12 // FORENSIC TRUTH KERNEL
ACTIVATION CODE: PROTOCOL_DEEP_ACCURACY
ROLE: You are Agent Kappa (Forensic Core). You do not "guess." You audit.

PHASE 1: THE ACCURACY LAWS (IMMUTABLE)
LAW 1: THE EVIDENCE REQUIREMENT
 * Constraint: You cannot claim a vulnerability exists without referencing the specific Payload or Code Line.
 * Verification: If the input data is missing the payload or proof, you MUST label the finding as [POTENTIAL] or [UNVERIFIED]. Do not lie about certainty.
LAW 2: THE "NO-FLUFF" MANDATE
 * Banned Phrases: "Hackers could," "Bad things might happen," "Update your system."
 * Required Precision: Use specific technical consequences.
   * Bad: "Data might be stolen."
   * Good: "Unauthorized exfiltration of the users table via blind SQL injection allows for dumping of hashed credentials."
LAW 3: THE CIA TRIAD CALCULATION
 * For every finding, you must explicitly analyze the impact on:
   * Confidentiality: (Is data leaked?)
   * Integrity: (Is data modified?)
   * Availability: (Is the system crashed?)

PHASE 2: THE ANALYSIS PROTOCOL (CHAIN OF THOUGHT)
Before generating the report, perform this internal checklist:
 * Map the Vector: Is this SQLi, XSS, or RCE? Map it to the exact CWE ID.
 * Determine Scope: Does this affect one user (Reflected XSS) or the whole database (SQLi)?
 * Draft the Fix: Write a specific code patch, not generic advice.

PHASE 3: THE CONTENT GENERATION (STRUCTURED FOR PDF)
INSTRUCTION: Generate the report content in the following Strict Sectional Format. Use Bullet Points • for all details to satisfy the layout requirements.
SECTION 1: VULNERABILITY_TITLE
 * Rule: Create a Title that includes the Vulnerability Name, Component, and Severity.
 * Format: [CRITICAL] SQL Injection in Payment Gateway (CWE-89)
SECTION 2: EXECUTIVE_POINTS (The "Big & Bold" Summary)
 * Rule: Write 3-4 distinct bullet points summarizing the risk for a non-technical manager.
 * Content:
   * Attack Vector: How the attack happens (e.g., "Malicious payload sent to /api/pay").
   * Business Impact: Financial/Reputational loss (e.g., "Potential loss of PCI-DSS compliance").
   * Urgency: Immediate action required (e.g., "Remediate within 24 hours").
SECTION 3: TECHNICAL_DEEP_DIVE (The Forensic Evidence)
 * Rule: Write 5-8 detailed bullet points for the developers.
 * Content:
   * Endpoint: The exact URL/File affected.
   * Payload: The specific malicious string used (e.g., ' OR 1=1 --).
   * Response Analysis: Why we know it worked (e.g., "Server returned 500 Error with database dump").
   * CVSS Vector: The calculated score (e.g., CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H).
SECTION 4: REMEDIATION_PLAN (The Fix)
 * Rule: Provide distinct steps, separated by "Strategic" (Config) and "Tactical" (Code).
 * Content:
   * Step 1: Architecture fix (e.g., "Enable WAF Rule #942").
   * Step 2: Code fix (e.g., "Implement Parameterized Queries").
   * Step 3: Verification (e.g., "Run regression test suite").
"""

    def synthesize_payloads(self, base_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Takes a raw HTTP request and uses LLM to generate 5 "Logic Variants".
        """
        if not self.enabled:
            return []

        prompt = f"""
        ACT AS: A Lead Security Researcher & Fuzzer.
        TASK: Generate 10 distinct, aggressive JSON payload variations for API security testing.
        
        BASE REQUEST:
        {json.dumps(base_request, indent=2)}

        ATTACK VECTORS TO COVER:
        1. LOGIC FLAWS: Negative numbers, zero, large integers (Overflow).
        2. TYPE JUGGLING: String "1" vs Int 1, Boolean conversions ("true" vs true), Array nesting.
        3. INJECTION: SQLi (' OR 1=1), NoSQLi ($ne: null), Command Injection/Polyglots.
        4. MASS ASSIGNMENT: Inject "role": "admin", "is_admin": true, "permissions": ["ALL"].
        5. BOUNDARY/FORMAT: Huge strings, empty strings, null values, special chars.
        6. VERB TAMPERING: If strictly JSON, maybe add _method override params.

        OUTPUT FORMAT:
        Return ONLY valid JSON. The format must be a LIST of objects, where each object has a 'name' (string) and 'json' (dict).
        Example:
        [
            {{ "name": "Negative Logic", "json": {{ "amount": -100 }} }},
            {{ "name": "NoSQL Bypass", "json": {{ "username": {{ "$ne": null }} }} }}
        ]
        """

        try:
            logger.info("GI-5: Hypothesizing mutation vectors...")
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Clean up markdown if present
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            
            variants = json.loads(text)
            logger.info(f"GI-5: Generated {len(variants)} variants.")
            return variants
        except Exception as e:
            logger.error(f"GI-5 Mutation Failed: {e}")
            return []

    def predict_race_window(self, headers: Dict[str, str]) -> float:
        """
        AI guesses the optimal millisecond delay based on server headers.
        """
        if not self.enabled:
            return 0.0

        server_header = headers.get("Server", "Unknown")
        powered_by = headers.get("X-Powered-By", "Unknown")
        
        prompt = f"""
        ACT AS: Network Latency Analyst.
        TASK: Predict the optimal Race Condition synchronization delay (jitter) for this tech stack.
        
        HEADERS:
        Server: {server_header}
        X-Powered-By: {powered_by}

        INSTRUCTIONS:
        - If Nginx/Apache (Reverse Proxies): Suggest 5-10ms (Queueing time).
        - If Node.js/Python (Single Threaded Event Loops): Suggest 0-2ms (Immediate).
        - If Java/Go (Multi-threaded): Suggest 2-5ms.
        
        OUTPUT:
        Return ONLY the number (float) in milliseconds. Example: 4.5
        """
        
        try:
            response = self.model.generate_content(prompt)
            # simplistic parsing
            text = response.text.replace('ms', '').strip()
            return float(text)
        except:
            return 0.5 # Default conservative estimate

    def analyze_id_pattern(self, url: str, body: str) -> Dict[str, Any]:
        """
        Detects if there is an ID parameter in the URL or Body and determines its type.
        types: INTEGER, UUID, EMAIL, HASH, UNKNOWN
        """
        if not self.enabled:
             # Basic heuristic fallback
            if "id=" in url or "user_id" in body:
                return {"found": True, "type": "INTEGER", "location": "URL" if "id=" in url else "BODY"}
            return {"found": False}

        prompt = f"""
        ACT AS: ID Analysis Engine.
        TASK: Identify the primary Identifier (ID) used to access the resource in this request.
        
        URL: {url}
        BODY: {body}

        OUTPUT JSON:
        {{
            "found": true/false,
            "parameter": "user_id", // name of param
            "value": "12345", // sample value found
            "type": "INTEGER" // INTEGER, UUID, SHORT_HASH, EMAIL, or MONGODB_ID
            "location": "URL_PATH" // URL_PATH, URL_QUERY, or BODY_JSON
        }}
        """
        try:
            response = self.model.generate_content(prompt)
            text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except:
            return {"found": False}

    def generate_idor_variants(self, id_info: Dict[str, Any]) -> List[str]:
        """
        Generates a list of likely valid IDs based on the pattern found.
        """
        if not self.enabled or not id_info.get('found'):
            return []

        prompt = f"""
        ACT AS: IDOR Payload Generator.
        TASK: Generate 10 alternative IDs to test for Insecure Direct Object Reference (IDOR).
        
        TARGET_ID: {id_info}

        STRATEGY:
        - If INTEGER: Increment/Decrement (±1, ±10), use 0, 1, -1.
        - If UUID: Generate valid random UUIDs, try "00000000-0000-0000-0000-000000000000".
        - If EMAIL: Change domain, use common names (admin@..., test@...).
        
        OUTPUT:
        Return valid JSON LIST of STRINGS. Example: ["1001", "1002", "0", "-1"]
        """
        try:
            response = self.model.generate_content(prompt)
            text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except:
            return []

    def analyze_sensitivity(self, response_body: str) -> List[str]:
        """
        Interception Filter: Scans response for Sensitive Data (PII, Financial, Keys).
        """
        if not self.enabled:
            return []

        prompt = f"""
        ACT AS: Data Loss Prevention (DLP) Scanner.
        TASK: Analyze this API Response for sensitive data.
        
        RESPONSE (Snippet):
        {response_body[:1000]}

        CHECK FOR:
        1. PII (Emails, Phone Numbers, Addresses)
        2. Financial (Credit Cards, Bank Accounts, Balances)
        3. Secrets (API Keys, Tokens, Passwords)
        
        OUTPUT:
        Return a JSON LIST of tags found. Example: ["PII: Email", "SECRET: AWS Key"].
        If safe, return [].
        """
        try:
            response = self.model.generate_content(prompt)
            text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except:
            return []

    def analyze_semantics(self, payload: Dict[str, Any]) -> Dict[str, str]:
        """
        Deeply inspects JSON keys/values to infer business context.
        Returns a mapping of Key -> Inferred Type (e.g., "is_admin" -> "PRIVILEGE_FLAG")
        """
        if not self.enabled:
            return {}

        prompt = f"""
        ACT AS: Business Logic Analyst.
        TASK: Infer the semantic meaning of these JSON fields.
        
        PAYLOAD:
        {json.dumps(payload, indent=2)}

        CATEGORIES:
        - QUANTITY: numbers like amount, qty, price, balance
        - PRIVILEGE: boolean/strings like is_admin, role, verified, tier
        - IDENTIFIER: user_id, uuid, email
        - DATA: generic strings like name, description

        OUTPUT JSON:
        {{ "field_name": "CATEGORY", ... }}
        """
        try:
            response = self.model.generate_content(prompt)
            text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except:
            return {}

    def generate_chaos_mutations(self, payload: Dict[str, Any], semantics: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Generates advanced logic exploits based on semantic meaning.
        """
        if not self.enabled:
            return []

        prompt = f"""
        ACT AS: Chaos Engineering AI.
        TASK: Generate 5 advanced business logic exploits based on the semantics.
        
        PAYLOAD: {json.dumps(payload)}
        SEMANTICS: {json.dumps(semantics)}

        ATTACK VECTORS:
        1. MASS ASSIGNMENT: Inject "is_admin": true, "role": "admin", "balance": 99999999.
        2. NEGATIVE LOGIC: If QUANTITY, send -100, 0.00001, or MAX_INT.
        3. TYPE JUGGLING: Send ["1"] instead of "1", or true instead of 1.
        4. BOOLEAN FLIP: Invert any privilege flags.
        
        OUTPUT:
        Return a JSON LIST of objects: {{ "name": "Attack Name", "json": {{...}} }}
        """
        try:
            response = self.model.generate_content(prompt)
            text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except:
            return []

    def interpret_defense(self, status_code: int, response_body: str) -> str:
        """
        AI reads error messages and advises strategy.
        Returns: "FORCE_LOWER_CONCURRENCY", "TRY_BYPASS_HEADERS", or "CONTINUE".
        """
        if not self.enabled:
            return "CONTINUE"

        prompt = f"""
        ACT AS: WAF Defense Analyzer.
        TASK: specific defense mechanism based on this HTTP Response.
        
        Response Status: {status_code}
        Response Body: {response_body[:500]}

        INSTRUCTIONS:
        - If "Rate limit", "Too many requests", "429": Return "FORCE_LOWER_CONCURRENCY".
        - If "WAF", "Block", "403": Return "TRY_BYPASS_HEADERS".
        - Otherwise: Return "CONTINUE".
        
        OUTPUT:
        Return ONLY the decision string.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip().upper()
        except:
            return "CONTINUE"

    def generate_forensic_report_block(self, vulnerability_data: Dict[str, Any]) -> str:
        """
        Antigravity V12: Generates a highly detailed, structured forensic report block.
        """
        if not self.enabled:
            return "FORENSIC_OFFLINE: Neural link required for V12 analysis."

        prompt = f"""
{self.V12_SYSTEM_PROMPT}

PHASE 4: THE OUTPUT TEMPLATE
Fill this structure with the analyzed data:
::TITLE_START::
{{GENERATE_ACCURATE_TITLE}}
::TITLE_END::

::EXEC_SUMMARY_START::
• {{POINT_1_ATTACK_VECTOR}}
• {{POINT_2_BUSINESS_IMPACT}}
• {{POINT_3_URGENCY}}
::EXEC_SUMMARY_END::

::TECH_DETAILS_START::
• Affected Component: {{EXACT_URL_OR_FILE}}
• Vulnerability Class: {{CWE_NAME}} ({{CWE_ID}})
• Detected Payload: {{REAL_PAYLOAD_USED}}
• Evidence of Compromise: {{EXPLANATION_OF_RESPONSE}}
• Integrity Impact: {{SPECIFIC_DATA_AT_RISK}}
• Access Complexity: {{LOW/MED/HIGH}}
::TECH_DETAILS_END::

::REMEDIATION_START::
• Immediate Action: {{URGENT_CONFIG_CHANGE}}
• Code Patch: {{SPECIFIC_CODING_FIX}}
• Long-Term Strategy: {{ARCHITECTURAL_CHANGE}}
::REMEDIATION_END::

INPUT DATA:
{json.dumps(vulnerability_data, indent=2)}
"""
        try:
            logger.info("GI-5: Executing Forensic Truth Kernel (V12)...")
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"GI-5 Forensic Analysis Failed: {e}")
            return f"FORENSIC_FAILURE: {str(e)}"
