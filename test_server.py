# test_server.py (Temporary - Just to test the extension)
from flask import Flask
from flask_sock import Sock
import json

app = Flask(__name__)
sock = Sock(app)

print("[-] ANTIGRAVITY RECEIVER LISTENING ON PORT 5000...")

@sock.route('/stream')
def stream(ws):
    while True:
        data = ws.receive()
        if data:
            packet = json.loads(data)
            if packet.get("type") == "ping": continue
            
            # VISUAL PROOF
            print(f"\n[+] INTERCEPTED: {packet.get('method')} {packet.get('url')}")
            print(f"    Response: {str(packet.get('response_body'))[:100]}...")

if __name__ == "__main__":
    app.run(port=5000)
