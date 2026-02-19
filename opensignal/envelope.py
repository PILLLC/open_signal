import uuid
from datetime import datetime

def create_event(event_type: str, source_id: str, data: dict):
    """
    Create a canonical OpenSignal event envelope (v1).

    This envelope is intentionally simple and vendor-neutral.
    """
    return {
        "id": str(uuid.uuid4()),
        "type": event_type,
        "source": source_id,
        "time": datetime.utcnow().isoformat(),
        "data": data,
        "risk": {
            "score": 0.0,
            "rules_applied": [],
            "explain": []
        },
        "schema_version": "1.0"
    }
