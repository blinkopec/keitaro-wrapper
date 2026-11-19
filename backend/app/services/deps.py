from typing import Annotated

from fastapi import Depends, Request

from app.services.keitaro import KeitaroClient, KeitaroNotConfigured


def get_keitaro_client(request: Request) -> KeitaroClient:
    client: KeitaroClient | None = getattr(request.app.state, "keitaro", None)

    if client is None:
        raise KeitaroNotConfigured(
            "Keitaro API не настроен: заполните KEITARO_API_URL и KEITARO_API_KEY"
        )
    return client


KeitaroDep = Annotated[KeitaroClient, Depends(get_keitaro_client)]
