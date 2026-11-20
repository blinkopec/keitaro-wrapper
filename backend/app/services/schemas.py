from datetime import datetime
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field

GOOGLE_URL = "https://google.com"


class Campaign(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    alias: str
    state: str
    type: str
    position: int
    group_id: int
    domain_id: int | None = None
    traffic_source_id: int
    domain: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class StreamOffer(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    stream_id: int
    offer_id: int
    state: str
    share: int


class StreamFilter(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int | None = None
    stream_id: int | None = None
    name: str
    mode: str
    payload: list[str]
    oid: int | None = None


class Stream(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    campaign_id: int
    name: str
    type: str
    position: int
    state: str
    schema_: str = Field(alias="schema", default="redirect")
    action_type: str
    action_payload: str = ""
    filters: list[StreamFilter] = Field(default_factory=list)
    offers: list[StreamOffer] = Field(default_factory=list)


class Offer(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    group_id: int
    state: str
    country: list[str] = Field(default_factory=list)


class Domain(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    state: str
    is_ssl: bool = False


class Group(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    type: str
    position: int = 0


class TrafficSource(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    state: str


class CampaignCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=255)
    alias: str = Field(min_length=1, max_length=255)
    domain_id: int
    group_id: int
    traffic_source_id: int

    def to_payload(self) -> dict[str, Any]:
        return self.model_dump()


class CampaignRequest(BaseModel):
    """Данные формы создания кампании."""

    model_config = ConfigDict(extra="forbid")

    geo: str = Field(min_length=2, max_length=2, pattern=r"^[A-Z]{2}$")
    offer_id: int = Field(gt=0)


class StreamCreate(BaseModel):
    """Тело запроса на создание потока."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    name: str
    position: int
    schema_: Annotated[str, Field(alias="schema")] = "redirect"
    action_type: str = "http"
    action_payload: str = ""

    def to_payload(self) -> dict[str, Any]:
        return self.model_dump(by_alias=True)


class FilterCreate(BaseModel):
    """Фильтр для вложения в поток при создании."""

    model_config = ConfigDict(extra="forbid")

    name: str
    mode: str
    payload: list[str]

    def to_payload(self) -> dict[str, Any]:
        return self.model_dump()


class OfferCreate(BaseModel):
    """Оффер для вложения в поток при создании."""

    model_config = ConfigDict(extra="forbid")

    offer_id: int
    share: int = Field(ge=0, le=100)
    state: str = "active"

    def to_payload(self) -> dict[str, Any]:
        return self.model_dump()


class OfferAddRequest(BaseModel):
    """Запрос на добавление оффера: доля пересчитывается автоматически."""

    model_config = ConfigDict(extra="forbid")

    offer_id: int


def build_geo_redirect_stream(geo: str) -> dict[str, Any]:
    """Поток 1: всех из указанной страны отправляем на Google."""
    payload = StreamCreate(
        name=f"Geo Filter ({geo}) -> Google",
        position=1,
        schema="redirect",
        action_type="http",
        action_payload=GOOGLE_URL,
    ).to_payload()
    payload["filters"] = [FilterCreate(name="country", mode="accept", payload=[geo]).to_payload()]
    return payload


def build_offer_stream(offer_id: int) -> dict[str, Any]:
    """Поток 2: остальных отправляем на выбранный оффер."""
    payload = StreamCreate(
        name=f"Offer Stream (ID: {offer_id})",
        position=2,
        schema="landings",
        action_type="http",
        action_payload="",
    ).to_payload()
    payload["offers"] = [OfferCreate(offer_id=offer_id, share=100, state="active").to_payload()]
    return payload


class CampaignDetail(BaseModel):
    """Кампания и её потоки."""

    campaign: Campaign
    streams: list[Stream] = Field(default_factory=list)
