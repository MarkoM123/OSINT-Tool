from typing import List, Dict
import uuid
from database.models.finding import Finding


def normalize_findings(raw_findings: List[Dict], assessment_id: uuid.UUID) -> List[Finding]:
	objects: List[Finding] = []
	for r in raw_findings:
		f = Finding(
			assessment_id=assessment_id,
			title=r.get("title", "Unnamed finding"),
			description=r.get("description", ""),
			evidence={"text": r.get("evidence")},
			evidence_source=r.get("evidence_source", ""),
			confidence=float(r.get("confidence", 0.0)),
			severity=r.get("severity", "medium"),
			category=r.get("category", "uncategorized"),
			recommendation=r.get("recommendation", ""),
		)
		objects.append(f)
	return objects

