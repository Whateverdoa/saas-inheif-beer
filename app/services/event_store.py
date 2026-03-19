import os
import logging
from typing import Any, Dict
from asyncio import Lock

logger = logging.getLogger("uvicorn.error")

CONVEX_URL = os.getenv("CONVEX_URL", "")
CONVEX_TOKEN = os.getenv("CONVEX_TOKEN", "")

_inmem_lock = Lock()
_inmem_events: dict[str, dict[str, Any]] = {}
_inmem_notes: dict[str, list[str]] = {}


class BaseEventStore:
    async def exists(self, event_id: str) -> bool: ...
    async def save(self, event_id: str, provider: str, payload: Dict[str, Any]) -> None: ...
    async def mark_failed(self, event_id: str, error: str) -> None: ...
    async def mark_note(self, key: str, note: str) -> None: ...
    async def get_event(self, event_id: str) -> Dict[str, Any] | None: ...
    async def list_events(self, provider: str | None = None, limit: int = 100, offset: int = 0) -> Dict[str, Any]: ...
    async def get_stats(self) -> Dict[str, Any]: ...


class InMemoryEventStore(BaseEventStore):
    async def exists(self, event_id: str) -> bool:
        async with _inmem_lock:
            return event_id in _inmem_events

    async def save(self, event_id: str, provider: str, payload: Dict[str, Any]) -> None:
        async with _inmem_lock:
            _inmem_events[event_id] = {"provider": provider, "payload": payload, "status": "saved"}

    async def mark_failed(self, event_id: str, error: str) -> None:
        async with _inmem_lock:
            if event_id in _inmem_events:
                _inmem_events[event_id]["status"] = "failed"
                _inmem_events[event_id]["error"] = error

    async def mark_note(self, key: str, note: str) -> None:
        async with _inmem_lock:
            _inmem_notes.setdefault(key, []).append(note)

    async def get_event(self, event_id: str) -> Dict[str, Any] | None:
        async with _inmem_lock:
            return _inmem_events.get(event_id)

    async def list_events(self, provider: str | None = None, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        async with _inmem_lock:
            events = list(_inmem_events.items())
            if provider:
                events = [(eid, edata) for eid, edata in events if edata.get("provider") == provider]
            # Sort by event_id (descending, most recent first)
            events.sort(key=lambda x: x[0], reverse=True)
            total = len(events)
            paginated = events[offset:offset + limit]
            return {
                "events": [{"event_id": eid, **edata} for eid, edata in paginated],
                "total": total,
                "limit": limit,
                "offset": offset,
            }

    async def get_stats(self) -> Dict[str, Any]:
        async with _inmem_lock:
            total = len(_inmem_events)
            by_provider = {}
            by_status = {}
            for edata in _inmem_events.values():
                provider = edata.get("provider", "unknown")
                status_val = edata.get("status", "unknown")
                by_provider[provider] = by_provider.get(provider, 0) + 1
                by_status[status_val] = by_status.get(status_val, 0) + 1
            return {
                "total_events": total,
                "by_provider": by_provider,
                "by_status": by_status,
            }


class ConvexEventStore(BaseEventStore):
    """
    Stub for Convex integration. Replace with your real Convex mutations/queries.
    """
    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token

    async def exists(self, event_id: str) -> bool:
        # TODO: call Convex to check if event exists
        logger.debug("convex.exists_called", extra={"event_id": event_id})
        return False

    async def save(self, event_id: str, provider: str, payload: Dict[str, Any]) -> None:
        # TODO: call Convex to insert event
        logger.debug("convex.save_called", extra={"event_id": event_id, "provider": provider})

    async def mark_failed(self, event_id: str, error: str) -> None:
        # TODO: call Convex to update event status
        logger.debug("convex.mark_failed_called", extra={"event_id": event_id, "error": error})

    async def mark_note(self, key: str, note: str) -> None:
        # TODO: call Convex to append a note
        logger.debug("convex.mark_note_called", extra={"key": key, "note": note})

    async def get_event(self, event_id: str) -> Dict[str, Any] | None:
        # TODO: call Convex to get event by ID
        logger.debug("convex.get_event_called", extra={"event_id": event_id})
        return None

    async def list_events(self, provider: str | None = None, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        # TODO: call Convex to list events with pagination
        logger.debug("convex.list_events_called", extra={"provider": provider, "limit": limit, "offset": offset})
        return {"events": [], "total": 0, "limit": limit, "offset": offset}

    async def get_stats(self) -> Dict[str, Any]:
        # TODO: call Convex to get statistics
        logger.debug("convex.get_stats_called")
        return {"total_events": 0, "by_provider": {}, "by_status": {}}


def get_event_store() -> BaseEventStore:
    if CONVEX_URL and CONVEX_TOKEN:
        logger.info("event_store.using_convex")
        return ConvexEventStore(CONVEX_URL, CONVEX_TOKEN)
    logger.info("event_store.using_inmemory")
    return InMemoryEventStore()
