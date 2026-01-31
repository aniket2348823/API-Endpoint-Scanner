import json
import os
from datetime import datetime
from typing import List, Dict, Any

STATE_FILE = "stats.json"

class StateManager:
    def __init__(self):
        self._stats = {
            "scans": [],
            "active_scans": 0,
            "total_scans": 0,
            "vulnerabilities": 0,
            "critical": 0,
            "history": [0] * 30  # Initialize with flatline for graph
        }
        self._load()
        
    def _load(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r") as f:
                    saved_data = json.load(f)
                    # Update local stats with saved data while preserving structure
                    self._stats.update(saved_data)
                    # Ensure scans list exists
                    if "scans" not in self._stats:
                        self._stats["scans"] = []
            except Exception as e:
                print(f"[StateManager] Load Error: {e}")

    def _save(self):
        try:
            with open(STATE_FILE, "w") as f:
                json.dump(self._stats, f, indent=4)
        except Exception as e:
            print(f"[StateManager] Save Error: {e}")

    def get_stats(self):
        return self._stats

    def register_scan(self, scan_data: Dict[str, Any]):
        self._stats["scans"].insert(0, scan_data)
        self._stats["active_scans"] += 1
        self._stats["total_scans"] += 1
        self._save()

    def record_finding(self, severity: str = "Medium"):
        """Real-time update for a found vulnerability."""
        self._stats["vulnerabilities"] += 1
        
        if severity.upper() in ["CRITICAL", "HIGH"]:
            self._stats["critical"] += 1
            
        # Update history immediate for graph spike
        # We take the current total and append/update last point
        current_total = self._stats["vulnerabilities"]
        
        # Simple Logic: Append new total to history for the graph
        self._stats["history"].append(current_total)
        if len(self._stats["history"]) > 30:
            self._stats["history"].pop(0)
            
        self._save()

        
    def complete_scan(self, scan_id: str, results: List[Any], duration: float):
        self._stats["active_scans"] = max(0, self._stats["active_scans"] - 1)
        
        c = 0
        v = 0
        for r in results:
            verdict = r.get('verdict', 'SECURE')
            if 'CRITICAL' in verdict or 'LEAK' in verdict:
                c += 1
            if 'VULNERABLE' in verdict:
                v += 1
                
        self._stats["critical"] += c
        self._stats["vulnerabilities"] += v
        
        for s in self._stats["scans"]:
            if s["id"] == scan_id:
                s["status"] = "Completed"
                s["duration"] = f"{duration:.2f}s"
                s["results"] = results
                break
        
        # Add to history for graph (simulating activity point)
        self._stats["history"].append(v + c)
        if len(self._stats["history"]) > 30:
            self._stats["history"].pop(0)

        self._save()
                
    def reset_stale_scans(self):
        """Called on startup to clean up zombie scans."""
        cleaned = 0
        for s in self._stats["scans"]:
            if s["status"] == "Running":
                s["status"] = "Interrupted"
                cleaned += 1
        self._stats["active_scans"] = 0
        if cleaned > 0:
            self._save()
        return cleaned

# Singleton Instance
stats_db_manager = StateManager()
# Legacy Accessor (for backward compatibility if needed, but prefer manager)
stats_db = stats_db_manager._stats
