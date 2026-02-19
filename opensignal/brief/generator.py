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
