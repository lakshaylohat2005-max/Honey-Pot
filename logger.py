import json
import threading
from datetime import datetime, timezone

_lock = threading.Lock()


class EventLogger:
    def __init__(self, log_file: str = "honeypot.log"):
        self.log_file = log_file

    def log_event(self, service: str, remote_ip: str, remote_port: int, event_type: str, details: dict = None):
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": service,
            "src_ip": remote_ip,
            "src_port": remote_port,
            "event_type": event_type,
            "details": details or {},
        }

        line = json.dumps(event)

        with _lock:
            with open(self.log_file, "a") as f:
                f.write(line + "\n")

        # human-readable console mirror
        detail_str = ", ".join(f"{k}={v}" for k, v in event["details"].items())
        print(f"[{event['timestamp']}] {service.upper():5} | {remote_ip}:{remote_port} | {event_type} | {detail_str}")
