import json
import logging
from collections import deque
from datetime import datetime

logger = logging.getLogger(__name__)

class RetroactiveRouter:
    def __init__(self):
        # Buffer: Stores last 20 requests: {requestId: {request_payload}}
        self.request_buffer = {} 
        # Rolling Log for UI: Stores last 50 transactions
        self.transaction_log = deque(maxlen=50)
        
        # High-Value Keywords that trigger specific attacks
        self.RACE_TRIGGERS = ["balance", "credit", "transfer", "amount", "role", "admin"]
        self.IDOR_TRIGGERS = ["email", "uuid", "user_id", "account_id", "profile"]

    def handle_traffic(self, packet):
        """
        Ingests traffic from the Chrome Extension.
        Packet structure: { type, requestId, ... }
        """
        packet_type = packet.get("type")
        request_id = packet.get("requestId")

        if packet_type == "REQUEST":
            # Store request for potential retroactive attack
            self.request_buffer[request_id] = packet
            
        elif packet_type == "RESPONSE":
            # This is the 'Time-Travel' moment. We analyze the RESPONSE to judge the REQUEST.
            self._analyze_response(packet, request_id)

    def _analyze_response(self, response_packet, request_id):
        # Retrieve the original request
        original_request = self.request_buffer.get(request_id)
        if not original_request:
            return # We missed the request portion, can't replay.

        body_str = response_packet.get("body", "")
        # Try to parse JSON
        try:
            body_json = json.loads(body_str)
        except:
            # Not JSON, ignore for now (or regex search text)
            return

        # 1. Check for Race Conditions (The Hammer)
        if self._matches_triggers(body_json, self.RACE_TRIGGERS):
            logger.warning(f"[TIME-TRAVELER] High-Value Target Found (Race): {original_request['url']}")
            self._log_transaction(original_request, "RACE_CANDIDATE", "Detected financial/state terms")
            # TODO: Trigger RawSocketEngine.prepare_race(original_request)

        # 2. Check for IDOR (The Doppelganger)
        if self._matches_triggers(body_json, self.IDOR_TRIGGERS):
            logger.warning(f"[TIME-TRAVELER] Identity Target Found (IDOR): {original_request['url']}")
            self._log_transaction(original_request, "IDOR_CANDIDATE", "Detected PII/UUIDs")
            # TODO: Trigger IDOR checks

        # Cleanup buffer
        if request_id in self.request_buffer:
            del self.request_buffer[request_id]

    def _matches_triggers(self, data, keywords):
        """
        Recursively checks if any key in the JSON object matches one of the keywords.
        """
        if isinstance(data, dict):
            for k, v in data.items():
                if any(trigger in k.lower() for trigger in keywords):
                    return True
                if self._matches_triggers(v, keywords):
                    return True
        elif isinstance(data, list):
            for item in data:
                if self._matches_triggers(item, keywords):
                    return True
        return False

    def _log_transaction(self, request, status, details):
        entry = {
            "id": request.get("requestId"),
            "timestamp": datetime.now().isoformat(),
            "url": request.get("url"),
            "method": request.get("method"),
            "status": status,
            "details": details
        }
        self.transaction_log.append(entry)
        # TODO: WebSocket emit 'ledger_update'

# Singleton Instance
retro_router = RetroactiveRouter()
