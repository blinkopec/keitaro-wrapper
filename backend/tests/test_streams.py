import pytest
import respx
from httpx import Response

from app.services.keitaro import KeitaroClient
from app.services.streams import (
    OfferNotInStream,
    StreamNotFound,
    add_offer,
    rebalance_shares,
    redistribute,
    remove_offer,
)

BASE = "https://keitaro.test"
CAMPAIGN_ID = 1
STREAM_ID = 10


def _stream_payload(offers: list[tuple[int, int]]) -> dict:
    return {
        "id": STREAM_ID,
        "campaign_id": CAMPAIGN_ID,
        "name": "Offer Stream",
        "type": "regular",
        "position": 2,
        "state": "active",
        "schema": "landings",
        "action_type": "http",
        "filters": [],
        "offers": [
            {
                "id": index + 1,
                "stream_id": STREAM_ID,
                "offer_id": offer_id,
                "state": "active",
                "share": share,
            }
            for index, (offer_id, share) in enumerate(offers)
        ],
    }


@pytest.fixture
async def client() -> object:
    c = KeitaroClient(base_url=BASE, api_key="test-key")
    yield c
    await c.aclose()


def test_redistribute_keeps_total() -> None:
    for count in range(1, 20):
        values = redistribute(100, count)
        assert sum(values) == 100
        assert len(values) == count


def test_redistribute_handles_zero() -> None:
    assert redistribute(100, 0) == []


def test_rebalance_three_offers() -> None:
    assert rebalance_shares([1, 2, 3]) == [34, 33, 33]


def test_rebalance_single_offer_gets_all() -> None:
    assert rebalance_shares([1]) == [100]


def test_rebalance_two_offers() -> None:
    assert rebalance_shares([1, 2]) == [50, 50]


def test_rebalance_seven_offers_sums_to_hundred() -> None:
    values = rebalance_shares(list(range(7)))

    assert sum(values) == 100


@respx.mock
async def test_add_offer_redistributes(client: KeitaroClient) -> None:
    respx.get(f"{BASE}/admin_api/v1/campaigns/{CAMPAIGN_ID}/streams").mock(
        return_value=Response(200, json=[_stream_payload([(18813, 100)])])
    )
    update_route = respx.put(f"{BASE}/admin_api/v1/streams/{STREAM_ID}").mock(
        return_value=Response(200, json=_stream_payload([(18813, 50), (12992, 50)]))
    )

    stream = await add_offer(client, campaign_id=CAMPAIGN_ID, stream_id=STREAM_ID, offer_id=12992)

    assert sum(offer.share for offer in stream.offers) == 100
    assert len(stream.offers) == 2
    assert update_route.called


@respx.mock
async def test_add_offer_sends_equal_shares(client: KeitaroClient) -> None:
    respx.get(f"{BASE}/admin_api/v1/campaigns/{CAMPAIGN_ID}/streams").mock(
        return_value=Response(200, json=[_stream_payload([(1, 50), (2, 50)])])
    )
    update_route = respx.put(f"{BASE}/admin_api/v1/streams/{STREAM_ID}").mock(
        return_value=Response(200, json=_stream_payload([(1, 34), (2, 33), (3, 33)]))
    )

    await add_offer(client, campaign_id=CAMPAIGN_ID, stream_id=STREAM_ID, offer_id=3)

    body = update_route.calls.last.request.read().decode()
    assert '"share":34' in body or '"share":33' in body
    assert '"offer_id":3' in body


@respx.mock
async def test_add_existing_offer_raises(client: KeitaroClient) -> None:
    respx.get(f"{BASE}/admin_api/v1/campaigns/{CAMPAIGN_ID}/streams").mock(
        return_value=Response(200, json=[_stream_payload([(18813, 100)])])
    )

    with pytest.raises(OfferNotInStream):
        await add_offer(client, campaign_id=CAMPAIGN_ID, stream_id=STREAM_ID, offer_id=18813)


@respx.mock
async def test_add_offer_to_missing_stream_raises(client: KeitaroClient) -> None:
    respx.get(f"{BASE}/admin_api/v1/campaigns/{CAMPAIGN_ID}/streams").mock(
        return_value=Response(200, json=[_stream_payload([(1, 100)])])
    )

    with pytest.raises(StreamNotFound):
        await add_offer(client, campaign_id=CAMPAIGN_ID, stream_id=999, offer_id=5)


@respx.mock
async def test_remove_offer_redistributes(client: KeitaroClient) -> None:
    respx.get(f"{BASE}/admin_api/v1/campaigns/{CAMPAIGN_ID}/streams").mock(
        return_value=Response(200, json=[_stream_payload([(1, 34), (2, 33), (3, 33)])])
    )
    respx.put(f"{BASE}/admin_api/v1/streams/{STREAM_ID}").mock(
        return_value=Response(200, json=_stream_payload([(1, 50), (3, 50)]))
    )

    stream = await remove_offer(client, campaign_id=CAMPAIGN_ID, stream_id=STREAM_ID, offer_id=2)

    assert len(stream.offers) == 2
    assert sum(offer.share for offer in stream.offers) == 100


@respx.mock
async def test_remove_offer_sends_balanced_values(client: KeitaroClient) -> None:
    respx.get(f"{BASE}/admin_api/v1/campaigns/{CAMPAIGN_ID}/streams").mock(
        return_value=Response(200, json=[_stream_payload([(1, 50), (2, 30), (3, 20)])])
    )
    update_route = respx.put(f"{BASE}/admin_api/v1/streams/{STREAM_ID}").mock(
        return_value=Response(200, json=_stream_payload([(1, 50), (3, 50)]))
    )

    await remove_offer(client, campaign_id=CAMPAIGN_ID, stream_id=STREAM_ID, offer_id=2)

    body = update_route.calls.last.request.read().decode()
    assert "12992" not in body
    assert '"share":50' in body


@respx.mock
async def test_remove_last_offer_leaves_empty_list(client: KeitaroClient) -> None:
    respx.get(f"{BASE}/admin_api/v1/campaigns/{CAMPAIGN_ID}/streams").mock(
        return_value=Response(200, json=[_stream_payload([(1, 100)])])
    )
    update_route = respx.put(f"{BASE}/admin_api/v1/streams/{STREAM_ID}").mock(
        return_value=Response(200, json=_stream_payload([]))
    )

    await remove_offer(client, campaign_id=CAMPAIGN_ID, stream_id=STREAM_ID, offer_id=1)

    body = update_route.calls.last.request.read().decode()
    assert '"offers":[]' in body


@respx.mock
async def test_remove_missing_offer_raises(client: KeitaroClient) -> None:
    respx.get(f"{BASE}/admin_api/v1/campaigns/{CAMPAIGN_ID}/streams").mock(
        return_value=Response(200, json=[_stream_payload([(1, 100)])])
    )

    with pytest.raises(OfferNotInStream):
        await remove_offer(client, campaign_id=CAMPAIGN_ID, stream_id=STREAM_ID, offer_id=999)
