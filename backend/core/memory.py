import json
import os
import time
from typing import Dict, Any, List
from threading import Lock

class BlackBoxRecorder:
    """
    The Flight Recorder of the Organism.
    Persists State to Disk (JSON) so Agent Kappa can 'Remember'.
    """
    def __init__(self, storage_file="hive_memory.json"):
        self.storage_file = storage_file
        self.lock = Lock()
        self.memory = self._load_memory()

    def _load_memory(self) -> Dict[str, Any]:
        if not os.path.exists(self.storage_file):
            return {"scans": [], "vectors": {}, "system_stats": []}
        try:
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {"scans": [], "vectors": {}, "system_stats": []}

    def _save_memory(self):
        """Atomic write to prevent corruption."""
        with self.lock:
            temp_file = f"{self.storage_file}.tmp"
            with open(temp_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
            os.replace(temp_file, self.storage_file)

    def record_scan_result(self, result_packet: Dict):
        """Kappa uses this to archive successful attacks."""
        entry = {
            "timestamp": time.time(),
            "target": result_packet.get("target"),
            "vuln_type": result_packet.get("vulnerabilities", [{}])[0].get("name", "Unknown"),
            "payload": result_packet.get("data", {}).get("payload", "N/A"),
            "agent": result_packet.get("source_agent")
        }
        self.memory["scans"].append(entry)
        
        # Update Vector Knowledge (Mock Vector DB)
        tech_stack = result_packet.get("data", {}).get("tech_stack", "generic")
        if tech_stack not in self.memory["vectors"]:
            self.memory["vectors"][tech_stack] = []
        self.memory["vectors"][tech_stack].append(entry)
        
        self._save_memory()

    def recall_tactics(self, tech_stack: str) -> List[Dict]:
        """Kappa uses this to suggest attacks."""
        return self.memory["vectors"].get(tech_stack, [])

# Global Instance
recorder = BlackBoxRecorder()
