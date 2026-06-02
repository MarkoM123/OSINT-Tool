from typing import Any


def _get_field(f: Any, key: str, default=None):
    # support both dict-like and object-like findings
    if isinstance(f, dict):
        return f.get(key, default)
    return getattr(f, key, default)


def compute_score(findings: list[Any]) -> dict[str, int]:
    # Categories and weights
    weights: dict[str, float] = {
        "email_security": 0.25,
        "attack_surface": 0.25,
        "credentials": 0.20,
        "technology": 0.15,
        "reputation": 0.15,
    }

    severity_impact: dict[str, int] = {
        "critical": 40,
        "high": 20,
        "medium": 10,
        "low": 5,
    }

    # initialize per-category scores at 100
    category_scores: dict[str, float] = {k: 100.0 for k in weights}

    for f in findings:
        cat = _get_field(f, "category", "uncategorized")
        if cat not in category_scores:
            continue
        sev = _get_field(f, "severity", "medium") or "medium"
        conf = float(_get_field(f, "confidence", 0.0) or 0.0)
        impact = severity_impact.get(str(sev).lower(), 10)
        deduction = impact * conf
        category_scores[cat] -= deduction

    # floor to 0 and integer
    for k in category_scores:
        category_scores[k] = max(0.0, category_scores[k])

    # weighted overall
    overall: float = 0.0
    for k, w in weights.items():
        overall += category_scores.get(k, 0.0) * w

    overall = max(0, int(overall))

    result = {
        "overall": overall,
        "email_score": int(category_scores["email_security"]),
        "attack_surface_score": int(category_scores["attack_surface"]),
        "credentials_score": int(category_scores["credentials"]),
        "technology_score": int(category_scores["technology"]),
        "reputation_score": int(category_scores["reputation"]),
    }
    return result
