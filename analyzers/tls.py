from typing import List, Dict
import asyncio


async def analyze_hosts(hosts: List[str]) -> List[Dict]:
	findings: List[Dict] = []
	for h in hosts:
		# Mock TLS checks: in production use ssl.get_server_certificate or sslyze
		await asyncio.sleep(0)
		findings.append(
			{
				"title": "Expired TLS certificate",
				"description": f"Host {h} serves an expired certificate.",
				"evidence": f"Certificate expired for {h}",
				"evidence_source": "TLS_SCAN",
				"confidence": 0.75,
				"severity": "medium",
				"category": "attack_surface",
				"recommendation": "Replace the certificate and ensure timely renewal (ACME).",
			}
		)
	return findings

