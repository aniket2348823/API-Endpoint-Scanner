
import os
import json
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from backend.ai.gi5 import GI5Engine
from backend.reporting.pdf_maker import ForensicReport

def test_v12_logic():
    print("--- [1/3] Testing GI5 V12 Forensic Prompt ---")
    # Use a dummy key if env not set for structure test (won't call API but checks logic)
    engine = GI5Engine(api_key=os.getenv("GEMINI_API_KEY", "DUMMY_KEY"))
    
    sample_data = {
        "target": "http://api.target.com/api/pay",
        "payload": "' OR 1=1 --",
        "verdict": "VULNERABLE",
        "status": "200 OK",
        "variant": "SQLi Attempt #1"
    }
    
    # If key is dummy, it will return OFFLINE message, but if real it will return structured text
    if not os.getenv("GEMINI_API_KEY"):
        print("[!] No API key found. Skipping live AI test.")
        # Mocking AI output for PDF test
        ai_output = """
::TITLE_START::
[CRITICAL] SQL Injection in Payment Gateway (CWE-89)
::TITLE_END::

::EXEC_SUMMARY_START::
• Attack Vector: Malicious payload sent to /api/pay allows database access.
• Business Impact: Potential loss of PCI-DSS compliance and customer data leakage.
• Urgency: Immediate action required; remediate within 24 hours.
::EXEC_SUMMARY_END::

::TECH_DETAILS_START::
• Affected Component: http://api.target.com/api/pay
• Vulnerability Class: SQL Injection (CWE-89)
• Detected Payload: ' OR 1=1 --
• Evidence of Compromise: Server returned 200 OK with sensitive database dump.
• Integrity Impact: Full database access allows modification of payment records.
• Access Complexity: LOW
::TECH_DETAILS_END::

::REMEDIATION_START::
• Immediate Action: Enable WAF Rule #942 to block common SQLi patterns.
• Code Patch: Implement Parameterized Queries across all database interactions.
• Long-Term Strategy: Conduct a full security audit of the payment module.
::REMEDIATION_END::
"""
    else:
        print("[*] Generating live V12 forensic report block...")
        ai_output = engine.generate_forensic_report_block(sample_data)
        print("AI Output Snippet:\n", ai_output[:200], "...")

    print("\n--- [2/3] Testing PDF Marker Parsing & Rendering ---")
    report = ForensicReport()
    report.add_page()
    
    try:
        report.add_forensic_truth_kernel_section(ai_output)
        output_file = "v12_test_report.pdf"
        report.output(output_file)
        print(f"[+] PDF generated successfully: {output_file}")
    except Exception as e:
        print(f"[-] PDF Generation Failed: {e}")

    print("\n--- [3/3] Logic Verification ---")
    if "::TITLE_START::" in ai_output and "::REMEDIATION_END::" in ai_output:
        print("[TRUE] Output contains correct V12 markers.")
    else:
        print("[FALSE] Output is missing markers.")

if __name__ == "__main__":
    test_v12_logic()
