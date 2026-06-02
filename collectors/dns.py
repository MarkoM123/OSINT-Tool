from __future__ import annotations

import asyncio
import logging
from typing import Any

import dns.asyncresolver
import dns.exception
import dns.name
import dns.rdatatype

logger = logging.getLogger("eip.collectors.dns")

_DNS_CACHE: dict[str, dict[str, Any]] = {}


def _parse_txt_record(record: dns.rrset.RRset) -> list[str]:
    values: list[str] = []
    for item in record:
        try:
            text = item.to_text().strip('"')
        except Exception:
            text = str(item)
        values.append(text)
    return values


def _normalize_hostname(hostname: str) -> str:
    return hostname.strip().lower().rstrip('.')


async def _resolve_name(name: str, rdtype: str) -> list[str]:
    resolver = dns.asyncresolver.Resolver()
    resolver.lifetime = 5.0
    resolver.timeout = 5.0

    for attempt in range(1, 4):
        try:
            answer = await resolver.resolve(name, rdtype)
            return [str(rdata).strip() for rdata in answer]
        except dns.exception.DNSException as exc:
            logger.warning(
                "DNS %s lookup failed for %s on attempt %d: %s",
                rdtype,
                name,
                attempt,
                exc,
            )
            if attempt == 3:
                return []
            await asyncio.sleep(1 << attempt)
    return []


async def collect_dns_records(hostnames: list[str]) -> dict[str, Any]:
    normalized_hosts = sorted({_normalize_hostname(host) for host in hostnames if host})
    if not normalized_hosts:
        return {"subdomains": [], "ips": [], "dns_records": {}, "ip_metadata": []}

    cache_key = ":".join(normalized_hosts)
    if cache_key in _DNS_CACHE:
        logger.info("Using cached DNS records for %s", normalized_hosts)
        return _DNS_CACHE[cache_key]

    dns_records: dict[str, dict[str, Any]] = {}
    ip_set: set[str] = set()

    async def resolve_host(host: str) -> None:
        a_records = await _resolve_name(host, "A")
        mx_records = await _resolve_name(host, "MX")
        txt_records = await _resolve_name(host, "TXT")

        spf = next((txt for txt in txt_records if txt.lower().startswith("v=spf1")), "")
        dmarc_host = f"_dmarc.{host}"
        dmarc_records = await _resolve_name(dmarc_host, "TXT")
        dmarc = next((txt for txt in dmarc_records if txt.lower().startswith("v=dmarc1")), "")

        dns_records[host] = {
            "a": a_records,
            "mx": mx_records,
            "txt": txt_records,
            "spf": spf,
            "dmarc": dmarc,
        }
        ip_set.update(a_records)

    tasks = [resolve_host(host) for host in normalized_hosts]
    await asyncio.gather(*tasks)

    result = {
        "subdomains": normalized_hosts,
        "ips": sorted(ip_set),
        "dns_records": dns_records,
        "ip_metadata": [],
    }
    _DNS_CACHE[cache_key] = result
    return result
