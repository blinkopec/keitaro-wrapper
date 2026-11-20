from fastapi import APIRouter

from app.services.deps import KeitaroDep
from app.services.schemas import Offer

router = APIRouter(prefix="/offers", tags=["offers"])


@router.get("/", response_model=list[Offer])
async def list_offers(keitaro: KeitaroDep) -> list[Offer]:
    raw = await keitaro.get_offers()
    return [Offer.model_validate(item) for item in raw]
