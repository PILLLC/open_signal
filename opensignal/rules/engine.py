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
