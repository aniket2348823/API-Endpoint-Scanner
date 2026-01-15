from flask import Flask, jsonify, request
from flask_cors import CORS
import time
import threading

app = Flask(__name__)
# Allow CORS so our React frontend (Port 3000) can talk to this API (Port 5001)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# --- IN-MEMORY DATABASE (Resets on restart) ---
# We use a global dictionary to simulate a database.
DATABASE = {
    "user_1": {
        "balance": 100.00,
        "coupons_used": []
    }
}

# Thread lock to simulate "Attempted" security (optional, we leave it open for the heist)
db_lock = threading.Lock()

@app.route('/api/balance', methods=['GET'])
def get_balance():
    """Returns the current balance. Frontend polls this every 1s."""
    user = DATABASE["user_1"]
    return jsonify({
        "balance": user["balance"],
        "currency": "USD"
    })

@app.route('/api/apply', methods=['POST'])
def apply_coupon():
    """
    VULNERABLE ENDPOINT
    Logic:
    1. Check if coupon is used.
    2. SLEEP (Simulate DB latency / External API call).
    3. Credit balance.
    4. Mark coupon as used.
    """
    data = request.json
    coupon_code = data.get("code")
    user = DATABASE["user_1"]

    if coupon_code != "WELCOME50":
        return jsonify({"error": "Invalid Coupon"}), 400

    # --- THE VULNERABILITY IS HERE ---
    
    # Step 1: Check Logic
    if coupon_code in user["coupons_used"]:
        return jsonify({"error": "Coupon already redeemed!"}), 403

    # Step 2: The "Race Window" (0.2s Delay)
    # This simulates a slow database query or external validation
    time.sleep(0.2)

    # Step 3: Write Logic
    user["balance"] += 50.00
    user["coupons_used"].append(coupon_code)

    return jsonify({
        "success": True, 
        "new_balance": user["balance"],
        "message": "Coupon Applied: +$50.00"
    })

@app.route('/api/reset', methods=['POST'])
def reset_db():
    """Helper to reset the demo without restarting the server."""
    DATABASE["user_1"]["balance"] = 100.00
    DATABASE["user_1"]["coupons_used"] = []
    return jsonify({"message": "System Reset", "balance": 100.00})

if __name__ == '__main__':
    # Threaded=True is default in Flask 1.0+, essential for concurrency
    print("[-] VICTIM SERVER RUNNING ON PORT 5001")
    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)
