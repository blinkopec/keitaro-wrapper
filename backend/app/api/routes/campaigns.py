from fastapi import APIRouter, status

from app.services.campaigns import create_campaign
from app.services.deps import KeitaroDep
from app.services.schemas import Campaign, CampaignRequest

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.post("/", response_model=Campaign, status_code=status.HTTP_201_CREATED)
async def create_campaign_endpoint(payload: CampaignRequest, keitaro: KeitaroDep) -> Campaign:
    return await create_campaign(keitaro, geo=payload.geo, offer_id=payload.offer_id)
