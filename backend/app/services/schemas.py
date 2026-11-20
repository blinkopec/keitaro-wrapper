from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Campaign(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    alias: str
    state: str
    type: str
    position: int
    group_id: int
    domain_id: int
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

    name: str
    domain_id: int
    group_id: int
    traffic_source_id: int

    def to_payload(self) -> dict[str, Any]:
        return self.model_dump()
