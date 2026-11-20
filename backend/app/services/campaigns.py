import re
from datetime import UTC, datetime

from app.config import settings
from app.services.keitaro import KeitaroClient
from app.services.schemas import (
    Campaign,
    CampaignCreate,
    build_geo_redirect_stream,
    build_offer_stream,
)

CAMPAIGN_PREFIX = "test_sinelnikov_campaign"


def next_campaign_name(existing_names: list[str]) -> str:
    """Подбирает следующее свободное имя по порядку."""
    pattern = re.compile(rf"^{CAMPAIGN_PREFIX}(\d+)$")
    numbers = [int(match.group(1)) for name in existing_names if (match := pattern.match(name))]
    return f"{CAMPAIGN_PREFIX}{max(numbers, default=0) + 1}"


def timestamped_campaign_name(existing_names: list[str]) -> str:
    """Уникальное имя по метке времени."""
    stamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    candidate = f"{CAMPAIGN_PREFIX}{stamp}"
    suffix = 1
    while candidate in existing_names:
        suffix += 1
        candidate = f"{CAMPAIGN_PREFIX}{stamp}_{suffix}"
    return candidate


async def create_campaign(client: KeitaroClient, *, geo: str, offer_id: int) -> Campaign:
    campaigns = await client.get_campaigns()
    name = timestamped_campaign_name([raw["name"] for raw in campaigns])

    payload = CampaignCreate(
        name=name,
        alias=name,
        domain_id=settings.KEITARO_DEFAULT_DOMAIN_ID,
        group_id=settings.KEITARO_DEFAULT_GROUP_ID,
        traffic_source_id=settings.KEITARO_DEFAULT_SOURCE_ID,
    ).to_payload()

    raw_campaign = await client.create_campaign(payload)
    campaign_id: int = raw_campaign["id"]

    for stream_payload in (
        build_geo_redirect_stream(geo),
        build_offer_stream(offer_id),
    ):
        stream_payload["campaign_id"] = campaign_id
        await client.create_stream(stream_payload)

    return Campaign.model_validate(raw_campaign)
