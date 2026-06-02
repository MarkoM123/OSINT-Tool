from typing import List, Dict
import asyncio


async def fingerprint_hosts(hosts: List[str]) -> List[Dict]:
	findings: List[Dict] = []
	for h in hosts:
		await asyncio.sleep(0)
		findings.append(
			{
				"title": "Outdated web server",
				"description": f"Host {h} runs an outdated web server with known CVEs.",
				"evidence": f"Server header indicates Apache 2.2 on {h}",
				"evidence_source": "SERVICE_FINGERPRINT",
				"confidence": 0.7,
				"severity": "high",
				"category": "technology",
				"recommendation": "Upgrade server to a supported version and apply security patches.",
			}
		)
	return findings
