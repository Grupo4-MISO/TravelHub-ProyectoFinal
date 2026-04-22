import time
import uuid
from datetime import date, datetime, timezone

from pydantic import BaseModel, ConfigDict
from pydantic import model_validator

from app.domain.reserva_estado import ReservaEstado


class Hold(BaseModel):
    """Modelo canónico de una reserva temporal (hold)."""

    id: str
    public_id: str
    estado: str
    created_at: datetime
    updated_at: datetime
    user_id: str
    habitacion_id: str
    check_in: date
    check_out: date
    expira_en: int
    ttl_segundos: int
    ttl_restante: int | None = None

    model_config = ConfigDict(extra="ignore")

    @model_validator(mode="before")
    @classmethod
    def _compatibilidad_payload_viejo(cls, payload):
        if not isinstance(payload, dict):
            return payload

        normalized = dict(payload)

        if "id" not in normalized and "hold_id" in normalized:
            normalized["id"] = normalized["hold_id"]

        if "public_id" not in normalized:
            normalized["public_id"] = "RSV-" + uuid.uuid4().hex[:8].upper()

        if "estado" not in normalized:
            normalized["estado"] = ReservaEstado.PENDIENTE.value

        now = datetime.now(timezone.utc)
        if "created_at" not in normalized:
            normalized["created_at"] = now
        if "updated_at" not in normalized:
            normalized["updated_at"] = now

        return normalized

    @classmethod
    def crear(cls, user_id, habitacion_id, check_in: date, check_out: date, ttl_segundos: int):
        now = datetime.now(timezone.utc)
        return cls(
            id=str(uuid.uuid4()),
            public_id="RSV-" + uuid.uuid4().hex[:8].upper(),
            estado=ReservaEstado.PENDIENTE.value,
            created_at=now,
            updated_at=now,
            user_id=str(user_id),
            habitacion_id=str(habitacion_id),
            check_in=check_in,
            check_out=check_out,
            expira_en=int(time.time()) + ttl_segundos,
            ttl_segundos=ttl_segundos,
        )
