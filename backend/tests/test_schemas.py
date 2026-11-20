import pytest
from pydantic import ValidationError

from app.services.schemas import (
    Campaign,
    CampaignCreate,
    Domain,
    Group,
    Offer,
    Stream,
    StreamFilter,
    StreamOffer,
    TrafficSource,
)

RAW_CAMPAIGN = {
    "id": 216415,
    "alias": "test_khristoforov_campaign12",
    "name": "test_khristoforov_campaign12",
    "type": "position",
    "uniqueness_method": "ip",
    "cookies_ttl": 24,
    "position": 9999,
    "state": "active",
    "updated_at": "2026-11-20 06:29:38",
    "cost_type": "CPC",
    "cost_value": 0,
    "cost_currency": "USD",
    "group_id": 0,
    "bind_visitors": "",
    "traffic_source_id": 836,
    "token": "73243978a8a387dc11a3efcb5dd9022f3c7a99e",
    "cost_auto": False,
    "domain_id": 1813,
    "notes": None,
    "parameters": {},
    "uniqueness_use_cookies": True,
    "traffic_loss": 0,
    "bypass_cache": False,
    "created_at": "2026-11-20 06:29:38",
    "uniqueness_param": None,
    "domain": "https://kylovoa.com/",
    "postbacks": [],
    "group": "",
}

RAW_STREAM = {
    "id": 1330354,
    "type": "regular",
    "name": "Offer Stream (ID: 18813)",
    "campaign_id": 216370,
    "position": 2,
    "action_options": None,
    "comments": "",
    "state": "active",
    "created_at": "2026-11-20 05:43:04",
    "action_type": "http",
    "action_payload": "",
    "schema": "landings",
    "collect_clicks": True,
    "filter_or": False,
    "weight": 0,
    "offer_selection": "before_click",
    "filters": [],
    "triggers": [],
    "landings": [],
    "offers": [
        {
            "id": 2086148,
            "stream_id": 1330354,
            "offer_id": 18813,
            "state": "active",
            "share": 34,
            "created_at": "2026-11-20 05:43:04",
            "updated_at": "2026-11-20 05:44:27",
        },
        {
            "id": 2086149,
            "stream_id": 1330354,
            "offer_id": 12992,
            "state": "active",
            "share": 33,
            "created_at": "2026-11-20 05:44:27",
            "updated_at": "2026-11-20 05:44:27",
        },
        {
            "id": 2086150,
            "stream_id": 1330354,
            "offer_id": 22999,
            "state": "active",
            "share": 33,
            "created_at": "2026-11-20 05:44:27",
            "updated_at": "2026-11-20 05:44:27",
        },
    ],
}

RAW_FILTER_STREAM = {
    "id": 1330353,
    "type": "regular",
    "name": "Geo Filter (AU, RU, EN) -> Google",
    "campaign_id": 216370,
    "position": 1,
    "action_type": "http",
    "action_payload": "https://google.com",
    "schema": "redirect",
    "state": "active",
    "filters": [
        {
            "id": 2997975,
            "stream_id": 1330353,
            "name": "country",
            "mode": "accept",
            "payload": ["AU, RU, EN"],
            "oid": 2997975,
        }
    ],
    "offers": [],
}


def test_campaign_parses_real_payload() -> None:
    campaign = Campaign.model_validate(RAW_CAMPAIGN)

    assert campaign.id == 216415
    assert campaign.name == "test_khristoforov_campaign12"
    assert campaign.domain_id == 1813
    assert campaign.traffic_source_id == 836
    assert campaign.domain == "https://kylovoa.com/"


def test_campaign_parses_datetime() -> None:
    campaign = Campaign.model_validate(RAW_CAMPAIGN)

    assert campaign.created_at is not None
    assert campaign.created_at.year == 2026
    assert campaign.created_at.month == 11


def test_campaign_ignores_unknown_fields() -> None:
    campaign = Campaign.model_validate(RAW_CAMPAIGN)

    assert not hasattr(campaign, "token")
    assert not hasattr(campaign, "cookies_ttl")


def test_campaign_requires_id() -> None:
    payload = {key: value for key, value in RAW_CAMPAIGN.items() if key != "id"}

    with pytest.raises(ValidationError):
        Campaign.model_validate(payload)


def test_campaign_rejects_wrong_type() -> None:
    payload = {**RAW_CAMPAIGN, "id": "not-a-number"}

    with pytest.raises(ValidationError):
        Campaign.model_validate(payload)


def test_stream_parses_schema_alias() -> None:
    stream = Stream.model_validate(RAW_STREAM)

    assert stream.schema_ == "landings"


def test_stream_defaults_schema_to_redirect() -> None:
    payload = {key: value for key, value in RAW_STREAM.items() if key != "schema"}

    stream = Stream.model_validate(payload)

    assert stream.schema_ == "redirect"


def test_stream_parses_offers_with_share() -> None:
    stream = Stream.model_validate(RAW_STREAM)

    assert len(stream.offers) == 3
    assert [offer.offer_id for offer in stream.offers] == [18813, 12992, 22999]


def test_stream_offers_share_sums_to_hundred() -> None:
    stream = Stream.model_validate(RAW_STREAM)

    assert sum(offer.share for offer in stream.offers) == 100


def test_stream_without_offers_gets_empty_list() -> None:
    stream = Stream.model_validate(RAW_FILTER_STREAM)

    assert stream.offers == []


def test_stream_parses_country_filter() -> None:
    stream = Stream.model_validate(RAW_FILTER_STREAM)

    assert len(stream.filters) == 1
    filter_ = stream.filters[0]
    assert filter_.name == "country"
    assert filter_.mode == "accept"
    assert filter_.payload == ["AU, RU, EN"]


def test_stream_position_defines_order() -> None:
    first = Stream.model_validate(RAW_FILTER_STREAM)
    second = Stream.model_validate(RAW_STREAM)

    assert first.position < second.position


def test_filter_can_be_built_without_ids() -> None:
    filter_ = StreamFilter(name="country", mode="accept", payload=["MX"])

    assert filter_.id is None
    assert filter_.stream_id is None
    assert filter_.oid is None


def test_stream_offer_requires_share() -> None:
    payload = {
        "id": 1,
        "stream_id": 2,
        "offer_id": 3,
        "state": "active",
    }

    with pytest.raises(ValidationError):
        StreamOffer.model_validate(payload)


def test_stream_offer_share_accepts_numeric_string() -> None:
    offer = StreamOffer.model_validate(
        {"id": 1, "stream_id": 2, "offer_id": 3, "state": "active", "share": "34"}
    )

    assert offer.share == 34
    assert isinstance(offer.share, int)


def test_stream_offer_share_rejects_non_numeric() -> None:
    with pytest.raises(ValidationError):
        StreamOffer.model_validate(
            {"id": 1, "stream_id": 2, "offer_id": 3, "state": "active", "share": "abc"}
        )


def test_offer_parses_countries() -> None:
    offer = Offer.model_validate(
        {
            "id": 18813,
            "name": "18813 Flexacil",
            "group_id": 7183,
            "state": "active",
            "country": ["Peru"],
            "payout_value": 0,
        }
    )

    assert offer.country == ["Peru"]


def test_offer_countries_default_to_empty() -> None:
    offer = Offer.model_validate({"id": 1, "name": "test", "group_id": 2, "state": "active"})

    assert offer.country == []


def test_domain_defaults_is_ssl_to_false() -> None:
    domain = Domain.model_validate({"id": 1813, "name": "kylovoa.com", "state": "active"})

    assert domain.is_ssl is False


def test_group_parses() -> None:
    group = Group.model_validate(
        {"id": 9799, "name": "VZ adrobot test", "position": 9282, "type": "campaigns"}
    )

    assert group.type == "campaigns"
    assert group.name == "VZ adrobot test"


def test_traffic_source_parses() -> None:
    source = TrafficSource.model_validate(
        {"id": 836, "name": "FORTESTS", "state": "active", "postback_url": ""}
    )

    assert source.id == 836
    assert source.name == "FORTESTS"


def test_campaign_create_dumps_payload() -> None:
    payload = CampaignCreate(
        name="MX test",
        domain_id=1813,
        group_id=9799,
        traffic_source_id=836,
    ).to_payload()

    assert payload == {
        "name": "MX test",
        "domain_id": 1813,
        "group_id": 9799,
        "traffic_source_id": 836,
    }


def test_campaign_create_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        CampaignCreate(
            name="MX test",
            domain_id=1813,
            group_id=9799,
            traffic_source_id=836,
            typo_field="oops",
        )


def test_campaign_create_requires_all_fields() -> None:
    with pytest.raises(ValidationError):
        CampaignCreate(name="MX test", domain_id=1813)
