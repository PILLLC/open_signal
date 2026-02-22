# scripts/run_demo.py
#
# Usage (from project root):
#   python3 -m scripts.run_demo
#   python3 -m scripts.run_demo --n 10000
#   python3 -m scripts.run_demo --n 50000 --no-brief
#

import argparse
import time

from opensignal.envelope import create_event
from opensignal.transport.memory import MemoryTransport
from opensignal.rules.engine import apply_rules
from opensignal.sinks.ndjson import NDJSONSink
from opensignal.brief.generator import generate_brief


def main():
    parser = argparse.ArgumentParser(description="Run OpenSignal demo pipeline.")
    parser.add_argument("--n", type=int, default=3, help="Number of events to generate")
    parser.add_argument(
        "--no-brief",
        action="store_true",
        help="Skip daily brief generation (recommended for large N)",
    )
    args = parser.parse_args()

    transport = MemoryTransport()
    sink = NDJSONSink("out/events.ndjson")

    stream_name = "opensignal.normalized.v1"
    processed_events = []

    # Streaming-style handler
    def handler(event: dict):
        processed_events.append(apply_rules(event))

    # Subscribe before publishing
    transport.subscribe(stream_name, handler)

    t0 = time.time()

    # Generate events
    for i in range(args.n):
        if i % 3 == 0:
            event = create_event(
                "sanction_update",
                "public_list",
                {"entity": f"Entity {i}"}
            )
        elif i % 3 == 1:
            event = create_event(
                "economic_indicator_update",
                "public_stats",
                {"indicator": "GDP", "seq": i}
            )
        else:
            event = create_event(
                "policy_announcement",
                "public_bulletin",
                {"title": f"Policy {i}"}
            )

        transport.publish(stream_name, event)

    # Persist NDJSON output
    sink.write(processed_events)

    dt = time.time() - t0
    rate = args.n / dt if dt > 0 else 0

    print(
        f"OpenSignal demo complete. "
        f"Processed {len(processed_events)} events in {dt:.2f}s "
        f"({rate:.0f} events/sec)."
    )
    print("NDJSON written to ./out/events.ndjson")

    # Optional brief generation
    if not args.no_brief:
        with open("out/daily-brief.adoc", "w", encoding="utf-8") as f:
            f.write(generate_brief(processed_events))
        print("Brief written to ./out/daily-brief.adoc")


if __name__ == "__main__":
    main()