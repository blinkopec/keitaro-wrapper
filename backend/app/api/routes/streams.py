from fastapi import APIRouter, HTTPException, status

from app.services.deps import KeitaroDep
from app.services.schemas import OfferAddRequest, Stream
from app.services.streams import (
    OfferNotInStream,
    StreamNotFound,
    add_offer,
    remove_offer,
)

router = APIRouter(prefix="/campaigns/{campaign_id}/streams/{stream_id}", tags=["streams"])


@router.post("/offers", response_model=Stream, status_code=status.HTTP_201_CREATED)
async def add_offer_endpoint(
    campaign_id: int,
    stream_id: int,
    payload: OfferAddRequest,
    keitaro: KeitaroDep,
) -> Stream:
    try:
        return await add_offer(
            keitaro,
            campaign_id=campaign_id,
            stream_id=stream_id,
            offer_id=payload.offer_id,
        )
    except StreamNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except OfferNotInStream as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.delete("/offers/{offer_id}", response_model=Stream)
async def remove_offer_endpoint(
    campaign_id: int,
    stream_id: int,
    offer_id: int,
    keitaro: KeitaroDep,
) -> Stream:
    try:
        return await remove_offer(
            keitaro,
            campaign_id=campaign_id,
            stream_id=stream_id,
            offer_id=offer_id,
        )
    except StreamNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except OfferNotInStream as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
