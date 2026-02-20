def generate_brief(events: list) -> str:
    lines = ["= OpenSignal Daily Brief", ""]
    for e in events:
        lines.append(f"== {e.get('type')}")
        lines.append(f"*Source:* {e.get('source')}")
        lines.append(f"*Risk Score:* {e.get('risk', {}).get('score')}")

        if e.get("risk", {}).get("rules_applied"):
            lines.append("")
            lines.append("*Applied Rules:*")
            for rule in e["risk"]["rules_applied"]:
                lines.append(f"- {rule}")

        if e.get("risk", {}).get("explain"):
            lines.append("")
            lines.append("*Explanation:*")
            for explanation in e["risk"]["explain"]:
                lines.append(f"- {explanation}")

        lines.append("")

    return "\n".join(lines)
