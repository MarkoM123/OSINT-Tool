import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from services.assessment_service import AssessmentService


@pytest.mark.asyncio
async def test_assessment_pipeline_completes(db_session: AsyncSession, monkeypatch):
    service = AssessmentService(db_session)

    async def fake_query_ct(domain: str):
        return {
            "subdomains": ["app.example.com", "api.example.com"],
            "certificate_names": ["app.example.com", "api.example.com"],
        }

    async def fake_collect_dns_records(hostnames):
        return {"subdomains": hostnames, "ips": ["1.1.1.1"], "dns_records": {}, "ip_metadata": []}

    async def fake_enrich_ips(ips):
        return [{"ip": "1.1.1.1", "asn": "AS13335", "org": "Cloudflare", "country": "US", "hosting_provider": "Cloudflare", "raw": {}}]

    async def fake_whois_lookup(domain: str):
        return {"domain": domain, "created": "2020-01-01", "registrar": "Example Registrar"}

    async def fake_email_analyze(domain: str):
        return [{"title": "Missing SPF record", "description": "SPF record missing.", "evidence": "none", "evidence_source": "email", "confidence": 0.5, "severity": "high", "category": "email_security", "recommendation": "Add SPF."}]

    async def fake_tls_analyze(hosts):
        return [{"title": "Expired TLS certificate", "description": "Certificate expired.", "evidence": "tls", "evidence_source": "tls", "confidence": 0.75, "severity": "medium", "category": "technology", "recommendation": "Renew certificate."}]

    async def fake_tech_fingerprint(hosts):
        return [{"title": "Exposed outdated service", "description": "Outdated web server.", "evidence": "tech", "evidence_source": "technology", "confidence": 0.8, "severity": "medium", "category": "attack_surface", "recommendation": "Patch service."}]

    async def fake_cred_check(domain: str):
        return [{"title": "Default credentials exposed", "description": "Default login found.", "evidence": "creds", "evidence_source": "credentials", "confidence": 0.6, "severity": "high", "category": "credentials", "recommendation": "Change credentials."}]

    monkeypatch.setattr("services.assessment_service.ct_logs.query_ct", fake_query_ct)
    monkeypatch.setattr("services.assessment_service.dns.collect_dns_records", fake_collect_dns_records)
    monkeypatch.setattr("services.assessment_service.ipinfo.enrich_ips", fake_enrich_ips)
    monkeypatch.setattr("services.assessment_service.whois.lookup", fake_whois_lookup)
    monkeypatch.setattr("services.assessment_service.email_analyzer.analyze_domain", fake_email_analyze)
    monkeypatch.setattr("services.assessment_service.tls_analyzer.analyze_hosts", fake_tls_analyze)
    monkeypatch.setattr("services.assessment_service.tech_analyzer.fingerprint_hosts", fake_tech_fingerprint)
    async def fake_generate_executive_report(domain: str, score: int, category_scores: dict, findings: list, tone: str = "executive"):
        return "This is a concise executive summary for senior leadership."

    monkeypatch.setattr("services.assessment_service.cred_analyzer.check_credentials", fake_cred_check)
    monkeypatch.setattr("services.assessment_service.generate_executive_report", fake_generate_executive_report)
    monkeypatch.setattr("services.assessment_service.render_report", lambda context: b"%PDF-1.4")

    assessment_id = await service.run_full_assessment("example.com")
    assert assessment_id is not None

    result = await service.get_assessment(str(assessment_id))
    assert result is not None
    assert isinstance(result["findings"], list)
    assert len(result["findings"]) >= 4
    assert 0 <= result["score"] <= 100
    assert isinstance(result["executive_summary"], str)
    assert result["executive_summary"] != ""
