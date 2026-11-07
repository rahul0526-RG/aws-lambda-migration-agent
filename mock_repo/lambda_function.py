import json
from datetime import datetime, timezone
from typing import Any

def strtobool(val: str | bool) -> bool:
    """Convert a string representation of truth to True or False."""
    if isinstance(val, bool):
        return val
    val_str = str(val).lower()
    if val_str in ("y", "yes", "t", "true", "on", "1"):
        return True
    elif val_str in ("n", "no", "f", "false", "off", "0"):
        return False
    raise ValueError(f"invalid truth value {val!r}")

def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    current_time = datetime.now(timezone.utc).isoformat()
    is_active = strtobool(event.get("is_active", "true"))
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "status": "success",
            "timestamp": current_time,
            "active": is_active
        })
    }