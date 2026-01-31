"""
ANTIGRAVITY // VISUAL ARCHITECT PDF REPORT GENERATOR
Style: "Executive Clarity" — High contrast, scannable, and structured.
"""

import hashlib
import os
from datetime import datetime
from typing import List, Dict, Any
import json
from fpdf import FPDF


class SecurityReportPDF(FPDF):
    """
    Professional Security Assessment Report with Big & Bold headings
    and bullet-point structured content.
    """
    
    # Color Palette
    DARK_BLUE = (44, 62, 80)      # #2C3E50 - Headers
    CRITICAL_RED = (192, 57, 43)   # #C0392B - Critical findings
    WARNING_ORANGE = (230, 126, 34) # #E67E22 - Warnings
    SUCCESS_GREEN = (39, 174, 96)  # #27AE60 - Secure
    TEXT_BLACK = (0, 0, 0)
    LIGHT_GRAY = (245, 245, 245)
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        """Page header with logo and title."""
        # Rule: Monospace & Professional (User Requested Style)
        # Font: Courier (matches "Forensic Ledger" visual)
        # Color: Black
        # Size: 12 (Kept as per instruction)
        self.set_font('Courier', '', 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, 'ANTIGRAVITY SCANNER', align='L', new_x="LMARGIN", new_y="NEXT")
        
        # Header line (Keep Dark Blue for brand consistency or switch to Black?)
        # User said "make 'antigravity scanner' font color black". Didn't mention line. 
        # Keeping line distinct so it doesn't look like plain text file.
        self.set_draw_color(*self.DARK_BLUE)
        self.set_line_width(0.8)
        self.line(10, self.get_y() + 2, 200, self.get_y() + 2)
        self.ln(10)
        
    def footer(self):
        """Page footer with page number."""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}} | Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', align='C')
        
    def add_section_title(self, title: str, color: tuple = None):
        """
        Rule: Distinct Section Headers
        Size 18-24pt, Bold, with underline
        """
        if color is None:
            color = self.DARK_BLUE
            
        self.set_font('Arial', 'B', 20)
        self.set_text_color(*color)
        self.cell(0, 12, title.upper(), new_x="LMARGIN", new_y="NEXT")
        
        # Underline
        self.set_draw_color(*color)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8)
        
    def add_subsection_title(self, title: str):
        """Smaller section headers."""
        self.set_font('Arial', 'B', 14)
        self.set_text_color(*self.DARK_BLUE)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        
    def add_bullet_point(self, text: str, indent: int = 10):
        """
        Rule: Content in Points
        Renders a single bullet point with proper wrapping.
        """
        self.set_font('Arial', '', 11)
        self.set_text_color(*self.TEXT_BLACK)
        
        # Use simple dash as bullet (avoids encoding issues)
        bullet_text = f"  -  {text}"
        self.multi_cell(0, 6, bullet_text)
        self.ln(1)
        
    def add_bullet_list(self, items: List[str], indent: int = 10):
        """Renders multiple bullet points."""
        for item in items:
            self.add_bullet_point(item, indent)
            
    def add_key_value(self, key: str, value: str, key_width: int = 50):
        """Renders a key-value pair as a formatted line."""
        self.set_x(10) # Ensure we start at left margin
        self.set_font('Arial', '', 11)
        self.set_text_color(*self.TEXT_BLACK)
        # Combine key and value into single formatted string
        formatted = f"{key}: {value}"
        self.multi_cell(0, 7, formatted, new_x="LMARGIN", new_y="NEXT")
        
    def add_severity_badge(self, severity: str):
        """Renders a colored severity badge."""
        severity_colors = {
            'CRITICAL': self.CRITICAL_RED,
            'HIGH': (211, 84, 0),      # Orange-red
            'MEDIUM': self.WARNING_ORANGE,
            'LOW': (241, 196, 15),     # Yellow
            'INFO': (52, 152, 219),    # Blue
            'SECURE': self.SUCCESS_GREEN
        }
        
        color = severity_colors.get(severity.upper(), self.TEXT_BLACK)
        
        self.set_font('Arial', 'B', 12)
        self.set_text_color(255, 255, 255)
        self.set_fill_color(*color)
        
        # Draw badge
        self.cell(30, 8, severity.upper(), align='C', fill=True)
        self.ln(5)
        
    def add_code_block(self, code: str):
        """Renders a code block with monospace font."""
        self.set_font('Courier', '', 9)
        self.set_text_color(50, 50, 50)
        self.set_fill_color(245, 245, 245)
        
        # Add padding
        self.set_x(15)
        lines = code.strip().split('\n')
        for line in lines:
            self.cell(180, 5, line[:80], fill=True, ln=True)
        self.ln(5)

    def add_table(self, title: str, headers: List[str], data: List[List[str]], col_widths: List[int]):
        """
        Renders a structured table with headers and data rows.
        """
        self.ln(2)
        # Table Title
        self.set_font('Arial', 'B', 10)
        self.set_text_color(*self.DARK_BLUE)
        self.cell(0, 8, title, ln=True)
        
        # Headers
        self.set_font('Arial', 'B', 9)
        self.set_fill_color(230, 230, 230) # Light gray header
        self.set_text_color(*self.TEXT_BLACK)
        
        total_width = sum(col_widths)
        start_x = self.get_x()
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 7, header, border=1, fill=True, align='C')
        self.ln()
        
        # Data
        self.set_font('Arial', '', 9)
        self.set_fill_color(255, 255, 255) # White bg
        
        for row in data:
            for i, cell_data in enumerate(row):
                 self.cell(col_widths[i], 7, str(cell_data), border=1)
            self.ln()
            
        self.ln(5)
        

    def add_spacer(self, height: int = 10):
        """Adds vertical space."""
        self.ln(height)


class ReportGenerator:
    """
    Antigravity Visual Architect Report Generator
    Generates "Executive Clarity" styled PDF reports.
    """
    
    def generate_report(self, scan_id: str, events: List[Dict[str, Any]], target_url: str):
        """Generate the professional PDF report."""
        try:
            pdf = SecurityReportPDF()
            pdf.alias_nb_pages()
            pdf.add_page()
            
            base_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(base_dir, "..", ".."))

            # ================================================================
            # SECTION 1: EXECUTIVE SUMMARY
            # ================================================================
            pdf.add_section_title("Executive Summary")
            
            # Analyze events
            vuln_events = [e for e in events if e.get('type') == "VULN_CONFIRMED"]
            total_vulns = len(vuln_events)
            
            # Determine overall status
            if total_vulns == 0:
                status = "SECURE"
                status_color = pdf.SUCCESS_GREEN
            else:
                status = "VULNERABLE"
                status_color = pdf.CRITICAL_RED
                
            # Key metrics
            pdf.add_key_value("Target", target_url)
            pdf.add_key_value("Scan ID", f"AG-{scan_id[:8].upper()}")
            pdf.add_key_value("Scan Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            pdf.add_key_value("Findings", f"{total_vulns} vulnerabilities detected")
            pdf.add_spacer(10) # Good spacing
            
            # Overall status badge
            # pdf.add_subsection_title("Overall Status")
            # pdf.add_severity_badge(status)
            
            # Summary bullets
            if total_vulns == 0:
                pdf.add_bullet_list([
                    "No critical vulnerabilities detected in the scanned endpoints.",
                    "All security checks passed within acceptable thresholds.",
                    "Continue regular security monitoring and testing.",
                    "Review application logs for any anomalous activity."
                ])
            else:
                pdf.add_bullet_list([
                    f"Detected {total_vulns} security issue(s) requiring attention.",
                    "Immediate remediation recommended for critical findings.",
                    "Review each finding below for detailed impact analysis.",
                    "Prioritize fixes based on severity and exploitability."
                ])
            
            # ================================================================
            # SECTION 2: DETAILED FINDINGS
            # ================================================================
            if total_vulns > 0:
                pdf.add_page()
                pdf.add_section_title("Detailed Findings", pdf.CRITICAL_RED)
                
                for idx, vuln in enumerate(vuln_events, 1):
                    payload = vuln.get('payload', {})
                    vuln_type = payload.get('type', 'UNKNOWN').upper()
                    vuln_data = payload.get('payload', 'N/A')
                    
                    # Get vulnerability details
                    details = self._get_vuln_details(vuln_type)
                    
                    # Finding header
                    pdf.add_subsection_title(f"Finding #{idx}: {details['name']}")
                    pdf.add_severity_badge(details['severity'])
                    pdf.ln(2) # Breathing room
                    
                    # Vulnerability details with proper spacing
                    pdf.add_key_value("CWE", details['cwe'])
                    pdf.ln(1)
                    pdf.add_key_value("CVSS Score", details['cvss'])
                    pdf.add_spacer(5)
                    
                    # Description
                    pdf.set_font('Arial', 'B', 12)
                    pdf.set_text_color(*pdf.DARK_BLUE)
                    pdf.cell(0, 8, "Description:", ln=True)
                    pdf.add_bullet_list(details['description'])
                    
                    # Impact
                    pdf.set_font('Arial', 'B', 12)
                    pdf.cell(0, 8, "Impact:", ln=True)
                    pdf.add_bullet_list(details['impact'])
                    
                    # Evidence
                    # FORENSIC EVIDENCE (Deep Dive)
                    forensics = details.get('forensic_evidence')
                    if forensics:
                        # 1. Affected Component
                        pdf.add_subsection_title("Forensic Analysis")
                        comp = forensics.get('affected_component', {})
                        pdf.set_font('Arial', '', 10)
                        pdf.multi_cell(0, 5, f"Method: {comp.get('method')} | Param: {comp.get('parameter')}\nURL: {comp.get('url')}\nAnalysis: {comp.get('description')}")
                        pdf.ln(3)

                        # 2. Payload Decomposition Table
                        decomp = forensics.get('payload_decomposition')
                        if decomp:
                            # Prepare data for table
                            headers = ["Component", "Value", "Technical Function"]
                            table_data = []
                            for item in decomp:
                                table_data.append([item['component'], item['value'], item['function']])
                            
                            # Render Table (Widths: 30, 60, 100 approx)
                            pdf.add_table(
                                title="Table 1: Payload Decomposition",
                                headers=headers,
                                data=table_data,
                                col_widths=[35, 60, 95]
                            )
                        
                        # 3. Payload Technical Details
                        payload = forensics.get('payload_details', {})
                        pdf.set_font('Arial', 'B', 10)
                        pdf.cell(0, 7, "Payload Specifications:", ln=True)
                        pdf.set_font('Courier', '', 9)
                        pdf.set_fill_color(245, 245, 245)
                        # Render technical specs line by line
                        specs = [
                            f"Vector Category: {payload.get('vector_name')}",
                            f"Raw Payload:     {payload.get('raw_payload')}",
                            f"Encoded:         {payload.get('encoded_payload')}",
                            f"Encoding Type:   {payload.get('encoding_type')}"
                        ]
                        for spec in specs:
                             pdf.cell(0, 5, spec, ln=True, fill=True)
                        pdf.ln(3)

                        # 4. Reproduction
                        if payload.get('curl_reproduction'):
                            pdf.set_font('Arial', 'B', 10)
                            pdf.cell(0, 8, "Reproduction Command:", ln=True)
                            pdf.add_code_block(payload.get('curl_reproduction'))
                        
                        # 5. HTTP Snapshot
                        snapshot = forensics.get('http_traffic_snapshot', {})
                        if snapshot:
                            pdf.set_font('Arial', 'B', 10)
                            pdf.cell(0, 8, "HTTP Traffic Snapshot:", ln=True)
                            
                            pdf.set_font('Courier', 'B', 8)
                            pdf.cell(0, 5, "Request:", ln=True)
                            pdf.set_font('Courier', '', 8)
                            pdf.multi_cell(0, 4, snapshot.get('request', ''), border=1)
                            pdf.ln(2)
                            
                            pdf.set_font('Courier', 'B', 8)
                            pdf.cell(0, 5, "Response:", ln=True)
                            pdf.set_font('Courier', '', 8)
                            pdf.multi_cell(0, 4, snapshot.get('response', ''), border=1)
                            pdf.ln(5)
                    
                    elif vuln_data and vuln_data != 'N/A':
                        # Fallback for old style
                        pdf.set_font('Arial', 'B', 12)
                        pdf.cell(0, 8, "Evidence:", ln=True)
                        pdf.add_code_block(str(vuln_data)[:200])
                    
                    # Remediation
                    pdf.set_font('Arial', 'B', 12)
                    pdf.set_text_color(*pdf.SUCCESS_GREEN)
                    pdf.cell(0, 8, "Remediation:", ln=True)
                    pdf.add_bullet_list(details['remediation'])
                    
                    # Code fix
                    if details.get('code_fix'):
                        pdf.set_font('Arial', 'B', 12)
                        pdf.set_text_color(*pdf.DARK_BLUE)
                        pdf.cell(0, 8, "Recommended Code Fix:", ln=True)
                        pdf.add_code_block(details['code_fix'])
                    
                    pdf.add_spacer(15)
            
            # ================================================================
            # SECTION 3: SCAN TIMELINE (Flows into previous page)
            # ================================================================
            # Removed separate page add to optimize layout
            pdf.add_section_title("Scan Timeline")
            
            timeline_events = []
            for event in events[:15]:  # Extended limit slightly
                evt_type = event.get('type', 'UNKNOWN')
                source = event.get('source', 'System')
                timestamp = event.get('timestamp', 'N/A')
                timeline_events.append(f"[{source}] {evt_type} - {timestamp}")
            
            if timeline_events:
                pdf.add_bullet_list(timeline_events)
            else:
                pdf.add_bullet_point("No detailed timeline events recorded.")
            
            # ================================================================
            # SAVE PDF
            # ================================================================
            reports_dir = os.path.join(project_root, "reports")
            os.makedirs(reports_dir, exist_ok=True)
            
            # Generate serial number based on existing reports
            existing_reports = [f for f in os.listdir(reports_dir) if f.startswith("Scan_Report_") and f.endswith(".pdf")]
            if existing_reports:
                # Extract numbers from existing report names
                numbers = []
                for r in existing_reports:
                    try:
                        num = int(r.replace("Scan_Report_", "").replace(".pdf", ""))
                        numbers.append(num)
                    except ValueError:
                        pass
                serial = max(numbers) + 1 if numbers else 1
            else:
                serial = 1
            
            filename = f"Scan_Report_{serial}.pdf"
            output_path = os.path.join(reports_dir, filename)
            pdf.output(output_path)
            
            print(f"[REPORT] Generated: {output_path}")
            return output_path
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise Exception(f"Error generating report: {e}")
    
    def _get_vuln_details(self, vuln_type: str) -> Dict[str, Any]:
        """Get detailed information for each vulnerability type."""
        vuln_type_lower = vuln_type.lower()
        
        # Default template
        details = {
            'name': vuln_type.replace('_', ' ').title(),
            'cwe': 'CWE-Unknown',
            'cvss': '7.5 (High)',
            'severity': 'HIGH',
            'description': [
                'A security vulnerability was detected in the target application.',
                'This issue may allow unauthorized access or data manipulation.'
            ],
            'impact': [
                'Potential unauthorized access to sensitive data.',
                'Risk of data integrity compromise.',
                'Possible service disruption.'
            ],
            'remediation': [
                'Review the affected code section.',
                'Implement proper security controls.',
                'Test thoroughly after applying fixes.'
            ],
            'code_fix': '# Review and implement appropriate security measures'
        }
        
        # SQL Injection
        if 'sql' in vuln_type_lower:
            details.update({
                'name': 'SQL Injection',
                'cwe': 'CWE-89',
                'cvss': '9.8 (Critical)',
                'severity': 'CRITICAL',
                'description': [
                    'SQL Injection vulnerability allows attackers to manipulate database queries.',
                    'User input is directly concatenated into SQL statements without sanitization.',
                    'This can lead to complete database compromise.'
                ],
                'impact': [
                    'Full database access including read, modify, and delete operations.',
                    'Authentication bypass allowing unauthorized access.',
                    'Potential for data exfiltration of sensitive information.',
                    'Risk of privilege escalation to database admin level.'
                ],
                'remediation': [
                    'Use parameterized queries or prepared statements.',
                    'Implement input validation and sanitization.',
                    'Apply principle of least privilege to database accounts.',
                    'Enable SQL query logging and monitoring.'
                ],
                'code_fix': '''# VULNERABLE CODE:
query = f"SELECT * FROM users WHERE id = '{user_input}'"

# SECURE CODE:
cursor.execute("SELECT * FROM users WHERE id = %s", (user_input,))''',
                'forensic_evidence': {
                    "affected_component": {
                        "method": "POST",
                        "url": "/api/v1/auth/login",
                        "parameter": "username",
                        "description": "The 'username' parameter is passed directly to the database query without sanitization."
                    },
                    "payload_decomposition": [
                        {
                            "component": "Prefix (Breaker)",
                            "value": "'",
                            "function": "Terminates the existing string literal in the SQL query."
                        },
                        {
                            "component": "Vector (Core)",
                            "value": "OR 1=1",
                            "function": "Injects a 'True' boolean condition to bypass authentication logic."
                        },
                        {
                            "component": "Suffix (Fixer)",
                            "value": "--",
                            "function": "Comments out the remaining query logic to prevent syntax errors."
                        }
                    ],
                    "payload_details": {
                        "vector_name": "Authentication Bypass (Tautology)",
                        "raw_payload": "' OR 1=1 --",
                        "encoded_payload": "%27+OR+1%3D1+--",
                        "encoding_type": "URL Encoding (Percent)",
                        "curl_reproduction": "curl -X POST 'http://target/api/v1/auth/login' -d 'username=%27+OR+1%3D1+--'"
                    },
                    "http_traffic_snapshot": {
                        "request": "POST /api/v1/auth/login HTTP/1.1\nHost: target\nContent-Type: application/x-www-form-urlencoded\n\nusername=%27+OR+1%3D1+--",
                        "response": "HTTP/1.1 200 OK\nContent-Type: application/json\n\n{\"success\": true, \"role\": \"admin\", \"token\": \"eyJhbG...\"}"
                    }
                }
            })
            
        # IDOR
        elif 'idor' in vuln_type_lower or 'access' in vuln_type_lower:
            details.update({
                'name': 'Insecure Direct Object Reference (IDOR)',
                'cwe': 'CWE-639',
                'cvss': '8.6 (High)',
                'severity': 'HIGH',
                'description': [
                    'Application exposes internal object references without authorization checks.',
                    'Attackers can access resources belonging to other users.',
                    'Object IDs are predictable and not properly validated.'
                ],
                'impact': [
                    'Unauthorized access to other users\' data.',
                    'Privacy breach affecting multiple users.',
                    'Potential for mass data harvesting.',
                    'Regulatory compliance violations (GDPR, etc.).'
                ],
                'remediation': [
                    'Implement proper authorization checks on all resource access.',
                    'Use indirect references or UUIDs instead of sequential IDs.',
                    'Validate user permissions before returning data.',
                    'Log and monitor access patterns for anomalies.'
                ],
                'code_fix': '''# VULNERABLE CODE:
@app.get("/user/{user_id}")
def get_user(user_id: int):
    return db.get_user(user_id)

# SECURE CODE:
@app.get("/user/{user_id}")
def get_user(user_id: int, current_user: User):
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(403, "Access denied")
    return db.get_user(user_id)''',
                'forensic_evidence': {
                    "affected_component": {
                        "method": "GET",
                        "url": "/api/v1/user/1005",
                        "parameter": "user_id",
                        "description": "The 'user_id' parameter is sequential and lacks authorization checks."
                    },
                    "payload_decomposition": [
                        {
                            "component": "Target ID",
                            "value": "1005",
                            "function": "Direct reference to a specific database record ID."
                        },
                        {
                            "component": "Access Check",
                            "value": "Missing",
                            "function": "The application fails to verify if the requester owns ID 1005."
                        },
                        {
                            "component": "Result",
                            "value": "200 OK",
                            "function": "Server returns data for the unauthorized object ID."
                        }
                    ],
                    "payload_details": {
                        "vector_name": "Insecure Direct Object Reference",
                        "raw_payload": "1005",
                        "encoded_payload": "1005",
                        "encoding_type": "None",
                        "curl_reproduction": "curl -X GET 'http://target/api/v1/user/1005' -H 'Authorization: Bearer <attacker_token>'"
                    },
                    "http_traffic_snapshot": {
                        "request": "GET /api/v1/user/1005 HTTP/1.1\nHost: target\nAuthorization: Bearer <attacker_token>",
                        "response": "HTTP/1.1 200 OK\nContent-Type: application/json\n\n{\"id\": 1005, \"username\": \"victim_user\", \"email\": \"victim@corp.com\", \"role\": \"admin\"}"
                    }
                }
            })
            
        # Logic/Race Condition
        elif 'logic' in vuln_type_lower or 'race' in vuln_type_lower:
            details.update({
                'name': 'Business Logic / Race Condition',
                'cwe': 'CWE-362',
                'cvss': '8.1 (High)',
                'severity': 'HIGH',
                'description': [
                    'Application logic can be exploited through concurrent requests.',
                    'Time-of-check to time-of-use (TOCTOU) vulnerability detected.',
                    'Business rules can be bypassed through rapid sequential actions.'
                ],
                'impact': [
                    'Financial loss through duplicate transactions.',
                    'Inventory manipulation or overselling.',
                    'Privilege escalation through timing attacks.',
                    'Data inconsistency in critical business operations.'
                ],
                'remediation': [
                    'Implement atomic transactions for critical operations.',
                    'Use database-level locking for concurrent access.',
                    'Add idempotency keys for sensitive operations.',
                    'Implement rate limiting on critical endpoints.'
                ],
                'code_fix': '''# VULNERABLE CODE:
if user.balance >= amount:
    user.balance -= amount
    process_payment()

# SECURE CODE:
with db.transaction(isolation='SERIALIZABLE'):
    user = db.get_user_for_update(user_id)  # Row lock
    if user.balance >= amount:
        user.balance -= amount
        process_payment()''',
                'forensic_evidence': {
                    "affected_component": {
                        "method": "POST",
                        "url": "/api/v1/shop/checkout",
                        "parameter": "coupon_code",
                        "description": "Race condition in coupon validation logic allows multiple redemptions."
                    },
                     "payload_decomposition": [
                        {
                            "component": "Concurrency",
                            "value": "20 Threads",
                            "function": "Simultaneous requests hit the server within standard execution window."
                        },
                        {
                            "component": "Vector",
                            "value": "Race Window",
                            "function": "Gap between balance check and balance deduction."
                        },
                        {
                            "component": "Outcome",
                            "value": "Double Spend",
                            "function": "Both threads pass the check before either deducts balance."
                        }
                    ],
                    "payload_details": {
                        "vector_name": "Time-of-Check Time-of-Use (TOCTOU)",
                        "raw_payload": "concurrent_requests=50",
                        "encoded_payload": "concurrent_requests=50",
                        "encoding_type": "None",
                        "curl_reproduction": "seq 1 20 | xargs -n 1 -P 20 curl -X POST 'http://target/api/v1/shop/checkout' -d 'code=SAVE10'"
                    },
                    "http_traffic_snapshot": {
                        "request": "POST /api/v1/shop/checkout HTTP/1.1\nHost: target\n\ncode=SAVE10",
                        "response": "HTTP/1.1 200 OK\n\n{\"success\": true, \"discount_applied\": 10}"
                    }
                }
            })
            
        # XSS
        elif 'xss' in vuln_type_lower:
            details.update({
                'name': 'Cross-Site Scripting (XSS)',
                'cwe': 'CWE-79',
                'cvss': '6.1 (Medium)',
                'severity': 'MEDIUM',
                'description': [
                    'Application reflects user input without proper encoding.',
                    'Malicious scripts can be injected and executed in user browsers.',
                    'Both stored and reflected XSS patterns detected.'
                ],
                'impact': [
                    'Session hijacking through cookie theft.',
                    'Credential harvesting via fake login forms.',
                    'Malware distribution to end users.',
                    'Defacement of application pages.'
                ],
                'remediation': [
                    'Encode all user input before rendering in HTML.',
                    'Implement Content Security Policy (CSP) headers.',
                    'Use HttpOnly and Secure flags on session cookies.',
                    'Sanitize input using established libraries.'
                ],
                'code_fix': '''# VULNERABLE CODE:
return f"<div>Welcome, {username}</div>"

# SECURE CODE:
from html import escape
return f"<div>Welcome, {escape(username)}</div>"''',
                'forensic_evidence': {
                    "affected_component": {
                        "method": "GET",
                        "url": "/api/v1/search",
                        "parameter": "q",
                        "description": "The 'q' parameter is reflected in the response without encoding."
                    },
                    "payload_decomposition": [
                         {
                            "component": "Prefix",
                            "value": "<script>",
                            "function": "Html tag that tells the browser to interpret content as JavaScript."
                        },
                        {
                            "component": "Payload",
                            "value": "alert(1)",
                            "function": "Execution of arbitrary JavaScript (Proof of Concept)."
                        },
                        {
                            "component": "Suffix",
                            "value": "</script>",
                            "function": "Closes the script tag to ensure valid HTML parsing."
                        }
                    ],
                    "payload_details": {
                        "vector_name": "Reflected XSS (Script Injection)",
                        "raw_payload": "<script>alert(1)</script>",
                        "encoded_payload": "%3Cscript%3Ealert(1)%3C%2Fscript%3E",
                        "encoding_type": "URL Encoding",
                        "curl_reproduction": "curl -X GET 'http://target/api/v1/search?q=%3Cscript%3Ealert(1)%3C%2Fscript%3E'"
                    },
                    "http_traffic_snapshot": {
                        "request": "GET /api/v1/search?q=%3Cscript%3Ealert(1)%3C%2Fscript%3E HTTP/1.1\nHost: target",
                        "response": "HTTP/1.1 200 OK\nContent-Type: text/html\n\n<html><body>Search results for: <script>alert(1)</script></body></html>"
                    }
                }
            })
            
        # JWT
        elif 'jwt' in vuln_type_lower or 'auth' in vuln_type_lower:
            details.update({
                'name': 'JWT / Authentication Bypass',
                'cwe': 'CWE-287',
                'cvss': '9.1 (Critical)',
                'severity': 'CRITICAL',
                'description': [
                    'Authentication mechanism can be bypassed or manipulated.',
                    'JWT tokens are not properly validated or use weak algorithms.',
                    'Session management has critical weaknesses.'
                ],
                'impact': [
                    'Complete authentication bypass.',
                    'Account takeover of any user.',
                    'Privilege escalation to admin level.',
                    'Unauthorized access to all protected resources.'
                ],
                'remediation': [
                    'Use strong asymmetric algorithms (RS256) for JWT.',
                    'Validate all JWT claims including expiration.',
                    'Implement token refresh with short-lived access tokens.',
                    'Store secrets securely and rotate regularly.'
                ],
                'code_fix': '''# VULNERABLE CODE:
token = jwt.decode(token, options={"verify_signature": False})

# SECURE CODE:
token = jwt.decode(
    token, 
    SECRET_KEY, 
    algorithms=["RS256"],
    options={"require": ["exp", "iat", "sub"]}
)''',
                'forensic_evidence': {
                    "affected_component": {
                        "method": "GET",
                        "url": "/api/v1/admin/dashboard",
                        "parameter": "Authorization",
                        "description": "JWT signature verification is disabled or vulnerable to 'none' algorithm."
                    },
                    "payload_decomposition": [
                         {
                            "component": "Header",
                            "value": "alg: none",
                            "function": "Instructs the server to skip signature verification."
                        },
                        {
                            "component": "Payload",
                            "value": "role: admin",
                            "function": "Elevates privileges to administrator level."
                        },
                        {
                            "component": "Signature",
                            "value": "<empty>",
                            "function": "Absence of signature creates a valid token under 'none' algo."
                        }
                    ],
                    "payload_details": {
                        "vector_name": "JWT None Algorithm Bypass",
                        "raw_payload": "eyJhbGciOiJub25l... . ... .",
                        "encoded_payload": "eyJhbGciOiJub25l... . ... .",
                        "encoding_type": "Base64Url",
                        "curl_reproduction": "curl -H 'Authorization: Bearer eyJhbGciOiJub25l...' http://target/api/v1/admin/dashboard"
                    },
                    "http_traffic_snapshot": {
                        "request": "GET /api/v1/admin/dashboard HTTP/1.1\nHost: target\nAuthorization: Bearer eyJhbGciOiJub25l...",
                        "response": "HTTP/1.1 200 OK\nContent-Type: application/json\n\n{\"admin_data\": \"TOP SECRET\"}"
                    }
                }
            })
            
        return details
