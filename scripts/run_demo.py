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

    events = [
        create_event("sanction_update", "public_list", {"entity": "Example Corp"}),
        create_event("policy_announcement", "public_bulletin", {"title": "New Regulation"}),
        create_event("economic_indicator_update", "public_stats", {"indicator": "GDP"}),
    ]

    for e in events:
        transport.publish(stream_name, e)

    def handler(event):
        processed_events.append(apply_rules(event))

    transport.subscribe(stream_name, handler)

    sink.write(processed_events)

    with open("out/daily-brief.adoc", "w", encoding="utf-8") as f:
        f.write(generate_brief(processed_events))

    print(f"OpenSignal demo complete. Processed {len(processed_events)} events. Outputs written to ./out")

if __name__ == "__main__":
    main()