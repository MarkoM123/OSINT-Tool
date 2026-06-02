from scoring.engine import compute_score


def test_compute_score_applies_category_weights():
    findings = [
        {"category": "email_security", "severity": "high", "confidence": 0.5},
        {"category": "attack_surface", "severity": "critical", "confidence": 1.0},
        {"category": "credentials", "severity": "medium", "confidence": 0.75},
    ]

    result = compute_score(findings)

    assert result["email_score"] == 90
    assert result["attack_surface_score"] == 60
    assert result["credentials_score"] == 92
    assert result["technology_score"] == 100
    assert result["reputation_score"] == 100
    assert result["overall"] == 85


def test_compute_score_never_drops_below_zero():
    findings = [
        {"category": "email_security", "severity": "critical", "confidence": 1.0},
        {"category": "email_security", "severity": "critical", "confidence": 1.0},
        {"category": "email_security", "severity": "critical", "confidence": 1.0},
    ]

    result = compute_score(findings)

    assert result["email_score"] == 0
    assert result["overall"] >= 0
