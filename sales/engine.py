from __future__ import annotations

import logging
from typing import Any

import openai

from core.config import get_settings

logger = logging.getLogger("sales.engine")

TONE_MAP = {
    "formal": "Use a polished and professional tone appropriate for senior decision makers.",
    "direct": "Use a concise and direct tone focused on business outcomes.",
    "consultative": "Use a consultative tone that emphasizes partnership and practical guidance.",
}

DEFAULT_TONE = "consultative"


def _get_openai_api_key() -> str:
    settings = get_settings()
    if not settings.openai_api_key:
        logger.error("OpenAI API key is not configured")
        raise RuntimeError("OpenAI API key is required for sales content generation.")
    return settings.openai_api_key


def _build_context(
    domain: str,
    score: int,
    category_scores: dict[str, int],
    executive_summary: str,
    top_findings: list[dict[str, Any]],
    industry: str | None = None,
) -> str:
    findings_text = []
    for index, finding in enumerate(top_findings[:5], start=1):
        finding_line = (
            f"{index}. {finding.get('title', 'Untitled')} | severity: "
            f"{finding.get('severity', 'medium')} | category: "
            f"{finding.get('category', 'uncategorized')} | recommendation: "
            f"{finding.get('recommendation', 'No recommendation provided.')}"
        )
        findings_text.append(finding_line)

    categories = ", ".join(
        [
            f"{key.replace('_', ' ').title()}: {value}"
            for key, value in category_scores.items()
        ]
    )
    industry_text = f"Industry: {industry}. " if industry else ""

    return (
        f"Domain: {domain}\n"
        f"Exposure score: {score}\n"
        f"Category scores: {categories}\n"
        f"Executive summary: {executive_summary}\n"
        f"Top findings:\n{chr(10).join(findings_text)}\n"
        f"{industry_text}"
    )


def _build_prompt(task: str, context: str, tone: str) -> str:
    tone_instruction = TONE_MAP.get(tone, TONE_MAP[DEFAULT_TONE])
    return "\n".join(
        [
            "You are a senior cybersecurity consultant and sales enablement specialist.",
            "Create persuasive, business-focused sales content from the assessment context below.",
            "Use a clear, confident tone and avoid overly technical language.",
            f"Task: {task}.",
            "",
            f"Context:\n{context}",
            "",
            "Requirements:",
            "- Keep output concise and tailored to business decision makers.",
            "- Do not include markdown code fences.",
            "- Use short, impactful sections where appropriate.",
            f"- Use the tone guidance: {tone_instruction}",
        ]
    )


def _create_completion(prompt: str) -> str:
    api_key = _get_openai_api_key()
    openai.api_key = api_key

    try:
        logger.info("Generating sales content with OpenAI")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You generate business-ready sales enablement content from "
                        "cybersecurity assessment data."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            max_tokens=700,
        )
        choice = response.choices[0]
        content = choice.message.content.strip()
        logger.info("Sales content generated successfully")
        return content
    except Exception as exc:  # pragma: no cover
        logger.exception("Failed to generate sales content")
        raise RuntimeError("Sales content generation failed") from exc


def generate_executive_snapshot(
    domain: str,
    score: int,
    category_scores: dict[str, int],
    executive_summary: str,
    top_findings: list[dict[str, Any]],
    tone: str = DEFAULT_TONE,
    industry: str | None = None,
) -> str:
    context = _build_context(
        domain,
        score,
        category_scores,
        executive_summary,
        top_findings,
        industry,
    )
    task = (
        "Create an executive snapshot: one-page summary with company domain, overall risk level, "
        "exposure score, top 3 risks, top 3 actions, and a short business summary."
    )
    prompt = _build_prompt(task, context, tone)
    return _create_completion(prompt)


def generate_discovery_brief(
    domain: str,
    score: int,
    category_scores: dict[str, int],
    executive_summary: str,
    top_findings: list[dict[str, Any]],
    tone: str = DEFAULT_TONE,
    industry: str | None = None,
) -> str:
    context = _build_context(
        domain,
        score,
        category_scores,
        executive_summary,
        top_findings,
        industry,
    )
    task = (
        "Create a discovery call brief with key risks to discuss, talking points, "
        "client questions, and technical concerns to explore."
    )
    prompt = _build_prompt(task, context, tone)
    return _create_completion(prompt)


def generate_outreach_email(
    domain: str,
    score: int,
    category_scores: dict[str, int],
    executive_summary: str,
    top_findings: list[dict[str, Any]],
    tone: str = DEFAULT_TONE,
    industry: str | None = None,
) -> str:
    context = _build_context(
        domain,
        score,
        category_scores,
        executive_summary,
        top_findings,
        industry,
    )
    task = (
        "Write a personalized cold outreach email of no more than 150 words that highlights "
        "a key risk insight and includes a clear call to action for a meeting."
    )
    prompt = _build_prompt(task, context, tone)
    return _create_completion(prompt)


def generate_linkedin_message(
    domain: str,
    score: int,
    category_scores: dict[str, int],
    executive_summary: str,
    top_findings: list[dict[str, Any]],
    tone: str = DEFAULT_TONE,
    industry: str | None = None,
) -> str:
    context = _build_context(
        domain,
        score,
        category_scores,
        executive_summary,
        top_findings,
        industry,
    )
    task = (
        "Create a LinkedIn message of no more than 300 characters that is personalized, "
        "non-salesy, and highlights one exposure issue."
    )
    prompt = _build_prompt(task, context, tone)
    return _create_completion(prompt)


def generate_proposal(
    domain: str,
    score: int,
    category_scores: dict[str, int],
    executive_summary: str,
    top_findings: list[dict[str, Any]],
    tone: str = DEFAULT_TONE,
    industry: str | None = None,
) -> str:
    context = _build_context(
        domain,
        score,
        category_scores,
        executive_summary,
        top_findings,
        industry,
    )
    task = (
        "Generate a consulting proposal draft with sections: Executive Summary, Observations, "
        "Scope of Work, Deliverables, Timeline (30/60/90 days), and a pricing placeholder."
    )
    prompt = _build_prompt(task, context, tone)
    return _create_completion(prompt)


def generate_sow(
    domain: str,
    score: int,
    category_scores: dict[str, int],
    executive_summary: str,
    top_findings: list[dict[str, Any]],
    tone: str = DEFAULT_TONE,
    industry: str | None = None,
) -> str:
    context = _build_context(
        domain,
        score,
        category_scores,
        executive_summary,
        top_findings,
        industry,
    )
    task = (
        "Create a detailed Statement of Work (SOW) that is more technical than the proposal "
        "and includes scope, roles, milestones, assumptions, and acceptance criteria."
    )
    prompt = _build_prompt(task, context, tone)
    return _create_completion(prompt)
