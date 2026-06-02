# Sales Enablement Module

## Overview

The Sales Enablement module converts exposure assessment results into business-ready sales collateral. It is designed for the Exposure Intelligence Platform (EIP) to support sales teams, cybersecurity consultants, and solution architects with content that turns technical findings into opportunity-focused narratives.

This module sits downstream of the assessment pipeline and uses AI to generate:

- executive snapshots
- discovery call briefs
- outreach emails
- LinkedIn messages
- proposal drafts
- statements of work

## Inputs

The engine requires a consistent assessment payload with business-context fields.

Required inputs:

- `domain` — the assessed company domain.
- `score` — the exposure score (0–100).
- `category_scores` — category breakdown scores for exposure dimensions.
- `executive_summary` — business-focused summary of the assessment.
- `top_findings` — selected top findings with title, severity, category, and recommendation.

Example input:

```python
payload = {
    "domain": "example.com",
    "score": 42,
    "category_scores": {
        "email_security": 60,
        "attack_surface": 35,
        "credentials": 50,
        "technology": 45,
        "reputation": 55,
    },
    "executive_summary": "Critical exposure in email and external attack surface. Immediate remediation is required to reduce business risk.",
    "top_findings": [
        {
            "title": "Missing SPF record",
            "severity": "high",
            "category": "email_security",
            "recommendation": "Implement SPF and enforce DMARC policies.",
        },
        {
            "title": "Unmanaged external hosts",
            "severity": "critical",
            "category": "attack_surface",
            "recommendation": "Review and secure all public-facing services.",
        },
        {
            "title": "Weak credential hygiene",
            "severity": "medium",
            "category": "credentials",
            "recommendation": "Enforce MFA and rotate exposed credentials.",
        },
    ],
}
```

## Available Functions

### `generate_executive_snapshot(...)`

- **Purpose:** Create a one-page executive summary for decision makers.
- **Input:** `domain`, `score`, `category_scores`, `executive_summary`, `top_findings`, optional `tone`, optional `industry`.
- **Output:** A concise, business-ready paragraph or report-style summary.

### `generate_discovery_brief(...)`

- **Purpose:** Produce a call-ready brief for sales discovery conversations.
- **Input:** same payload as above.
- **Output:** Notes that include risks, talking points, client questions, and technical concerns.

### `generate_outreach_email(...)`

- **Purpose:** Generate a short, personalized cold email.
- **Input:** same payload as above.
- **Output:** A <150-word email with risk insight and CTA.

### `generate_linkedin_message(...)`

- **Purpose:** Create a concise LinkedIn outreach message.
- **Input:** same payload as above.
- **Output:** A personalized message under 300 characters.

### `generate_proposal(...)`

- **Purpose:** Draft a consulting proposal.
- **Input:** same payload as above.
- **Output:** A structured proposal with executive summary, scope, deliverables, timeline, and pricing placeholder.

### `generate_sow(...)`

- **Purpose:** Create a detailed Statement of Work (SOW).
- **Input:** same payload as above.
- **Output:** A more technical, disciplined SOW with scope, milestones, assumptions, and acceptance criteria.

## Example Usage (Python)

```python
from sales.engine import (
    generate_executive_snapshot,
    generate_discovery_brief,
    generate_outreach_email,
    generate_linkedin_message,
    generate_proposal,
    generate_sow,
)

payload = {
    "domain": "example.com",
    "score": 42,
    "category_scores": {
        "email_security": 60,
        "attack_surface": 35,
        "credentials": 50,
        "technology": 45,
        "reputation": 55,
    },
    "executive_summary": "Critical exposure in email and external attack surface. Immediate remediation is required to reduce business risk.",
    "top_findings": [
        {
            "title": "Missing SPF record",
            "severity": "high",
            "category": "email_security",
            "recommendation": "Implement SPF and enforce DMARC policies.",
        },
        {
            "title": "Unmanaged external hosts",
            "severity": "critical",
            "category": "attack_surface",
            "recommendation": "Review and secure all public-facing services.",
        },
        {
            "title": "Weak credential hygiene",
            "severity": "medium",
            "category": "credentials",
            "recommendation": "Enforce MFA and rotate exposed credentials.",
        },
    ],
}

snapshot = generate_executive_snapshot(**payload)
brief = generate_discovery_brief(**payload)
email = generate_outreach_email(**payload)
linkedin = generate_linkedin_message(**payload)
proposal = generate_proposal(**payload)
sow = generate_sow(**payload)

print(snapshot)
print(email)
```

## Output Use Cases

- **Sales outreach:** Use email and LinkedIn templates to initiate conversations.
- **Consulting proposals:** Provide executive summaries and proposal drafts to prospects.
- **Client presentations:** Turn assessment findings into business-focused slides or one-pagers.
- **Lead qualification:** Use discovery briefs to prioritize deals and tailor follow-up.

## Tone Customization

The module supports a `tone` parameter:

- `formal` — polished, executive presentation.
- `direct` — concise, outcome-focused messaging.
- `consultative` — collaborative, solution-oriented guidance.

Use the tone parameter to align content with your audience and sales motion.

## Best Practices

- **Structure inputs cleanly:** Use the same field names and normalized categories.
- **Keep top findings focused:** Select the 3–5 highest-severity, highest-confidence findings.
- **Prioritize business impact:** Ensure recommendations are framed as risk reduction actions.
- **Use concise executive summaries:** Short summaries improve AI relevance.
- **Validate outputs:** Review generated copy for client-specific details and compliance.

## Integration Notes

### API Layer

Integrate the sales engine after assessment completion or on demand. Use assessment payloads returned by the API to populate the engine inputs.

### Dashboard

Render generated outputs in a sales enablement view or content library. Offer buttons such as `Generate Proposal` and `Create Outreach Email`.

### CRM Integration

Push generated content into CRM systems for follow-up and opportunity tracking:

- **Notion:** store snapshots, call briefs, and proposal drafts in the opportunity workspace.
- **HubSpot:** attach outreach email text and call brief notes to the deal record.

---

This README is intended to help developers and business users apply the Sales Enablement module consistently and efficiently.