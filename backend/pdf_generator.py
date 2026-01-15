from fpdf import FPDF
import json
import datetime

class PDFReport(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, 'Antigravity - Business Logic Assessment Report', 0, 0, 'L')
            self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

    def safe_text(self, text):
        return str(text).encode('latin-1', 'replace').decode('latin-1')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 16)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 12, self.safe_text(title), 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 6, self.safe_text(body))
        self.ln()

def generate_pdf(scan_data, output_path):
    pdf = PDFReport()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # 1. Title Page
    pdf.add_page()
    pdf.set_font('Arial', 'B', 24)
    pdf.cell(0, 60, '', 0, 1) # Spacing
    pdf.cell(0, 10, 'Antigravity Logic Assessment', 0, 1, 'C')
    pdf.set_font('Arial', '', 14)
    pdf.cell(0, 10, 'Autonomous Business Logic Vulnerability Scan', 0, 1, 'C')
    
    pdf.ln(40)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(40, 10, 'Scan ID:', 0, 0)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, pdf.safe_text(str(scan_data['id'])), 0, 1)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(40, 10, 'Target:', 0, 0)
    pdf.set_font('Arial', '', 12)
    
    # Extract target from result
    target = "Unknown"
    result_str = scan_data.get('result')
    results = {}
    if result_str:
        try:
            results = json.loads(result_str)
            target = results.get('target', 'Unknown')
        except: pass
    pdf.cell(0, 10, pdf.safe_text(target), 0, 1)

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(40, 10, 'Date:', 0, 0)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, pdf.safe_text(str(scan_data['timestamp'])), 0, 1)

    # Extract Vulnerabilities
    vulnerabilities = []
    if 'Scan_Report' in results:
        vulnerabilities = results['Scan_Report'].get('Vulnerabilities', [])
        if target == "Unknown":
            target = results['Scan_Report'].get('Target', 'Unknown')
    else:
        vulnerabilities = results.get('findings', [])

    # Overview Page
    pdf.add_page()
    pdf.chapter_title('Executive Overview')
    vuln_count = len(vulnerabilities)
    critical_count = sum(1 for v in vulnerabilities if v.get('Severity', v.get('severity', 'Low')).upper() in ['CRITICAL', 'HIGH'])
    
    overview_text = (f"Antigravity performed an automated business logic assessment against {target}. "
                     f"A total of {vuln_count} vulnerabilities were identified, with {critical_count} classified as Critical/High priority.\n\n"
                     "Scope of Assessment:\n"
                     " * Race Condition Analysis (concurrent state modification)\n"
                     " * Broken Access Control (IDOR / Privilege Escalation)\n"
                     " * Sensitive Data Exposure (PII / Secrets)\n"
                     " * Security Misconfiguration")
    pdf.chapter_body(overview_text)

    # Detailed Findings
    if not vulnerabilities:
        pdf.chapter_body("No significant vulnerabilities were detected.")
    else:
        for i, vuln in enumerate(vulnerabilities, 1):
            pdf.add_page()
            
            # Normalize fields
            name = vuln.get('Type', vuln.get('name', 'Unknown Issue'))
            severity = vuln.get('Severity', vuln.get('severity', 'Info')).upper()
            endpoint = vuln.get('Endpoint', vuln.get('url', target))
            evidence = vuln.get('Evidence', vuln.get('description', 'No details.'))
            endpoint_name = endpoint.split('/')[-1] if '/' in endpoint else "Endpoint"

            # 1. Executive Summary Block
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, pdf.safe_text(f"Finding #{i}: {name}"), 0, 1)
            pdf.ln(2)

            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, pdf.safe_text("1. Finding Summary"), 0, 1)
            pdf.set_font('Arial', '', 10)
            
            pdf.cell(40, 6, " * Vulnerability Title:", 0)
            pdf.cell(0, 6, pdf.safe_text(f"{name}"), 0, 1)
            
            pdf.cell(40, 6, " * Severity:", 0)
            
            # Color Coding
            cvss_color = (0, 0, 0)
            if severity == "CRITICAL": cs = (200, 0, 0)
            elif severity == "HIGH": cs = (255, 128, 0)
            elif severity == "MEDIUM": cs = (255, 191, 0)
            else: cs = (0, 128, 0)
                
            pdf.set_text_color(*cs)
            pdf.cell(0, 6, pdf.safe_text(severity), 0, 1)
            pdf.set_text_color(0, 0, 0)
            
            pdf.cell(40, 6, " * Affected Asset:", 0)
            pdf.cell(0, 6, pdf.safe_text(endpoint), 0, 1)

            # 2. Business Impact
            pdf.ln(5)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, pdf.safe_text("2. Business Impact Analysis"), 0, 1)
            pdf.set_font('Arial', '', 10)
            
            impact = "This vulnerability may allow unauthorized actions or data access."
            if "Race" in name:
                impact = "Financial Loss: Attackers can exploit the race condition to double-spend coupons, bypass transaction limits, or corrupt inventory data."
            elif "IDOR" in name or "Privilege" in name or "Access" in name:
                impact = "Data Breach: Unauthorized users can access sensitive personal information (PII) or perform actions on behalf of other users."
            elif "Secret" in name or "Key" in name:
                impact = "Infrastructure Compromise: Leaked API keys or secrets can provide full administrative access to third-party services (AWS, Stripe, etc.)."
            
            pdf.multi_cell(0, 5, pdf.safe_text(impact))
            pdf.ln(5)

            # 3. Technical Evidence
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, pdf.safe_text("3. Technical Evidence"), 0, 1)
            pdf.set_font('Arial', 'I', 9)
            pdf.cell(0, 6, "Automated Proof of Concept:", 0, 1)
            pdf.set_font('Courier', '', 9)
            pdf.set_fill_color(245, 245, 245)
            
            # Clean up evidence text
            evidence_clean = str(evidence).replace("\\n", "\n")
            pdf.multi_cell(0, 5, pdf.safe_text(evidence_clean), 1, 'L', True)
            pdf.ln(5)

            # 4. Remediation
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, pdf.safe_text("4. Recommended Remediation"), 0, 1)
            pdf.set_font('Arial', '', 10)
            
            remedy = "Review and validate all user inputs and access controls."
            if "Race" in name:
                remedy = "Implement pessimistic locking (SELECT FOR UPDATE) or optimistic locking (versioning) in the database transaction to prevent concurrent modifications."
            elif "IDOR" in name:
                remedy = "Enforce server-side authorization checks to ensure the logged-in user has permission to access the requested resource ID."
            elif "Secret" in name:
                remedy = "Rotate the exposed keys immediately and use environment variables for secret management. Remove secrets from the codebase."
            
            pdf.multi_cell(0, 5, pdf.safe_text(remedy))
            pdf.ln(5)

    pdf.output(output_path)

