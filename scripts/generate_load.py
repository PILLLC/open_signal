# scripts/generate_load.py
#
# Usage (from project root):
#   python3 -m scripts.generate_load --n 100000 --out out/events_100k.ndjson --no-brief
#   python3 -m scripts.generate_load --n 2000 --out out/events_2k.ndjson
#
# Notes:
# - For large N, skip brief generation (it will create a massive .adoc).
# - This script uses MemoryTransport to simulate streaming-style publish/subscribe.

import argparse
import random
import time

from opensignal.envelope import create_event
from opensignal.transport.memory import MemoryTransport
from opensignal.rules.engine import apply_rules
from opensignal.sinks.ndjson import NDJSONSink


EVENT_TYPES = [
    ("sanction_update", "public_list"),
    ("economic_indicator_update", "public_stats"),
    ("policy_announcement", "public_bulletin"),
]


def main():
    parser = argparse.ArgumentParser(description="Generate lots of OpenSignal demo events.")
    parser.add_argument("--n", type=int, default=10000, help="Number of events to generate")
    parser.add_argument("--out", type=str, default="out/events_load.ndjson", help="NDJSON output path")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for repeatability")
    parser.add_argument(
        "--no-brief",
        action="store_true",
        help="Skip daily brief generation (recommended for large N)",
    )
    args = parser.parse_args()

    random.seed(args.seed)

    transport = MemoryTransport()
    sink = NDJSONSink(args.out)

    stream_name = "opensignal.normalized.v1"
    processed_events = []

    def handler(event: dict):
        processed_events.append(apply_rules(event))

    # Subscribe first (streaming pattern)
    transport.subscribe(stream_name, handler)

    t0 = time.time()

    # Generate + publish events
    for i in range(args.n):
        event_type, source_id = random.choice(EVENT_TYPES)

        if event_type == "sanction_update":
            data = {
                "entity": f"Entity {i}",
                "list": "demo_sanctions_list",
            }
        elif event_type == "economic_indicator_update":
            data = {
                "indicator": random.choice(["GDP", "inflation", "unemployment"]),
                "value": round(random.random() * 100, 4),
                "seq": i,
            }
        else:  # policy_announcement
            data = {
                "title": f"Policy bulletin {i}",
                "topic": random.choice(["finance", "trade", "security"]),
            }

        event = create_event(event_type, source_id, data)
        transport.publish(stream_name, event)

    # Persist NDJSON output
    sink.write(processed_events)

    dt = time.time() - t0
    rate = args.n / dt if dt > 0 else 0

    print(f"Generated + processed {args.n} events in {dt:.2f}s ({rate:.0f} events/sec).")
    print(f"Wrote NDJSON: {args.out}")

    # Optional brief generation (keep small!)
    if not args.no_brief:
        from opensignal.brief.generator import generate_brief

        brief_path = "out/daily-brief-load.adoc"
        with open(brief_path, "w", encoding="utf-8") as f:
            f.write(generate_brief(processed_events))

        print(f"Wrote brief: {brief_path}")


if __name__ == "__main__":
    main()