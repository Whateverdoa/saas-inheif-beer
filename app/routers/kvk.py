"""KVK company lookup endpoints."""
from fastapi import APIRouter, HTTPException, status

from app.services.kvk_service import lookup_kvk, normalize_kvk_input

router = APIRouter(prefix="/kvk", tags=["kvk"])


@router.get("/lookup/{kvk_nummer}")
async def kvk_lookup(kvk_nummer: str) -> dict:
    """
    Basisprofiel lookup voor een 8-cijferig KVK-nummer.
    Vereist ``KVK_API_KEY`` in productie; zonder key zijn alleen testnummers (mock) beschikbaar.
    """
    _, err = normalize_kvk_input(kvk_nummer)
    if err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)
    try:
        return await lookup_kvk(kvk_nummer)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e
