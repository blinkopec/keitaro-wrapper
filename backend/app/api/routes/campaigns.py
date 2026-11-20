from fastapi import APIRouter, status

from app.services.campaigns import create_campaign
from app.services.deps import KeitaroDep
from app.services.schemas import (
    Campaign,
    CampaignDetail,
    CampaignRequest,
    Stream,
)

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("/", response_model=list[Campaign])
async def list_campaigns(keitaro: KeitaroDep) -> list[Campaign]:
    raw = await keitaro.get_campaigns()
    return [Campaign.model_validate(item) for item in raw]


@router.get("/{campaign_id}", response_model=CampaignDetail)
async def get_campaign_detail(campaign_id: int, keitaro: KeitaroDep) -> CampaignDetail:
    raw_campaign = await keitaro.get_campaign(campaign_id)
    raw_streams = await keitaro.get_streams(campaign_id)
    return CampaignDetail(
        campaign=Campaign.model_validate(raw_campaign),
        streams=[Stream.model_validate(item) for item in raw_streams],
    )


@router.post("/", response_model=Campaign, status_code=status.HTTP_201_CREATED)
async def create_campaign_endpoint(payload: CampaignRequest, keitaro: KeitaroDep) -> Campaign:
    return await create_campaign(keitaro, geo=payload.geo, offer_id=payload.offer_id)
