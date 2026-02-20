def apply_rules(event: dict):
    """
    Apply transparent enrichment rules.

    Demo rules:
    - If event.type == 'economic_indicator_update', apply baseline 0.2
    - If event.type == 'sanction_update', apply baseline 0.5
    """

    if event.get("type") == "economic_indicator_update":
        event["risk"]["score"] += 0.2
        event["risk"]["rules_applied"].append("economic_baseline")
        event["risk"]["explain"].append(
            "Baseline weight for economic indicator"
        )

    if event.get("type") == "sanction_update":
        event["risk"]["score"] += 0.5
        event["risk"]["rules_applied"].append("base_sanction_weight")
        event["risk"]["explain"].append(
            "Baseline risk weight applied for sanction event"
        )

    return event