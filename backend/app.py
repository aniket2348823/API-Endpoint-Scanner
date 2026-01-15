from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import scan_engine
import db
import logging
from antigravity.orchestrator import ScanOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
val = CORS(app) # Enable CORS for all routes

# Initialize SocketIO (Async Mode: eventlet/gevent recommended)
# cors_allowed_origins="*" is critical for the snippet to work from any domain
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize DB
db.init_db()

@app.route('/')
def home():
    return jsonify({"status": "Antigravity Engine Online", "version": "2.0 (SocketIO Enabled)"})

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify(scan_engine.scan_manager.get_status())

@app.route('/api/history', methods=['GET'])
def get_history():
    history = db.get_history()
    return jsonify(history)

@app.route('/api/report/<int:scan_id>', methods=['GET'])
def download_report(scan_id):
    report_path = scan_engine.scan_manager.generate_report(scan_id)
    if report_path and os.path.exists(report_path):
        return send_file(report_path, as_attachment=True)
    else:
        return jsonify({"error": "Report generation failed"}), 500

@app.route('/api/scan', methods=['POST'])
def start_scan():
    data = request.json
    target_url = data.get('target_url')
    scan_mode = data.get('scan_mode', 'Standard')
    
    if not target_url:
        return jsonify({"status": "error", "message": "Target URL is required"}), 400

    if scan_engine.scan_manager.start_scan(target_url, scan_mode=scan_mode):
        return jsonify({"status": "started", "message": f"Scan started on {target_url} (Mode: {scan_mode})"})
    else:
        return jsonify({"status": "error", "message": "A scan is already in progress."}), 409

# websocket Route for "Ghost-in-the-Browser" Traffic Mirror
@socketio.on('connect')
def handle_connect():
    logger.info("Ghost-in-the-Browser Interceptor Connected")
    emit('status', {'msg': 'Antigravity Uplink Established'})

@socketio.on('message')
def handle_message(data):
    # This handles the raw JSON sent by the JS snippet
    # data structure: { 'source': url, 'type': 'FETCH'/'XHR', 'method': ..., 'url': ..., 'body': ... }
    if isinstance(data, str):
        import json
        try:
            data = json.loads(data)
        except:
             pass
             
    if isinstance(data, dict):
        # 1. Log to console/dashboard
        msg = f"[TRAFFIC] {data.get('method')} {data.get('url')}"
        logger.info(msg)
        
        # Emit to Frontend Dashboard (Real-time visualization)
        socketio.emit('traffic_log', data)
        
        # 2. Feed to Retroactive Router (The Time-Traveler)
        from core.retro_router import retro_router
        retro_router.handle_traffic(data)
        if retro_router.transaction_log:
            latest = retro_router.transaction_log[-1]
            socketio.emit('ledger_update', latest)
        
        # 3. Feed to Orchestrator (Legacy Support)
        # scan_engine.scan_manager.analyze_realtime_traffic(data)

@socketio.on('replay_race')
def handle_replay(data):
    # data = { 'id': 'req_123' }
    logger.info(f"[AUDITOR] Replay Requested for {data.get('id')}")
    from core.retro_router import retro_router
    from core.raw_socket import raw_hammer
    
    # In a real scenario, we'd fetch the FULL request object from history/db
    # For now, we use the buffer (but the buffer might have expired).
    # Ideally, retro_router should persist candidates or we pass the full request back from UI.
    # To keep it robust, let's assume the UI passes the essential request details back 
    # OR retro_router kept it in a 'candidates' list (not just the rolling buffer).
    
    # For this Sprint, we will rely on client sending back the request details or retro_router finding it.
    # Let's use retro_router's buffer if available, or just fail safely.
    req_id = data.get('id')
    # Use the buffer
    # Note: request_buffer deletes after analysis in current implementation.
    # We should probably KEEP candidates in a separate list in retro_router.
    pass

if __name__ == '__main__':
    # Use socketio.run instead of app.run
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
