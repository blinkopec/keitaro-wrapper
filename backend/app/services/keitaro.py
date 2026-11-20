import logging
from http import HTTPStatus
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class KeitaroError(Exception):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.status_code = status_code
        super().__init__(message)


class KeitaroNotFound(KeitaroError):
    pass


class KeitaroNotConfigured(KeitaroError):
    pass


class KeitaroClient:
    def __init__(self, base_url: str, api_key: str, timeout: float = 15.0) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            headers={"Api-Key": api_key},
            timeout=timeout,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"/admin_api/v1{path}"

        try:
            response = await self._client.request(method, url, **kwargs)
        except httpx.TimeoutException as exc:
            raise KeitaroError(f"Keitaro API timeout: {method} {url}") from exc
        except httpx.HTTPError as exc:
            raise KeitaroError(f"Keitaro API connection error: {exc}") from exc

        if response.status_code == HTTPStatus.NOT_FOUND:
            raise KeitaroNotFound(f"Not found: {url}", status_code=404)

        if response.is_error:
            logger.warning(
                "Keitaro API error %s on %s: %s",
                response.status_code,
                url,
                response.text[:500],
            )
            raise KeitaroError(
                f"Keitaro API error {response.status_code} on {url}",
                status_code=response.status_code,
            )

        if not response.content:
            return None

        return response.json()

    async def get_campaigns(self, state: str | None = None) -> list[dict[str, Any]]:
        params = {"state": state} if state else None
        return await self._request("GET", "/campaigns", params=params)

    async def get_campaign(self, campaign_id: int) -> dict[str, Any]:
        return await self._request("GET", f"/campaigns/{campaign_id}")

    async def create_campaign(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._request("POST", "/campaigns", json=payload)

    async def get_offers(self) -> list[dict[str, Any]]:
        return await self._request("GET", "/offers")

    async def get_streams(self, campaign_id: int) -> list[dict[str, Any]]:
        return await self._request("GET", f"/campaigns/{campaign_id}/streams")

    async def create_stream(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._request("POST", "/streams", json=payload)

    async def get_domains(self) -> list[dict[str, Any]]:
        return await self._request("GET", "/domains")

    async def get_groups(self, group_type: str) -> list[dict[str, Any]]:
        return await self._request("GET", "/groups", params={"type": group_type})

    async def get_traffic_sources(self) -> list[dict[str, Any]]:
        return await self._request("GET", "/traffic_sources")


def create_keitaro_client() -> KeitaroClient | None:
    from app.config import settings

    if not settings.KEITARO_API_URL or not settings.KEITARO_API_KEY:
        logger.warning("Keitaro API не настроен: KEITARO_API_URL или KEITARO_API_KEY пусты")
        return None

    return KeitaroClient(
        base_url=settings.KEITARO_API_URL,
        api_key=settings.KEITARO_API_KEY,
    )
