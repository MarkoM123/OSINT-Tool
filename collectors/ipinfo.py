from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from core.config import get_settings

logger = logging.getLogger("eip.collectors.ipinfo")
settings = get_settings()

_IPINFO_CACHE: dict[str, dict[str, Any]] = {}


def _parse_org(org_string: str | None) -> tuple[str, str]:
    if not org_string:
        return "", ""
    parts = org_string.split(" ", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return parts[0], ""


async def _fetch_ip(ip: str, client: httpx.AsyncClient) -> dict[str, Any] | None:
    if ip in _IPINFO_CACHE:
        logger.debug("Using cached ipinfo for %s", ip)
        return _IPINFO_CACHE[ip]

    headers = {}
    if settings.ipinfo_token:
        headers["Authorization"] = f"Bearer {settings.ipinfo_token}"

    url = f"https://ipinfo.io/{ip}/json"
    for attempt in range(1, 4):
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            payload = response.json()
            asn, org = _parse_org(payload.get("org"))
            metadata = {
                "ip": ip,
                "asn": asn,
                "org": org,
                "country": payload.get("country", ""),
                "hosting_provider": org,
                "raw": payload,
            }
            _IPINFO_CACHE[ip] = metadata
            return metadata
        except httpx.HTTPError as exc:
            logger.warning("ipinfo lookup failed for %s attempt %d: %s", ip, attempt, exc)
            if attempt == 3:
                logger.error("ipinfo lookup failed after retries for %s", ip)
                return None
            await asyncio.sleep(1 << attempt)
    return None


async def enrich_ips(ips: list[str]) -> list[dict[str, Any]]:
    timeout = httpx.Timeout(5.0, connect=5.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        semaphore = asyncio.Semaphore(8)

        async def worker(ip_address: str) -> dict[str, Any] | None:
            async with semaphore:
                return await _fetch_ip(ip_address, client)

        tasks = [worker(ip_addr) for ip_addr in sorted(set(ips))]
        results = await asyncio.gather(*tasks)
    return [result for result in results if result]
