import logging
from flask import Flask, request, jsonify, g
import threading
import time
import random

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# --- IN-MEMORY DATABASE (Resets on restart) ---
users = {
    1001: {"id": 1001, "name": "Alice Admin", "role": "admin", "balance": 1000, "coupons_used": []},
    1002: {"id": 1002, "name": "Bob User", "role": "user", "balance": 100, "coupons_used": []}
}

coupons = {
    "WELCOME50": {"code": "WELCOME50", "value": 50, "max_uses": 1}
}

# --- VULNERABILITY 1: IDOR (Insecure Direct Object Reference) ---
@app.route('/api/v1/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    VULNERABILITY: No check if the requester is authorized to view this user_id.
    A user with ID 1002 can view ID 1001 by just changing the URL.
    """
    logger.info(f"IDOR Check: Fetching User {user_id}")
    user = users.get(user_id)
    if user:
        return jsonify(user), 200
    return jsonify({"error": "User not found"}), 404

# --- VULNERABILITY 2: RACE CONDITION (TOCTOU) ---
@app.route('/api/v1/coupon/apply', methods=['POST'])
def apply_coupon():
    """
    VULNERABILITY: Time-of-Check to Time-of-Use (TOCTOU) Race Condition.
    The database read and write are separated by a simulated delay (IO), 
    and there is NO lock.
    """
    data = request.json
    user_id = data.get('user_id')
    coupon_code = data.get('coupon_code')
    
    if not user_id or not coupon_code:
        return jsonify({"error": "Missing parameters"}), 400

    user = users.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    coupon = coupons.get(coupon_code)
    if not coupon:
        return jsonify({"error": "Invalid coupon"}), 400

    # [CRITICAL STEP] Reading State (Time of Check)
    if len(user['coupons_used']) >= coupon['max_uses']:
        return jsonify({"error": "Coupon already used"}), 400

    # [SIMULATED LATENCY] The "Gap" where the Race happens
    # In real DBs, this is just network/disk latency (ms).
    # We exaggerate it slightly (100ms) to make the demo 100% reliable.
    time.sleep(0.1) 

    # [CRITICAL STEP] Writing State (Time of Use)
    # If 50 requests arrived during the sleep(), they ALL passed the check above!
    user['balance'] += coupon['value']
    user['coupons_used'].append(coupon_code)
    
    msg = f"Coupon applied! New balance: {user['balance']}"
    logger.info(msg)
    
    return jsonify({
        "status": "success",
        "message": msg,
        "new_balance": user['balance']
    }), 200

# --- VULNERABILITY 3: SENSITIVE INFO LEAK ---
@app.route('/api/v1/config', methods=['GET'])
def get_config():
    """
    VULNERABILITY: Exposing internal config/env vars.
    """
    return jsonify({
        "environment": "production",
        "debug": True,
        "aws_key": "AKIAIOSFODNN7EXAMPLE", # Fake key detection
        "db_host": "10.0.0.5"
    }), 200

@app.route('/', methods=['GET'])
def home():
    return """
    <html>
    <head><title>Vulnerable Shop</title></head>
    <body>
        <h1>Vulnerable Shop API</h1>
        <ul>
            <li><a href="/api/v1/user/1001">User 1001</a></li>
            <li><a href="/api/v1/user/1002">User 1002</a></li>
            <li><a href="/api/v1/config">Config</a></li>
            <!-- Race Condition Target -->
            <li>
                <form action="/api/v1/coupon/apply" method="POST">
                    <input type="text" name="user_id" value="1002">
                    <input type="text" name="coupon_code" value="WELCOME50">
                    <input type="submit" value="Apply Coupon">
                </form>
            </li>
        </ul>
    </body>
    </html>
    """, 200

if __name__ == '__main__':
    # Run on port 5001 to avoid conflict with Scanner Backend (5000)
    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)
