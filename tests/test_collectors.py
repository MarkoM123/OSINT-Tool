import httpx
import pytest

from collectors import ct_logs, dns, ipinfo


class DummyResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.request = httpx.Request("GET", "https://example.com")

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("HTTP error", request=self.request, response=httpx.Response(self.status_code))

    def json(self):
        return self._payload


class DummyClient:
    def __init__(self, response):
        self._response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, *args, **kwargs):
        return self._response


@pytest.mark.asyncio
async def test_query_ct_returns_structure(monkeypatch):
    payload = [{"name_value": "app.example.com"}, {"name_value": "api.example.com"}]

    def fake_client(*args, **kwargs):
        return DummyClient(DummyResponse(payload))

    monkeypatch.setattr(ct_logs.httpx, "AsyncClient", fake_client)
    result = await ct_logs.query_ct("example.com")

    assert result["subdomains"] == ["app.example.com", "api.example.com"]
    assert "certificate_names" in result


@pytest.mark.asyncio
async def test_ipinfo_enrich_handles_http_errors(monkeypatch):
    class ErrorClient(DummyClient):
        async def get(self, *args, **kwargs):
            response = httpx.Response(404, request=httpx.Request("GET", "https://ipinfo.io/1.1.1.1/json"))
            raise httpx.HTTPStatusError("Not found", request=response.request, response=response)

    monkeypatch.setattr(ipinfo.httpx, "AsyncClient", lambda *args, **kwargs: ErrorClient(None))
    result = await ipinfo.enrich_ips(["1.1.1.1"])

    assert result == []


@pytest.mark.asyncio
async def test_collect_dns_records_returns_empty_structure():
    result = await dns.collect_dns_records([])
    assert result["subdomains"] == []
    assert result["ips"] == []
    assert result["dns_records"] == {}
