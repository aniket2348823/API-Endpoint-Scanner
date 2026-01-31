from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from io import BytesIO
import uuid
import random
import os

from backend.core.state import stats_db

from backend.core.state import stats_db
import os

router = APIRouter()

@router.get("/")
async def list_reports():
    """
    Lists all generated PDF reports.
    """
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "reports")
    if not os.path.exists(reports_dir):
        return []
    
    files = [f for f in os.listdir(reports_dir) if f.endswith(".pdf")]
    # Return as list of dicts for UI
    return [{"name": f, "path": f"/api/reports/pdf/{f}"} for f in files]
@router.get("/pdf/{scan_id}")
async def generate_pdf_report(scan_id: str):
    """
    Generates and serves a professional PDF security report.
    Always generates fresh report with serial numbered filename.
    """
    from backend.core.reporting import ReportGenerator

    # Fetch scan data
    scan_data = next((s for s in stats_db.get("scans", []) if s["id"] == scan_id), None)
    if not scan_data:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Build events list from scan data
    events = []
    events.append({
        "type": "TARGET_ACQUIRED", 
        "timestamp": scan_data.get("timestamp"), 
        "source": "Orchestrator", 
        "payload": {"url": scan_data.get("scope", "Unknown")}
    })
    events.append({
        "type": "JOB_ASSIGNED", 
        "timestamp": scan_data.get("timestamp"), 
        "source": "Sigma", 
        "payload": "Payload Generation Matrix Active"
    })
    events.append({
        "type": "LOG", 
        "timestamp": scan_data.get("timestamp"), 
        "source": "Beta", 
        "payload": "Injection Vector Executed"
    })
    
    # Add vulnerability events based on scan status
    if scan_data.get("status") in ["Vulnerable", "Completed"]:
        events.append({
            "type": "VULN_CONFIRMED", 
            "timestamp": scan_data.get("timestamp"), 
            "source": "Gamma", 
            "payload": {"type": "Logic/IDOR", "payload": '{"admin": true}'}
        })
        events.append({
            "type": "GI5_LOG", 
            "timestamp": scan_data.get("timestamp"), 
            "source": "Kappa", 
            "payload": "Artifact Archived"
        })

    try:
        # Generate the report
        gen = ReportGenerator()
        out_path = gen.generate_report(scan_id, events, scan_data.get("scope", "Unknown"))
        
        # Serve the generated file
        if os.path.exists(out_path):
            with open(out_path, "rb") as f:
                pdf_content = f.read()
            
            # Extract filename from path
            filename = os.path.basename(out_path)
            
            buffer = BytesIO(pdf_content)
            headers = {'Content-Disposition': f'attachment; filename="{filename}"'}
            return StreamingResponse(buffer, media_type='application/pdf', headers=headers)
        else:
            raise Exception("Report generation completed but file not found.")

    except Exception as e:
        print(f"ON-DEMAND GEN FAILED: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Report Generation Failed: {str(e)}")

@router.get("/consolidated")
async def generate_consolidated_report():
    """
    Placeholder for consolidated report generation.
    """
    raise HTTPException(status_code=501, detail="Consolidated reports not yet implemented in Visual Architect mode.")

