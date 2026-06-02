from __future__ import annotations

import json
import logging
from typing import Any, Dict, Iterable, List

import openai

from core.config import get_settings

logger = logging.getLogger("reporting.executive")

SEVERITY_PRIORITY = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}

TONE_INSTRUCTIONS = {
    "executive": "Write in a confident, advisory tone suitable for CEOs, CISOs, and IT directors.",
    "technical": "Write in a clear, professional tone for technical leadership.",
    "sales": "Write in a persuasive, business-outcome focused tone for a sales audience.",
}


def _safe_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value)


def _build_findings_summary(findings: List[Dict[str, Any]], limit: int = 5) -> str:
    ranked = sorted(
        findings,
        key=lambda item: (
            SEVERITY_PRIORITY.get(str(item.get("severity", "medium")).lower(), 2),
            float(item.get("confidence", 0.0) or 0.0),
        ),
        reverse=True,
    )
    lines: List[str] = []
    for index, finding in enumerate(ranked[:limit], start=1):
        title = _safe_text(finding.get("title")) or "Untitled finding"
        category = _safe_text(finding.get("category")) or "uncategorized"
        severity = _safe_text(finding.get("severity")) or "medium"
        confidence = float(finding.get("confidence", 0.0) or 0.0)
        recommendation = _safe_text(finding.get("recommendation")) or "No recommendation provided."
        lines.append(
            f"{index}. {title} | category: {category} | severity: {severity} | confidence: {confidence:.2f} | recommendation: {recommendation}"
        )
    return "\n".join(lines) if lines else "No findings were provided."


def _build_category_summary(category_scores: Dict[str, int]) -> str:
    entries = [f"{name}: {score}" for name, score in category_scores.items()]
    return "; ".join(entries)


def _normalize_category_name(category: str) -> str:
    return category.replace("_", " ").title()


def _build_tone_instruction(tone: str) -> str:
    return TONE_INSTRUCTIONS.get(tone.lower(), TONE_INSTRUCTIONS["executive"])


def _build_prompt(
    domain: str,
    score: int,
    category_scores: Dict[str, int],
    findings: List[Dict[str, Any]],
    tone: str,
) -> str:
    category_list = ", ".join([_normalize_category_name(name) for name in category_scores.keys()])
    report_data = {
        "domain": domain,
        "overall_score": score,
        "category_scores": category_scores,
        "exposure_categories": category_list,
        "top_findings": _build_findings_summary(findings, limit=5),
    }

    return (
        f"You are an experienced cybersecurity consultant preparing an executive report for C-suite stakeholders. "
        f"Use only the information provided below and keep the response concise, business focused, and free of technical jargon unless essential. "
        f"Return plain text only. Do not include markdown fences or code blocks. "
        f"Use headings for each section.\n\n"
        f"DATA:\n"
        f"Domain: {report_data['domain']}\n"
        f"Overall exposure score: {report_data['overall_score']}\n"
        f"Category scores: {json.dumps(report_data['category_scores'])}\n"
        f"Exposure categories: {report_data['exposure_categories']}\n"
        f"Top findings (sorted by severity and confidence):\n{report_data['top_findings']}\n\n"
        f"INSTRUCTIONS:\n"
        f"1. Executive Summary (max 200 words) - plain language, business risk focus.\n"
        f"2. Overall Risk Rating - Critical / High / Medium / Low with a short explanation.\n"
        f"3. Top 3 Risks - title, business impact, why it matters.\n"
        f"4. Top 3 Recommendations - prioritized, clear actions, executive-level language.\n"
        f"5. Exposure Breakdown - brief explanation of weakest categories.\n"
        f"6. Business Impact Statement - revenue risk, operational disruption, brand/reputation impact.\n"
        f"7. 30-Day Action Plan - concrete, realistic actions.\n"
        f"Tone guidance: {_build_tone_instruction(tone)}"
    )


def generate_executive_report(
    domain: str,
    score: int,
    category_scores: Dict[str, int],
    findings: List[Dict[str, Any]],
    tone: str = "executive",
) -> str:
    """Generate an executive report from exposure assessment data."""
    settings = get_settings()
    if not settings.openai_api_key:
        logger.error("OpenAI API key is not configured in settings.")
        raise RuntimeError("OpenAI API key is required to generate executive reports.")

    if score < 0 or score > 100:
        logger.warning("Overall score %s is out of expected range 0-100.", score)

    prompt = _build_prompt(domain, score, category_scores, findings, tone)
    openai.api_key = settings.openai_api_key

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a skilled cybersecurity consultant writing executive-level reports."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            max_tokens=700,
        )
        content = response.choices[0].message.content.strip()
        if not content:
            logger.error("OpenAI returned an empty executive report response.")
            raise RuntimeError("Executive report generation returned no content.")
        return content
    except Exception as exc:  # pragma: no cover
        logger.exception("Executive report generation failed for domain=%s", domain)
        raise RuntimeError("Failed to generate executive report") from exc
