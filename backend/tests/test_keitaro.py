import json
from collections.abc import AsyncGenerator

import httpx
import pytest
import respx

from app.services.keitaro import KeitaroClient, KeitaroError, KeitaroNotFound

BASE = "https://keitaro.test"


@pytest.fixture
async def client() -> AsyncGenerator[KeitaroClient, None]:
    c = KeitaroClient(base_url=BASE, api_key="test-key")
    yield c
    await c.aclose()


@respx.mock
async def test_sends_api_key_header(client: KeitaroClient) -> None:
    route = respx.get(f"{BASE}/admin_api/v1/campaigns").mock(
        return_value=httpx.Response(200, json=[])
    )
    await client.get_campaigns()
    assert route.calls.last.request.headers["Api-Key"] == "test-key"


@respx.mock
async def test_get_campaigns_returns_list(client: KeitaroClient) -> None:
    respx.get(f"{BASE}/admin_api/v1/campaigns").mock(
        return_value=httpx.Response(
            200,
            json=[{"id": 1, "name": "first"}, {"id": 2, "name": "second"}],
        )
    )
    campaigns = await client.get_campaigns()
    assert isinstance(campaigns, list)
    assert len(campaigns) == 2
    assert campaigns[0]["name"] == "first"


@respx.mock
async def test_get_campaign_returns_payload(client: KeitaroClient) -> None:
    respx.get(f"{BASE}/admin_api/v1/campaigns/42").mock(
        return_value=httpx.Response(200, json={"id": 42, "name": "test"})
    )
    campaign = await client.get_campaign(42)
    assert campaign["id"] == 42


@respx.mock
async def test_create_campaign_posts_json(client: KeitaroClient) -> None:
    route = respx.post(f"{BASE}/admin_api/v1/campaigns").mock(
        return_value=httpx.Response(200, json={"id": 1})
    )
    result = await client.create_campaign({"name": "test"})
    assert result["id"] == 1
    assert json.loads(route.calls.last.request.content) == {"name": "test"}


@respx.mock
async def test_get_offers_returns_list(client: KeitaroClient) -> None:
    respx.get(f"{BASE}/admin_api/v1/offers").mock(
        return_value=httpx.Response(200, json=[{"id": 7, "name": "offer"}])
    )
    offers = await client.get_offers()
    assert offers[0]["id"] == 7


@respx.mock
async def test_not_found_raises_specific_error(client: KeitaroClient) -> None:
    respx.get(f"{BASE}/admin_api/v1/campaigns/999").mock(
        return_value=httpx.Response(404, json={"error": "not found"})
    )
    with pytest.raises(KeitaroNotFound):
        await client.get_campaign(999)


@respx.mock
async def test_server_error_raises_keitaro_error(client: KeitaroClient) -> None:
    respx.get(f"{BASE}/admin_api/v1/campaigns").mock(return_value=httpx.Response(500, text="boom"))
    with pytest.raises(KeitaroError) as exc_info:
        await client.get_campaigns()
    assert exc_info.value.status_code == 500


@respx.mock
async def test_empty_response_returns_none(client: KeitaroClient) -> None:
    respx.get(f"{BASE}/admin_api/v1/campaigns").mock(return_value=httpx.Response(204))
    result = await client.get_campaigns()
    assert result is None


@respx.mock
async def test_timeout_raises_keitaro_error(client: KeitaroClient) -> None:
    respx.get(f"{BASE}/admin_api/v1/campaigns").mock(
        side_effect=httpx.TimeoutException("timed out")
    )
    with pytest.raises(KeitaroError) as exc_info:
        await client.get_campaigns()
    assert "timeout" in str(exc_info.value).lower()


@respx.mock
async def test_connection_error_raises_keitaro_error(client: KeitaroClient) -> None:
    respx.get(f"{BASE}/admin_api/v1/campaigns").mock(
        side_effect=httpx.ConnectError("connection refused")
    )
    with pytest.raises(KeitaroError) as exc_info:
        await client.get_campaigns()
    assert "connection" in str(exc_info.value).lower()


@respx.mock
async def test_get_streams_uses_campaign_path(client: KeitaroClient) -> None:
    route = respx.get(f"{BASE}/admin_api/v1/campaigns/42/streams").mock(
        return_value=httpx.Response(200, json=[{"id": 1, "position": 1}])
    )
    streams = await client.get_streams(42)
    assert streams[0]["id"] == 1
    assert route.called


@respx.mock
async def test_get_domains(client: KeitaroClient) -> None:
    respx.get(f"{BASE}/admin_api/v1/domains").mock(
        return_value=httpx.Response(200, json=[{"id": 1813, "name": "example.com"}])
    )
    domains = await client.get_domains()
    assert domains[0]["id"] == 1813


@respx.mock
async def test_get_groups_sends_type_param(client: KeitaroClient) -> None:
    route = respx.get(f"{BASE}/admin_api/v1/groups", params={"type": "campaigns"}).mock(
        return_value=httpx.Response(200, json=[{"id": 9799, "name": "group"}])
    )
    groups = await client.get_groups("campaigns")
    assert groups[0]["id"] == 9799
    assert route.calls.last.request.url.params["type"] == "campaigns"


@respx.mock
async def test_get_traffic_sources(client: KeitaroClient) -> None:
    respx.get(f"{BASE}/admin_api/v1/traffic_sources").mock(
        return_value=httpx.Response(200, json=[{"id": 836, "name": "FORTESTS"}])
    )
    sources = await client.get_traffic_sources()
    assert sources[0]["name"] == "FORTESTS"
