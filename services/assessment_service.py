from typing import Any, List
import uuid
import asyncio
import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models.assessment import Assessment
from database.models.company import Company
from database.models.finding import Finding
from database.models.asset import Asset
from database.models.score import Score

from collectors import ct_logs, dns, ipinfo, whois
from analyzers import email as email_analyzer, tls as tls_analyzer, technologies as tech_analyzer, credentials as cred_analyzer
from findings.engine import normalize_findings
from scoring.engine import compute_score
from reporting import generate_executive_report
from reporting.pdf import render_report
from core.config import get_settings

logger = logging.getLogger("eip.assessment")

SEVERITY_PRIORITY: dict[str, int] = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}


def _safe_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _sort_key_for_finding(finding: dict[str, Any]) -> tuple[int, float]:
    severity = str(finding.get("severity", "medium")).lower()
    priority = SEVERITY_PRIORITY.get(severity, 2)
    confidence = float(finding.get("confidence", 0.0) or 0.0)
    return priority, confidence


def _prepare_executive_findings(findings: list[dict[str, Any]], limit: int = 8) -> list[dict[str, Any]]:
    sorted_findings = sorted(findings, key=_sort_key_for_finding, reverse=True)
    compact: list[dict[str, Any]] = []
    for finding in sorted_findings[:limit]:
        compact.append(
            {
                "title": _safe_text(finding.get("title")),
                "description": _safe_text(finding.get("description")),
                "evidence": _safe_text(finding.get("evidence")),
                "severity": _safe_text(finding.get("severity")),
                "category": _safe_text(finding.get("category")),
                "confidence": float(finding.get("confidence", 0.0) or 0.0),
                "recommendation": _safe_text(finding.get("recommendation")),
            }
        )
    return compact


class AssessmentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()

    async def run_full_assessment(self, domain: str) -> uuid.UUID | None:
        """Orchestrate a full assessment pipeline for a given domain.

        This method is designed to be invoked inside a Celery worker process.
        """
        assessment_id: uuid.UUID | None = None
        try:
            logger.info("Starting full assessment for domain=%s", domain)

            # load or create company
            stmt = select(Company).where(Company.domain == domain)
            res = await self.db.execute(stmt)
            company = res.scalars().first()
            if not company:
                company = Company(name=domain, domain=domain)
                self.db.add(company)
                await self.db.commit()
                await self.db.refresh(company)
                logger.info("Created company id=%s", company.id)

            # create assessment record
            assessment = Assessment(company_id=company.id, status="running", started_at=datetime.utcnow())
            self.db.add(assessment)
            await self.db.commit()
            await self.db.refresh(assessment)
            assessment_id = assessment.id
            logger.info("Created assessment id=%s", assessment_id)

            # Asset discovery
            domain = domain.strip().lower()
            ct_data = await ct_logs.query_ct(domain)
            subdomains = ct_data.get("subdomains", [])
            certificate_names = ct_data.get("certificate_names", [])
            logger.info("Found %d subdomains from crt.sh for %s", len(subdomains), domain)

            dns_data = await dns.collect_dns_records(subdomains)
            ips = dns_data.get("ips", [])
            logger.info("Resolved %d unique ips for %d hosts", len(ips), len(subdomains))

            ip_metadata = await ipinfo.enrich_ips(ips)
            logger.info("Enriched %d IPs with IP intelligence", len(ip_metadata))

            whois_data = await whois.lookup(domain)
            logger.info("Loaded domain registration metadata for %s: %s", domain, whois_data)

            assets = [{"hostname": sd, "type": "hostname"} for sd in subdomains]

            # Run analyzers
            findings: List[dict] = []
            findings.extend(await email_analyzer.analyze_domain(domain))
            findings.extend(await tls_analyzer.analyze_hosts([a["hostname"] for a in assets]))
            findings.extend(await tech_analyzer.fingerprint_hosts([a["hostname"] for a in assets]))
            findings.extend(await cred_analyzer.check_credentials(domain))

            logger.info("Collected %d raw findings", len(findings))

            # Normalize & persist findings
            normalized = normalize_findings(findings, assessment_id)
            for f in normalized:
                self.db.add(f)
            await self.db.commit()

            # Compute score
            score_result = compute_score(findings)
            score = Score(
                assessment_id=assessment_id,
                overall=score_result["overall"],
                email_score=score_result["email_score"],
                attack_surface_score=score_result["attack_surface_score"],
                credentials_score=score_result["credentials_score"],
                technology_score=score_result["technology_score"],
                reputation_score=score_result["reputation_score"],
            )
            self.db.add(score)
            assessment.score = score.overall
            assessment.executive_summary = "Unavailable"

            category_scores = {
                "email_security": score_result["email_score"],
                "attack_surface": score_result["attack_surface_score"],
                "credentials": score_result["credentials_score"],
                "technology": score_result["technology_score"],
                "reputation": score_result["reputation_score"],
            }
            top_findings = _prepare_executive_findings(findings, limit=8)

            try:
                logger.info("Generating executive summary for assessment id=%s", assessment_id)
                executive_summary = await asyncio.wait_for(
                    asyncio.to_thread(
                        generate_executive_report,
                        domain,
                        score_result["overall"],
                        category_scores,
                        top_findings,
                        "executive",
                    ),
                    timeout=30.0,
                )
                assessment.executive_summary = executive_summary
                logger.info("Executive summary generated for assessment id=%s", assessment_id)
            except Exception as exc:
                logger.warning(
                    "Executive summary generation failed for assessment id=%s: %s",
                    assessment_id,
                    exc,
                )
                assessment.executive_summary = "Unavailable"

            # Generate PDF report
            # Build report context
            top_findings = sorted(
                [
                    {
                        "title": f.title,
                        "description": f.description,
                        "severity": f.severity,
                        "category": f.category,
                        "recommendation": f.recommendation,
                    }
                    for f in normalized
                ],
                key=lambda x: {"critical": 3, "high": 2, "medium": 1, "low": 0}.get(x.get("severity", "medium"), 0),
                reverse=True,
            )[:5]

            context = {
                "domain": domain,
                "company": company.name,
                "assessment_id": str(assessment_id),
                "executive_summary": "Executive summary placeholder",
                "overall_score": score.overall,
                "top_findings": top_findings,
                "category_breakdown": {
                    "email_security": score.email_score,
                    "attack_surface": score.attack_surface_score,
                    "credentials": score.credentials_score,
                    "technology": score.technology_score,
                    "reputation": score.reputation_score,
                },
            }

            pdf_bytes = render_report(context)
            # persist report to disk for now
            import os
            report_dir = "reporting/reports"
            os.makedirs(report_dir, exist_ok=True)
            report_path = f"{report_dir}/{assessment_id}.pdf"
            with open(report_path, "wb") as fh:
                fh.write(pdf_bytes)
            logger.info("Wrote report %s", report_path)

            # finalize assessment
            assessment.status = "completed"
            assessment.finished_at = datetime.utcnow()
            self.db.add(assessment)
            await self.db.commit()
            logger.info("Completed assessment id=%s", assessment_id)
            return assessment_id

        except Exception as exc:  # pragma: no cover - ensure failures are captured
            logger.exception("Assessment failed for domain=%s", domain)
            try:
                if assessment_id:
                    stmt = select(Assessment).where(Assessment.id == assessment_id)
                    res = await self.db.execute(stmt)
                    assessment = res.scalars().first()
                    if assessment:
                        assessment.status = "failed"
                        assessment.finished_at = datetime.utcnow()
                        self.db.add(assessment)
                        await self.db.commit()
            except Exception:
                logger.exception("Failed to mark assessment failed in DB for domain=%s", domain)
            raise

    async def get_assessment(self, assessment_id: str) -> dict | None:
        stmt = select(Assessment).where(Assessment.id == assessment_id)
        res = await self.db.execute(stmt)
        assessment = res.scalars().first()
        if not assessment:
            return None

        # load findings
        fstmt = select(Finding).where(Finding.assessment_id == assessment.id)
        fres = await self.db.execute(fstmt)
        findings = [
            {
                "id": str(f.id),
                "title": f.title,
                "description": f.description,
                "evidence": f.evidence,
                "evidence_source": f.evidence_source,
                "confidence": f.confidence,
                "severity": f.severity,
                "category": f.category,
                "recommendation": f.recommendation,
            }
            for f in fres.scalars().all()
        ]

        # load score
        sstmt = select(Score).where(Score.assessment_id == assessment.id)
        sres = await self.db.execute(sstmt)
        score = sres.scalars().first()

        return {
            "id": str(assessment.id),
            "company_id": str(assessment.company_id),
            "status": assessment.status,
            "score": score.overall if score else None,
            "executive_summary": assessment.executive_summary,
            "category_scores": {
                "email_security": score.email_score if score else None,
                "attack_surface": score.attack_surface_score if score else None,
                "credentials": score.credentials_score if score else None,
                "technology": score.technology_score if score else None,
                "reputation": score.reputation_score if score else None,
            },
            "findings": findings,
            "started_at": assessment.started_at,
            "finished_at": assessment.finished_at,
        }
