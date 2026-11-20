import pytest
import respx
from httpx import Response

from app.services.campaigns import (
    CAMPAIGN_PREFIX,
    create_campaign,
    next_campaign_name,
    timestamped_campaign_name,
)
from app.services.keitaro import KeitaroClient

BASE = "https://keitaro.test"

RAW_CAMPAIGN = {
    "id": 999,
    "alias": "test_sinelnikov_campaign1",
    "name": "test_sinelnikov_campaign1",
    "type": "position",
    "position": 9999,
    "state": "active",
    "group_id": 10332,
    "domain_id": 1813,
    "traffic_source_id": 836,
    "domain": "https://kylovoa.com/",
}


@pytest.fixture
async def client() -> object:
    c = KeitaroClient(base_url=BASE, api_key="test-key")
    yield c
    await c.aclose()


def test_next_name_starts_from_one() -> None:
    assert next_campaign_name([]) == f"{CAMPAIGN_PREFIX}1"


def test_next_name_increments_existing() -> None:
    names = [f"{CAMPAIGN_PREFIX}1", f"{CAMPAIGN_PREFIX}2"]

    assert next_campaign_name(names) == f"{CAMPAIGN_PREFIX}3"


def test_next_name_ignores_foreign_campaigns() -> None:
    names = ["test_banar_campaing4", "other", f"{CAMPAIGN_PREFIX}5"]

    assert next_campaign_name(names) == f"{CAMPAIGN_PREFIX}6"


def test_next_name_ignores_similar_prefixes() -> None:
    names = [f"{CAMPAIGN_PREFIX}7_extra", f"{CAMPAIGN_PREFIX}tmp"]

    assert next_campaign_name(names) == f"{CAMPAIGN_PREFIX}1"


@respx.mock
async def test_create_campaign_returns_campaign(client: KeitaroClient) -> None:
    respx.get(f"{BASE}/admin_api/v1/campaigns").mock(return_value=Response(200, json=[]))
    respx.post(f"{BASE}/admin_api/v1/campaigns").mock(return_value=Response(200, json=RAW_CAMPAIGN))
    respx.post(f"{BASE}/admin_api/v1/streams").mock(return_value=Response(200, json={"id": 1}))

    campaign = await create_campaign(client, geo="MX", offer_id=18813)

    assert campaign.id == 999
    assert campaign.name.startswith(CAMPAIGN_PREFIX)


@respx.mock
async def test_create_campaign_builds_two_streams(client: KeitaroClient) -> None:
    respx.get(f"{BASE}/admin_api/v1/campaigns").mock(return_value=Response(200, json=[]))
    respx.post(f"{BASE}/admin_api/v1/campaigns").mock(return_value=Response(200, json=RAW_CAMPAIGN))
    streams_route = respx.post(f"{BASE}/admin_api/v1/streams").mock(
        return_value=Response(200, json={"id": 1})
    )

    await create_campaign(client, geo="MX", offer_id=18813)

    assert streams_route.call_count == 2


@respx.mock
async def test_first_stream_redirects_country_to_google(
    client: KeitaroClient,
) -> None:
    respx.get(f"{BASE}/admin_api/v1/campaigns").mock(return_value=Response(200, json=[]))
    respx.post(f"{BASE}/admin_api/v1/campaigns").mock(return_value=Response(200, json=RAW_CAMPAIGN))
    streams_route = respx.post(f"{BASE}/admin_api/v1/streams").mock(
        return_value=Response(200, json={"id": 1})
    )

    await create_campaign(client, geo="MX", offer_id=18813)

    first = streams_route.calls[0].request
    body = first.read().decode()

    assert '"position":1' in body
    assert '"schema":"redirect"' in body
    assert "google.com" in body
    assert '"name":"country"' in body
    assert "MX" in body


@respx.mock
async def test_second_stream_uses_offer(client: KeitaroClient) -> None:
    respx.get(f"{BASE}/admin_api/v1/campaigns").mock(return_value=Response(200, json=[]))
    respx.post(f"{BASE}/admin_api/v1/campaigns").mock(return_value=Response(200, json=RAW_CAMPAIGN))
    streams_route = respx.post(f"{BASE}/admin_api/v1/streams").mock(
        return_value=Response(200, json={"id": 1})
    )

    await create_campaign(client, geo="MX", offer_id=18813)

    second = streams_route.calls[1].request.read().decode()

    assert '"position":2' in second
    assert '"offer_id":18813' in second
    assert '"share":100' in second


def test_timestamped_name_has_prefix() -> None:
    name = timestamped_campaign_name([])

    assert name.startswith(CAMPAIGN_PREFIX)
    assert len(name) > len(CAMPAIGN_PREFIX)


def test_timestamped_name_avoids_collision() -> None:
    first = timestamped_campaign_name([])
    second = timestamped_campaign_name([first])

    assert second != first
    assert second.endswith("_2")
