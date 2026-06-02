from __future__ import annotations

import asyncio
import logging

import httpx

logger = logging.getLogger("eip.collectors.whois")


async def lookup(domain: str) -> dict[str, str]:
    normalized = domain.strip().lower()
    url = f"https://rdap.org/domain/{normalized}"
    timeout = httpx.Timeout(5.0, connect=5.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        for attempt in range(1, 4):
            try:
                response = await client.get(url)
                response.raise_for_status()
                payload = response.json()
                registrar_field = payload.get("registrar")
                registrar = (
                    registrar_field.get("name", "")
                    if isinstance(registrar_field, dict)
                    else registrar_field or ""
                )
                created = payload.get("events", [])
                created_date = ""
                if isinstance(created, list):
                    for event in created:
                        if event.get("eventAction") == "registration":
                            created_date = event.get("eventDate", "")
                            break
                return {"registrar": registrar, "created": created_date}
            except httpx.HTTPError as exc:
                logger.warning(
                    "WHOIS lookup failed for %s attempt %d: %s",
                    normalized,
                    attempt,
                    exc,
                )
                if attempt == 3:
                    logger.error(
                        "WHOIS lookup failed after retries for %s",
                        normalized,
                    )
                    return {"registrar": "", "created": ""}
                await asyncio.sleep(1 << attempt)
    return {"registrar": "", "created": ""}
