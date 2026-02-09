import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict

class JsonFormatter(logging.Formatter):

    def format(self, record: logging.LogRecord) -> str:
        log: Dict[str, Any] = {
            "severity": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        if hasattr(record, "request_id"):
            log["request_id"] = record.request_id

        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log)
    
def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)