import respx
from fastapi.testclient import TestClient
from httpx import Response

from app.services.schemas import CampaignDetail, Offer

BASE = "https://keitaro.test"


def test_list_offers(client: TestClient) -> None:
    with respx.mock:
        respx.get(f"{BASE}/admin_api/v1/offers").mock(
            return_value=Response(
                200,
                json=[{"id": 1, "name": "offer", "group_id": 2, "state": "active"}],
            )
        )
        response = client.get("/api/v1/offers/")

    assert response.status_code == 200
    offers = [Offer.model_validate(item) for item in response.json()]
    assert offers[0].id == 1


def test_get_campaign_detail_returns_streams(client: TestClient) -> None:
    campaign = {
        "id": 1,
        "name": "test",
        "alias": "test",
        "state": "active",
        "type": "position",
        "position": 1,
        "group_id": 2,
        "traffic_source_id": 3,
    }
    stream = {
        "id": 10,
        "campaign_id": 1,
        "name": "stream",
        "type": "regular",
        "position": 1,
        "state": "active",
        "schema": "redirect",
        "action_type": "http",
        "filters": [],
        "offers": [{"id": 1, "stream_id": 10, "offer_id": 5, "state": "active", "share": 100}],
    }

    with respx.mock:
        respx.get(f"{BASE}/admin_api/v1/campaigns/1").mock(
            return_value=Response(200, json=campaign)
        )
        respx.get(f"{BASE}/admin_api/v1/campaigns/1/streams").mock(
            return_value=Response(200, json=[stream])
        )
        response = client.get("/api/v1/campaigns/1")

    assert response.status_code == 200
    detail = CampaignDetail.model_validate(response.json())
    assert detail.streams[0].offers[0].share == 100
