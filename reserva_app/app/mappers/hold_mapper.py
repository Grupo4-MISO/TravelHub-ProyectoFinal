import json

from app.domain.hold import Hold


class HoldMapper:
    """Convierte entre JSON de Redis y el modelo canónico Hold."""

    @staticmethod
    def from_cache_json(raw: str) -> Hold:
        payload = json.loads(raw)
        return Hold.model_validate(payload)

    @staticmethod
    def to_cache_dict(hold: Hold) -> dict:
        # mode='json' serializa date a ISO-8601 para Redis.
        return hold.model_dump(mode="json", exclude={"ttl_restante"})

    @staticmethod
    def to_public_dict(hold: Hold) -> dict:
        return hold.model_dump(mode="json", exclude_none=True)
