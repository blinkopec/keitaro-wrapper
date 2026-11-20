from app.services.keitaro import KeitaroClient
from app.services.schemas import Stream, StreamOffer

SHARE_TOTAL = 100


class StreamNotFound(Exception):
    """Поток не найден в кампании."""


class OfferNotInStream(Exception):
    """Оффер отсутствует в потоке."""


def redistribute(total: int, count: int) -> list[int]:
    """Делит total на count частей так, чтобы сумма осталась равна total."""
    if count <= 0:
        return []
    base, remainder = divmod(total, count)
    return [base + (1 if index < remainder else 0) for index in range(count)]


def rebalance_shares(offer_ids: list[int]) -> list[int]:
    """Возвращает доли офферов, сумма которых ровно 100."""
    return redistribute(SHARE_TOTAL, len(offer_ids))


def build_offers_payload(shares: dict[int, int]) -> list[dict[str, object]]:
    return [
        {"offer_id": offer_id, "share": share, "state": "active"}
        for offer_id, share in shares.items()
    ]


async def _load_offer_stream(client: KeitaroClient, campaign_id: int, stream_id: int) -> Stream:
    raw_streams = await client.get_streams(campaign_id)
    for raw in raw_streams:
        if raw["id"] == stream_id:
            return Stream.model_validate(raw)
    raise StreamNotFound(f"Stream {stream_id} not found in campaign {campaign_id}")


def _current_shares(stream: Stream) -> dict[int, int]:
    return {offer.offer_id: offer.share for offer in stream.offers}


async def add_offer(
    client: KeitaroClient,
    *,
    campaign_id: int,
    stream_id: int,
    offer_id: int,
) -> Stream:
    stream = await _load_offer_stream(client, campaign_id, stream_id)
    shares = _current_shares(stream)

    if offer_id in shares:
        raise OfferNotInStream(f"Offer {offer_id} already in stream {stream_id}")

    shares[offer_id] = 0
    new_offer_ids = list(shares)
    values = rebalance_shares(new_offer_ids)

    payload = {"offers": build_offers_payload(dict(zip(new_offer_ids, values, strict=True)))}
    raw = await client.update_stream(stream_id, payload)
    return Stream.model_validate(raw)


async def remove_offer(
    client: KeitaroClient,
    *,
    campaign_id: int,
    stream_id: int,
    offer_id: int,
) -> Stream:
    stream = await _load_offer_stream(client, campaign_id, stream_id)
    shares = _current_shares(stream)

    if offer_id not in shares:
        raise OfferNotInStream(f"Offer {offer_id} not in stream {stream_id}")

    del shares[offer_id]
    remaining = list(shares)
    values = rebalance_shares(remaining)

    payload = {"offers": build_offers_payload(dict(zip(remaining, values, strict=True)))}
    raw = await client.update_stream(stream_id, payload)
    return Stream.model_validate(raw)


def total_share(offers: list[StreamOffer]) -> int:
    return sum(offer.share for offer in offers)
