#!/usr/bin/env bash
set -euo pipefail

echo "Bootstrapping OpenSignal (vendor-neutral, containerized runnable demo)..."

# --- Directories ---
mkdir -p opensignal/transport
mkdir -p opensignal/sinks
mkdir -p opensignal/rules
mkdir -p opensignal/brief
mkdir -p scripts
mkdir -p docs
mkdir -p out

# --- Package markers ---
touch opensignal/__init__.py
touch opensignal/transport/__init__.py
touch opensignal/sinks/__init__.py
touch opensignal/rules/__init__.py
touch opensignal/brief/__init__.py
touch scripts/__init__.py

# --- setup.py (proper package install; avoids PYTHONPATH hacks) ---
cat > setup.py <<'EOF'
from setuptools import setup, find_packages

setup(
    name="opensignal",
    version="0.1.0",
    packages=find_packages(),
)
EOF

# --- requirements.txt ---
cat > requirements.txt <<'EOF'
PyYAML
EOF

# --- Dockerfile (installs project as package, runs demo as module) ---
cat > Dockerfile <<'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install --no-cache-dir .

CMD ["python", "-m", "scripts.run_demo"]
EOF

# --- docker-compose.yml ---
cat > docker-compose.yml <<'EOF'
version: "3.8"

services:
  opensignal:
    build: .
    volumes:
      - ./out:/app/out
EOF

# --- README.adoc ---
cat > README.adoc <<'EOF'
= OpenSignal
Public Information Limited (PIL)

OpenSignal is a container-native, transport-agnostic reference implementation for structured public intelligence events.

== What this demo does

. Generates a small set of canonical events
. Moves them through an in-memory transport (no external broker required)
. Applies a transparent enrichment rule (explainable scoring)
. Writes artifacts to the local `out/` directory:
* `events.ndjson`
* `daily-brief.adoc`

== Quick start

[source,bash]
----
docker compose up --build
----

== Notes

This repository is intentionally vendor-neutral.
Runtime transports and sinks can be added as optional plugins without changing the event contract.
EOF

# --- docs/00-architecture.adoc ---
cat > docs/00-architecture.adoc <<'EOF'
= OpenSignal Architecture (Demo)

OpenSignal is designed to be transport-agnostic and sink-agnostic by contract.

== Core concepts

* *Event envelope:* A canonical event structure used everywhere in the system.
* *Transport:* An abstraction for moving events between components.
* *Sink:* An abstraction for persisting events to storage/analytics targets.
* *Rules:* Transparent enrichment and scoring logic with human-readable explanations.
* *Briefs:* Human-readable exports (AsciiDoc) generated from processed events.

== Demo wiring

* Transport: In-memory (single-process)
* Sink: NDJSON file output
* Brief: AsciiDoc summary export

This provides a runnable baseline that can later be extended to additional transports and sinks.
EOF

# --- opensignal/envelope.py ---
cat > opensignal/envelope.py <<'EOF'
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
EOF

# --- opensignal/transport/base.py ---
cat > opensignal/transport/base.py <<'EOF'
class EventTransport:
    """
    Transport abstraction for moving events between components.

    Implementations should provide at-least-once semantics where applicable,
    and should not mutate event structure.
    """
    def publish(self, stream: str, event: dict):
        raise NotImplementedError

    def subscribe(self, stream: str, handler):
        raise NotImplementedError
EOF

# --- opensignal/transport/memory.py ---
cat > opensignal/transport/memory.py <<'EOF'
from .base import EventTransport

class MemoryTransport(EventTransport):
    """
    In-memory transport used for the runnable demo.

    This is intentionally simple and single-process.
    """
    def __init__(self):
        self.streams = {}

    def publish(self, stream: str, event: dict):
        self.streams.setdefault(stream, []).append(event)

    def subscribe(self, stream: str, handler):
        for event in self.streams.get(stream, []):
            handler(event)
EOF

# --- opensignal/sinks/base.py ---
cat > opensignal/sinks/base.py <<'EOF'
class EventSink:
    """
    Sink abstraction for persisting processed events.
    """
    def write(self, events: list[dict]):
        raise NotImplementedError
EOF

# --- opensignal/sinks/ndjson.py ---
cat > opensignal/sinks/ndjson.py <<'EOF'
import json
from .base import EventSink

class NDJSONSink(EventSink):
    """
    Writes events to newline-delimited JSON (NDJSON).
    """
    def __init__(self, path: str):
        self.path = path

    def write(self, events: list[dict]):
        with open(self.path, "w", encoding="utf-8") as f:
            for e in events:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
EOF

# --- opensignal/rules/engine.py ---
cat > opensignal/rules/engine.py <<'EOF'
def apply_rules(event: dict):
    """
    Apply transparent enrichment rules.

    Demo rule:
    - If event.type == 'sanction_update', apply a baseline risk score.
    """
    if event.get("type") == "sanction_update":
        event["risk"]["score"] += 0.5
        event["risk"]["rules_applied"].append("base_sanction_weight")
        event["risk"]["explain"].append(
            "Baseline risk weight applied for sanction event"
        )
    return event
EOF

# --- opensignal/brief/generator.py ---
cat > opensignal/brief/generator.py <<'EOF'
def generate_brief(events: list) -> str:
    """
    Generate a simple AsciiDoc intelligence brief from processed events.
    """
    lines = ["= OpenSignal Daily Brief", ""]
    for e in events:
        lines.append(f"== {e.get('type')}")
        lines.append(f"*Source:* {e.get('source')}")
        lines.append(f"*Risk Score:* {e.get('risk', {}).get('score')}")
        lines.append("")
    return "\n".join(lines)
EOF

# --- scripts/run_demo.py ---
cat > scripts/run_demo.py <<'EOF'
from opensignal.envelope import create_event
from opensignal.transport.memory import MemoryTransport
from opensignal.rules.engine import apply_rules
from opensignal.sinks.ndjson import NDJSONSink
from opensignal.brief.generator import generate_brief

def main():
    transport = MemoryTransport()
    sink = NDJSONSink("out/events.ndjson")

    stream_name = "opensignal.normalized.v1"
    processed_events = []

    # Demo events (intentionally generic / vendor-neutral)
    events = [
        create_event("sanction_update", "public_list", {"entity": "Example Corp"}),
        create_event("policy_announcement", "public_bulletin", {"title": "New Regulation"}),
        create_event("economic_indicator_update", "public_stats", {"indicator": "GDP"})
    ]

    # Publish
    for e in events:
        transport.publish(stream_name, e)

    # Consume + enrich
    def handler(event):
        processed_events.append(apply_rules(event))

    transport.subscribe(stream_name, handler)

    # Persist outputs
    sink.write(processed_events)

    with open("out/daily-brief.adoc", "w", encoding="utf-8") as f:
        f.write(generate_brief(processed_events))

    print("OpenSignal demo complete. Outputs written to ./out")

if __name__ == "__main__":
    main()
EOF

echo ""
echo "Bootstrap complete."
echo "Next:"
echo "  docker compose up --build"
echo "Then check:"
echo "  out/events.ndjson"
echo "  out/daily-brief.adoc"