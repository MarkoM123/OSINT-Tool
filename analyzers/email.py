import asyncio


async def analyze_domain(domain: str) -> list[dict]:
    # Mock analysis: in production check DNS for SPF, DKIM, DMARC records
    await asyncio.sleep(0)
    return [
        {
            "title": "DMARC not configured",
            "description": (
                f"Domain {domain} has no DMARC record detected."
            ),
            "evidence": f"No DMARC TXT record for {domain}",
            "evidence_source": "DNS",
            "confidence": 0.8,
            "severity": "high",
            "category": "email_security",
            "recommendation": (
                "Publish a DMARC policy (p=quarantine or p=reject) "
                "and monitor aggregate reports."
            ),
        }
    ]
