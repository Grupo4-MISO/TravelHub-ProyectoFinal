from datetime import date, datetime, timezone
from uuid import UUID
import re

from flask import request
from flask_restful import Resource

from app.db.models import Tarifa, TarifaStatus, Descuento, db
from app.utils.token_helper import token_required

CATEGORIAS_HABITACION = {
    "SENCILLA",
    "DOBLE",
    "TRIPLE",
    "SUITE",
    "DELUXE",
    "FAMILIAR",
}

MONEDAS_PERMITIDAS = {"COP", "USD", "PEN", "MXN", "CLP", "ARS"}


def _current_hotel_id(current_user):
    return str(current_user.get("sub", "")).strip()


def _get_owned_tarifa_or_404(tarifa_id, hotel_id):
    tarifa_uuid = UUID(tarifa_id)
    return Tarifa.query.filter_by(id=tarifa_uuid, hotel_id=hotel_id).first()


def _get_owned_descuento_or_404(descuento_id, hotel_id):
    descuento_uuid = UUID(descuento_id)
    return (
        Descuento.query.join(Tarifa, Descuento.tarifa_id == Tarifa.id)
        .filter(Descuento.id == descuento_uuid, Tarifa.hotel_id == hotel_id)
        .first()
    )


def _parse_iso_datetime(value, field_name):
    if value is None or value == "":
        raise ValueError(f"El campo '{field_name}' es requerido")
    try:
        if isinstance(value, datetime):
            parsed = value
        elif isinstance(value, date):
            parsed = datetime.combine(value, datetime.min.time())
        elif isinstance(value, str):
            normalized = value.strip()
            # Normalizar "Z" a "+00:00"
            normalized = normalized.replace("Z", "+00:00")
            # Quitar espacio antes del offset (ej: "2026-05-13 00:00:00.000000 +00:00" -> "2026-05-13 00:00:00.000000+00:00")
            # Maneja formatos como "+HH:MM" o "-HH:MM"
            normalized = re.sub(r' ([+-]\d{2}:\d{2})', r'\1', normalized)
            parsed = datetime.fromisoformat(normalized)
        elif hasattr(value, "isoformat"):
            return _parse_iso_datetime(value.isoformat(), field_name)
        else:
            raise ValueError(f"El campo '{field_name}' debe estar en formato ISO-8601")
        if parsed.tzinfo is not None:
            return parsed.astimezone(timezone.utc).replace(tzinfo=None)
        return parsed
    except ValueError as exc:
        raise ValueError(f"El campo '{field_name}' debe estar en formato ISO-8601") from exc


def _parse_bool_param(value, field_name):
    if value is None:
        return None
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes", "si", "sí"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise ValueError(f"El parámetro '{field_name}' debe ser true o false")


def _is_tarifa_vigente(tarifa, now_utc=None):
    now_utc = now_utc or datetime.now(timezone.utc)
    # Asegurar que las fechas sean timezone-aware
    inicio = tarifa.vigencia_inicio if tarifa.vigencia_inicio.tzinfo else tarifa.vigencia_inicio.replace(tzinfo=timezone.utc)
    fin = tarifa.vigencia_fin if tarifa.vigencia_fin.tzinfo else tarifa.vigencia_fin.replace(tzinfo=timezone.utc)
    return inicio <= now_utc <= fin


def _calcular_valor_descuento(valor_base, porcentaje):
    return round(float(valor_base) * float(porcentaje) / 100.0, 2)


def _calcular_valor_final_con_descuentos(valor_base, descuentos):
    valor_actual = round(float(valor_base), 2)
    total_descuento = 0.0
    for descuento in descuentos:
        valor_descuento = round(valor_actual * float(descuento.porcentaje) / 100.0, 2)
        valor_actual = round(valor_actual - valor_descuento, 2)
        total_descuento = round(total_descuento + valor_descuento, 2)
    return total_descuento, valor_actual


def _serialize_tarifa(tarifa):
    descuentos_activos = [
        descuento
        for descuento in tarifa.descuentos
        if descuento.activo and _is_descuento_vigente(descuento)
    ]
    descuentos_activos.sort(key=lambda descuento: (descuento.vigencia_inicio, descuento.created_at, str(descuento.id)))
    valor_descuento_total, valor_final = _calcular_valor_final_con_descuentos(tarifa.valor_base, descuentos_activos)
    return {
        "id": str(tarifa.id),
        "nombre": tarifa.nombre,
        "hotel_id": tarifa.hotel_id,
        "identificador": tarifa.identificador,
        "descripcion": tarifa.descripcion,
        "valor_base": tarifa.valor_base,
        "moneda": tarifa.moneda,
        "categoria_habitacion": tarifa.categoria_habitacion,
        "estado": tarifa.estado.name if tarifa.estado else None,
        "vigencia_inicio": tarifa.vigencia_inicio.isoformat(),
        "vigencia_fin": tarifa.vigencia_fin.isoformat(),
        "vigente": _is_tarifa_vigente(tarifa),
        "valor_descuento_total": valor_descuento_total,
        "valor_final": valor_final,
        "descuentos_activos": [_serialize_descuento(descuento) for descuento in descuentos_activos],
        "created_at": tarifa.created_at.isoformat() if hasattr(tarifa.created_at, "isoformat") else tarifa.created_at,
        "updated_at": tarifa.updated_at.isoformat() if hasattr(tarifa.updated_at, "isoformat") else tarifa.updated_at,
    }


def _parse_percent(value, field_name):
    if value is None or value == "":
        raise ValueError(f"El campo '{field_name}' es requerido")
    porcentaje = float(value)
    if porcentaje <= 0:
        raise ValueError(f"El campo '{field_name}' debe ser mayor a 0")
    if porcentaje > 100:
        raise ValueError(f"El campo '{field_name}' no puede ser mayor a 100")
    return porcentaje


def _parse_bool_value(value, field_name):
    if value is None:
        return None
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes", "si", "sí"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise ValueError(f"El campo '{field_name}' debe ser true o false")


def _is_descuento_vigente(descuento, now_utc=None):
    now_utc = now_utc or datetime.now(timezone.utc)
    inicio = descuento.vigencia_inicio if descuento.vigencia_inicio.tzinfo else descuento.vigencia_inicio.replace(tzinfo=timezone.utc)
    fin = descuento.vigencia_fin if descuento.vigencia_fin.tzinfo else descuento.vigencia_fin.replace(tzinfo=timezone.utc)
    return inicio <= now_utc <= fin


def _to_naive_utc(value):
    """Convierte a datetime naive en UTC, manejando both aware y naive datetimes."""
    if value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


def _to_comparable_datetime(value):
    """Convierte cualquier datetime (aware o naive) a naive UTC para comparaciones."""
    naive = _to_naive_utc(value) if hasattr(value, 'tzinfo') else value
    # Si es naive, asumir que ya está en UTC
    return naive.replace(tzinfo=None) if naive.tzinfo else naive


def _validate_descuento_within_tarifa(vigencia_inicio, vigencia_fin, tarifa):
    tarifa_inicio = _to_comparable_datetime(tarifa.vigencia_inicio)
    tarifa_fin = _to_comparable_datetime(tarifa.vigencia_fin)
    desc_inicio = _to_comparable_datetime(vigencia_inicio)
    desc_fin = _to_comparable_datetime(vigencia_fin)

    if desc_inicio < tarifa_inicio or desc_fin > tarifa_fin:
        raise ValueError("La vigencia del descuento debe estar dentro de la vigencia de la tarifa")


def _serialize_descuento(descuento):
    return {
        "id": str(descuento.id),
        "nombre": descuento.nombre,
        "tarifa_id": str(descuento.tarifa_id),
        "porcentaje": descuento.porcentaje,
        "valor_descuento_calculado": _calcular_valor_descuento(descuento.tarifa.valor_base, descuento.porcentaje) if descuento.tarifa else None,
        "activo": descuento.activo,
        "vigencia_inicio": descuento.vigencia_inicio.isoformat(),
        "vigencia_fin": descuento.vigencia_fin.isoformat(),
        "vigente": _is_descuento_vigente(descuento),
        "created_at": descuento.created_at.isoformat() if hasattr(descuento.created_at, "isoformat") else descuento.created_at,
        "updated_at": descuento.updated_at.isoformat() if hasattr(descuento.updated_at, "isoformat") else descuento.updated_at,
    }


class Health(Resource):
    def get(self):
        return {"status": "healthy"}, 200


class TarifaListResource(Resource):
    @token_required
    def get(self, current_user):
        try:
            hotel_id = _current_hotel_id(current_user)
            vigentes = _parse_bool_param(request.args.get("vigentes"), "vigentes")
            tarifas = Tarifa.query.filter_by(hotel_id=hotel_id).all()
            if vigentes is not None:
                tarifas = [tarifa for tarifa in tarifas if _is_tarifa_vigente(tarifa) is vigentes]
            return [_serialize_tarifa(tarifa) for tarifa in tarifas], 200
        except ValueError as exc:
            return {"error": str(exc)}, 400

    @token_required
    def post(self, current_user):
        try:
            hotel_id = _current_hotel_id(current_user)
            data = request.get_json(silent=True) or {}

            if not data.get("nombre") and not data.get("identificador"):
                return {"error": "Debe enviar al menos 'nombre' o 'identificador'"}, 400

            valor_base_raw = data.get("valor_base")

            required_fields = [
                "moneda",
                "categoria_habitacion",
                "vigencia_inicio",
                "vigencia_fin",
            ]
            if valor_base_raw in (None, ""):
                return {"error": "El campo 'valor_base' es requerido"}, 400
            for field in required_fields:
                if data.get(field) in (None, ""):
                    return {"error": f"El campo '{field}' es requerido"}, 400

            valor_base = float(valor_base_raw)
            if valor_base <= 0:
                return {"error": "El campo 'valor_base' debe ser mayor a 0"}, 400

            body_hotel_id = str(data.get("hotel_id") or data.get("hotelId") or "").strip()
            if body_hotel_id and body_hotel_id != hotel_id:
                return {"error": "El campo 'hotel_id' debe coincidir con el claim 'sub' del token"}, 400

            moneda = str(data.get("moneda")).upper().strip()
            if moneda not in MONEDAS_PERMITIDAS:
                return {
                    "error": f"Moneda no soportada. Permitidas: {sorted(MONEDAS_PERMITIDAS)}"
                }, 400

            categoria_habitacion = str(data.get("categoria_habitacion")).upper().strip()
            if categoria_habitacion not in CATEGORIAS_HABITACION:
                return {
                    "error": f"Categoria de habitacion no valida. Permitidas: {sorted(CATEGORIAS_HABITACION)}"
                }, 400

            vigencia_inicio = _parse_iso_datetime(data.get("vigencia_inicio"), "vigencia_inicio")
            vigencia_fin = _parse_iso_datetime(data.get("vigencia_fin"), "vigencia_fin")
            if vigencia_inicio > vigencia_fin:
                return {"error": "'vigencia_inicio' no puede ser mayor a 'vigencia_fin'"}, 400

            identificador = data.get("identificador")
            if identificador:
                exists = Tarifa.query.filter_by(identificador=identificador).first()
                if exists:
                    return {"error": "El identificador ya existe"}, 400

            nueva_tarifa = Tarifa(
                nombre=data.get("nombre"),
                hotel_id=hotel_id,
                identificador=identificador,
                descripcion=data.get("descripcion", ""),
                valor_base=valor_base,
                moneda=moneda,
                categoria_habitacion=categoria_habitacion,
                vigencia_inicio=vigencia_inicio,
                vigencia_fin=vigencia_fin,
                estado=TarifaStatus.Active,
            )

            db.session.add(nueva_tarifa)
            db.session.commit()
            return _serialize_tarifa(nueva_tarifa), 201
        except ValueError as exc:
            return {"error": str(exc)}, 400
        except Exception as exc:
            db.session.rollback()
            return {"error": str(exc)}, 500


class TarifaPublicLookupResource(Resource):
    def get(self):
        try:
            hotel_ids_raw = request.args.get("hotel_ids") or request.args.get("hotelIds") or ""
            hotel_ids = [hotel_id.strip() for hotel_id in hotel_ids_raw.split(",") if hotel_id.strip()]
            if not hotel_ids:
                return {"error": "El parámetro 'hotel_ids' es requerido"}, 400

            vigentes = _parse_bool_param(request.args.get("vigentes"), "vigentes")

            tarifas = Tarifa.query.filter(Tarifa.hotel_id.in_(hotel_ids)).all()
            if vigentes is not None:
                tarifas = [tarifa for tarifa in tarifas if _is_tarifa_vigente(tarifa) is vigentes]

            return [_serialize_tarifa(tarifa) for tarifa in tarifas], 200
        except ValueError as exc:
            return {"error": str(exc)}, 400
        except Exception as exc:
            return {"error": str(exc)}, 500


class TarifaResource(Resource):
    @token_required
    def get(self, current_user, tarifa_id):
        try:
            hotel_id = _current_hotel_id(current_user)
            tarifa = _get_owned_tarifa_or_404(tarifa_id, hotel_id)
            if not tarifa:
                return {"error": "Tarifa no encontrada"}, 404
            return _serialize_tarifa(tarifa), 200
        except ValueError:
            return {"error": "El id de la tarifa no tiene un formato UUID valido"}, 400
        except Exception as exc:
            return {"error": str(exc)}, 500

    @token_required
    def put(self, current_user, tarifa_id):
        try:
            hotel_id = _current_hotel_id(current_user)
            tarifa = _get_owned_tarifa_or_404(tarifa_id, hotel_id)
            if not tarifa:
                return {"error": "Tarifa no encontrada"}, 404

            data = request.get_json(silent=True) or {}

            if "nombre" in data:
                tarifa.nombre = data["nombre"]
            if "identificador" in data:
                new_identificador = data["identificador"]
                if new_identificador:
                    exists = Tarifa.query.filter(
                        Tarifa.identificador == new_identificador,
                        Tarifa.id != tarifa.id,
                    ).first()
                    if exists:
                        return {"error": "El identificador ya existe"}, 400
                tarifa.identificador = new_identificador
            if "descripcion" in data:
                tarifa.descripcion = data["descripcion"]
            if "hotel_id" in data or "hotelId" in data:
                body_hotel_id = str(data.get("hotel_id", data.get("hotelId")) or "").strip()
                if body_hotel_id and body_hotel_id != hotel_id:
                    return {"error": "El campo 'hotel_id' no puede cambiarse"}, 400
            if "valor_base" in data:
                valor_base_raw = data.get("valor_base")
                if valor_base_raw in (None, ""):
                    return {"error": "El campo 'valor_base' es requerido"}, 400
                valor_base = float(valor_base_raw)
                if valor_base <= 0:
                    return {"error": "El campo 'valor_base' debe ser mayor a 0"}, 400
                tarifa.valor_base = valor_base
            if "moneda" in data:
                moneda = str(data["moneda"]).upper().strip()
                if moneda not in MONEDAS_PERMITIDAS:
                    return {
                        "error": f"Moneda no soportada. Permitidas: {sorted(MONEDAS_PERMITIDAS)}"
                    }, 400
                tarifa.moneda = moneda
            if "categoria_habitacion" in data:
                categoria = str(data["categoria_habitacion"]).upper().strip()
                if categoria not in CATEGORIAS_HABITACION:
                    return {
                        "error": f"Categoria de habitacion no valida. Permitidas: {sorted(CATEGORIAS_HABITACION)}"
                    }, 400
                tarifa.categoria_habitacion = categoria
            if "estado" in data:
                try:
                    tarifa.estado = TarifaStatus[data["estado"]]
                except KeyError:
                    return {"error": "El campo 'estado' no es valido"}, 400
            if "vigencia_inicio" in data:
                tarifa.vigencia_inicio = _parse_iso_datetime(data["vigencia_inicio"], "vigencia_inicio")
            if "vigencia_fin" in data:
                tarifa.vigencia_fin = _parse_iso_datetime(data["vigencia_fin"], "vigencia_fin")

            # Si el cliente envía 'descuentos' lo tomamos como la lista definitiva:
            # - lista vacía -> eliminar todos los descuentos asociados
            # - lista con elementos -> reemplazar por los enviados
            if 'descuentos' in data:
                descuentos_payload = data.get('descuentos') or []
                # Eliminar descuentos existentes
                try:
                    db.session.query(Descuento).filter(Descuento.tarifa_id == tarifa.id).delete(synchronize_session=False)
                    db.session.flush()
                except Exception:
                    db.session.rollback()
                    raise

                # Añadir nuevos descuentos (si los hay)
                for idx, d in enumerate(descuentos_payload):
                    nombre = d.get('nombre')
                    porcentaje = _parse_percent(d.get('porcentaje'), f'descuentos[{idx}].porcentaje')
                    activo_val = _parse_bool_value(d.get('activo', True), f'descuentos[{idx}].activo')
                    activo_flag = True if activo_val is None else activo_val
                    vigencia_inicio = _parse_iso_datetime(d.get('vigencia_inicio'), f'descuentos[{idx}].vigencia_inicio')
                    vigencia_fin = _parse_iso_datetime(d.get('vigencia_fin'), f'descuentos[{idx}].vigencia_fin')
                    if vigencia_inicio > vigencia_fin:
                        raise ValueError(f"descuentos[{idx}].vigencia_inicio no puede ser mayor a vigencia_fin")
                    _validate_descuento_within_tarifa(vigencia_inicio, vigencia_fin, tarifa)

                    nuevo_desc = Descuento(
                        nombre=nombre,
                        tarifa_id=tarifa.id,
                        porcentaje=porcentaje,
                        activo=activo_flag,
                        vigencia_inicio=vigencia_inicio,
                        vigencia_fin=vigencia_fin,
                    )
                    db.session.add(nuevo_desc)

            if tarifa.vigencia_inicio > tarifa.vigencia_fin:
                return {"error": "'vigencia_inicio' no puede ser mayor a 'vigencia_fin'"}, 400
            if not tarifa.nombre and not tarifa.identificador:
                return {"error": "Debe existir al menos 'nombre' o 'identificador'"}, 400

            db.session.commit()
            return _serialize_tarifa(tarifa), 200
        except ValueError as exc:
            return {"error": str(exc)}, 400
        except Exception as exc:
            db.session.rollback()
            return {"error": str(exc)}, 500

    @token_required
    def delete(self, current_user, tarifa_id):
        try:
            hotel_id = _current_hotel_id(current_user)
            tarifa = _get_owned_tarifa_or_404(tarifa_id, hotel_id)
            if not tarifa:
                return {"error": "Tarifa no encontrada"}, 404

            db.session.delete(tarifa)
            db.session.commit()
            return {"message": "Tarifa eliminada"}, 200
        except ValueError:
            return {"error": "El id de la tarifa no tiene un formato UUID valido"}, 400
        except Exception as exc:
            db.session.rollback()
            return {"error": str(exc)}, 500


class DescuentoListResource(Resource):
    @token_required
    def get(self, current_user):
        try:
            hotel_id = _current_hotel_id(current_user)
            activos = request.args.get("activos")
            tarifa_id = request.args.get("tarifa_id") or request.args.get("tarifaId")

            descuentos = [
                descuento
                for descuento in Descuento.query.all()
                if descuento.tarifa and str(descuento.tarifa.hotel_id) == hotel_id
            ]

            if activos is not None:
                activos_normalizado = str(activos).strip().lower()
                if activos_normalizado not in {"true", "false", "1", "0", "yes", "no"}:
                    return {"error": "El parámetro 'activos' debe ser true o false"}, 400
                activo_flag = activos_normalizado in {"true", "1", "yes"}
                descuentos = [descuento for descuento in descuentos if descuento.activo is activo_flag]

            if tarifa_id:
                descuentos = [descuento for descuento in descuentos if str(descuento.tarifa_id) == str(tarifa_id)]

            return [_serialize_descuento(descuento) for descuento in descuentos], 200
        except ValueError as exc:
            return {"error": str(exc)}, 400
        except Exception as exc:
            return {"error": str(exc)}, 500

    @token_required
    def post(self, current_user):
        try:
            hotel_id = _current_hotel_id(current_user)
            data = request.get_json(silent=True) or {}

            tarifa_id = str(data.get("tarifa_id") or data.get("tarifaId") or "").strip()
            if not tarifa_id:
                return {"error": "El campo 'tarifa_id' es requerido"}, 400

            tarifa = Tarifa.query.filter_by(id=UUID(tarifa_id), hotel_id=hotel_id).first()
            if not tarifa:
                return {"error": "La tarifa asociada no existe"}, 404

            porcentaje = _parse_percent(data.get("porcentaje"), "porcentaje")
            vigencia_inicio = _parse_iso_datetime(data.get("vigencia_inicio"), "vigencia_inicio")
            vigencia_fin = _parse_iso_datetime(data.get("vigencia_fin"), "vigencia_fin")
            if vigencia_inicio > vigencia_fin:
                return {"error": "'vigencia_inicio' no puede ser mayor a 'vigencia_fin'"}, 400

            _validate_descuento_within_tarifa(vigencia_inicio, vigencia_fin, tarifa)

            activo = _parse_bool_value(data.get("activo", True), "activo")

            descuento = Descuento(
                nombre=data.get("nombre"),
                tarifa_id=tarifa.id,
                porcentaje=porcentaje,
                activo=True if activo is None else activo,
                vigencia_inicio=vigencia_inicio,
                vigencia_fin=vigencia_fin,
            )

            db.session.add(descuento)
            db.session.commit()
            return _serialize_descuento(descuento), 201
        except ValueError as exc:
            return {"error": str(exc)}, 400
        except Exception as exc:
            db.session.rollback()
            return {"error": str(exc)}, 500


class DescuentoResource(Resource):
    @token_required
    def get(self, current_user, descuento_id):
        try:
            hotel_id = _current_hotel_id(current_user)
            descuento = _get_owned_descuento_or_404(descuento_id, hotel_id)
            if not descuento:
                return {"error": "Descuento no encontrado"}, 404
            return _serialize_descuento(descuento), 200
        except ValueError:
            return {"error": "El id del descuento no tiene un formato UUID valido"}, 400
        except Exception as exc:
            return {"error": str(exc)}, 500

    @token_required
    def put(self, current_user, descuento_id):
        try:
            hotel_id = _current_hotel_id(current_user)
            descuento = _get_owned_descuento_or_404(descuento_id, hotel_id)
            if not descuento:
                return {"error": "Descuento no encontrado"}, 404

            data = request.get_json(silent=True) or {}
            tarifa_obj = descuento.tarifa

            if "nombre" in data:
                descuento.nombre = data["nombre"]
            if "porcentaje" in data:
                descuento.porcentaje = _parse_percent(data.get("porcentaje"), "porcentaje")
            if "activo" in data:
                descuento.activo = _parse_bool_value(data["activo"], "activo")
            if "vigencia_inicio" in data:
                descuento.vigencia_inicio = _parse_iso_datetime(data["vigencia_inicio"], "vigencia_inicio")
            if "vigencia_fin" in data:
                descuento.vigencia_fin = _parse_iso_datetime(data["vigencia_fin"], "vigencia_fin")
            if "tarifa_id" in data or "tarifaId" in data:
                tarifa_id = str(data.get("tarifa_id", data.get("tarifaId")) or "").strip()
                if not tarifa_id:
                    return {"error": "El campo 'tarifa_id' es requerido"}, 400
                tarifa = Tarifa.query.filter_by(id=UUID(tarifa_id), hotel_id=hotel_id).first()
                if not tarifa:
                    return {"error": "La tarifa asociada no existe"}, 404
                descuento.tarifa_id = tarifa.id
                tarifa_obj = tarifa

            if descuento.vigencia_inicio > descuento.vigencia_fin:
                return {"error": "'vigencia_inicio' no puede ser mayor a 'vigencia_fin'"}, 400

            _validate_descuento_within_tarifa(descuento.vigencia_inicio, descuento.vigencia_fin, tarifa_obj)

            db.session.commit()
            return _serialize_descuento(descuento), 200
        except ValueError as exc:
            return {"error": str(exc)}, 400
        except Exception as exc:
            db.session.rollback()
            return {"error": str(exc)}, 500

    @token_required
    def delete(self, current_user, descuento_id):
        try:
            hotel_id = _current_hotel_id(current_user)
            descuento = _get_owned_descuento_or_404(descuento_id, hotel_id)
            if not descuento:
                return {"error": "Descuento no encontrado"}, 404

            db.session.delete(descuento)
            db.session.commit()
            return {"message": "Descuento eliminado"}, 200
        except ValueError:
            return {"error": "El id del descuento no tiene un formato UUID valido"}, 400
        except Exception as exc:
            db.session.rollback()
            return {"error": str(exc)}, 500


class SeedDB(Resource):
    def post(self):
        try:
            if Tarifa.query.first() is not None:
                return {"message": "Base de datos ya contiene datos"}, 200

            tarifas_ejemplo = [
                Tarifa(
                    nombre="Tarifa Basica",
                    hotel_id="HTL-99281",
                    identificador="TAR-BASICA-001",
                    descripcion="Tarifa basica para alojamiento",
                    valor_base=50.0,
                    moneda="COP",
                    categoria_habitacion="SENCILLA",
                    vigencia_inicio=datetime(2026, 1, 1, 0, 0, 0),
                    vigencia_fin=datetime(2026, 12, 31, 23, 59, 59),
                ),
                Tarifa(
                    nombre="Tarifa Premium",
                    hotel_id="HTL-99282",
                    identificador="TAR-PREM-001",
                    descripcion="Tarifa premium con servicios adicionales",
                    valor_base=100.0,
                    moneda="USD",
                    categoria_habitacion="DELUXE",
                    vigencia_inicio=datetime(2026, 1, 1, 0, 0, 0),
                    vigencia_fin=datetime(2026, 8, 31, 23, 59, 59),
                ),
                Tarifa(
                    nombre="Tarifa Legacy",
                    hotel_id="HTL-99283",
                    identificador="TAR-LEG-001",
                    descripcion="Tarifa historica no vigente",
                    valor_base=30.0,
                    moneda="COP",
                    categoria_habitacion="DOBLE",
                    vigencia_inicio=datetime(2024, 1, 1, 0, 0, 0),
                    vigencia_fin=datetime(2024, 12, 31, 23, 59, 59),
                ),
            ]

            db.session.add_all(tarifas_ejemplo)
            db.session.commit()
            return {"message": "Base de datos poblada exitosamente"}, 200
        except Exception as exc:
            db.session.rollback()
            return {"error": str(exc)}, 500
