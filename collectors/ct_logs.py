from __future__ import annotations

import asyncio
import httpx
import logging
from typing import Any

logger = logging.getLogger("eip.collectors.ct_logs")

_CRT_CACHE: dict[str, dict[str, list[str]]] = {}


async def query_ct(domain: str) -> dict[str, list[str]]:
    normalized = domain.strip().lower()
    if normalized in _CRT_CACHE:
        logger.info("Using cached crt.sh results for %s", normalized)
        return _CRT_CACHE[normalized]

    url = "https://crt.sh/"
    params = {"q": f"%.{normalized}", "output": "json"}
    timeout = httpx.Timeout(5.0, connect=5.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        for attempt in range(1, 4):
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                entries = response.json()
                logger.info("crt.sh returned %d entries for %s", len(entries), normalized)
                break
            except (httpx.HTTPError, ValueError) as exc:
                logger.warning("crt.sh attempt %d failed for %s: %s", attempt, normalized, exc)
                if attempt == 3:
                    logger.error("crt.sh query failed after retries for %s", normalized)
                    return {"subdomains": [], "certificate_names": []}
                await asyncio.sleep(1 << attempt)
        else:
            return {"subdomains": [], "certificate_names": []}

    subdomains: set[str] = set()
    certificate_names: set[str] = set()

    if isinstance(entries, list):
        for row in entries:
            name_value = row.get("name_value")
            if not name_value:
                continue
            for name in str(name_value).split("\n"):
                name = name.strip().lower()
                if name:
                    certificate_names.add(name)
                    if name.endswith(f".{normalized}") or name == normalized:
                        subdomains.add(name)

    result = {
        "subdomains": sorted(subdomains),
        "certificate_names": sorted(certificate_names),
    }
    _CRT_CACHE[normalized] = result
    return result
