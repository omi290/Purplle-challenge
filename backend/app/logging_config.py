import logging
import sys
import json
from datetime import datetime
from app.config import settings

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "name": record.name,
            "filename": record.filename,
            "line": record.lineno,
        }
        if hasattr(record, "trace_id"):
            log_entry["trace_id"] = record.trace_id
        return json.dumps(log_entry)

def setup_logging():
    log_level_str = settings.LOG_LEVEL.upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    
    # Mute third party verbose logs
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("ultralytics").setLevel(logging.WARNING)
    
    return logger
