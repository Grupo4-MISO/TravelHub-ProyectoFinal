from datetime import datetime, timezone
from uuid import UUID

from flask import request
from flask_restful import Resource

from app.db.models import Tarifa, TarifaStatus, db

CATEGORIAS_HABITACION = {
    "SENCILLA",
    "DOBLE",
    "TRIPLE",
    "SUITE",
    "DELUXE",
    "FAMILIAR",
}

MONEDAS_PERMITIDAS = {"COP", "USD", "PEN", "MXN", "CLP", "ARS"}


def _parse_iso_datetime(value, field_name):
    if value is None or value == "":
        raise ValueError(f"El campo '{field_name}' es requerido")
    if not isinstance(value, str):
        raise ValueError(f"El campo '{field_name}' debe estar en formato ISO-8601")
    try:
        normalized = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
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


def _serialize_tarifa(tarifa):
    return {
        "id": str(tarifa.id),
        "nombre": tarifa.nombre,
        "identificador": tarifa.identificador,
        "descripcion": tarifa.descripcion,
        "valor_noche": tarifa.valor_noche,
        "moneda": tarifa.moneda,
        "categoria_habitacion": tarifa.categoria_habitacion,
        "estado": tarifa.estado.name if tarifa.estado else None,
        "vigencia_inicio": tarifa.vigencia_inicio.isoformat(),
        "vigencia_fin": tarifa.vigencia_fin.isoformat(),
        "vigente": _is_tarifa_vigente(tarifa),
        "created_at": tarifa.created_at.isoformat() if hasattr(tarifa.created_at, "isoformat") else tarifa.created_at,
        "updated_at": tarifa.updated_at.isoformat() if hasattr(tarifa.updated_at, "isoformat") else tarifa.updated_at,
    }


class Health(Resource):
    def get(self):
        return {"status": "healthy"}, 200


class TarifaListResource(Resource):
    def get(self):
        try:
            vigentes = _parse_bool_param(request.args.get("vigentes"), "vigentes")
            tarifas = Tarifa.query.all()
            if vigentes is not None:
                tarifas = [tarifa for tarifa in tarifas if _is_tarifa_vigente(tarifa) is vigentes]
            return [_serialize_tarifa(tarifa) for tarifa in tarifas], 200
        except ValueError as exc:
            return {"error": str(exc)}, 400

    def post(self):
        try:
            data = request.get_json(silent=True) or {}

            if not data.get("nombre") and not data.get("identificador"):
                return {"error": "Debe enviar al menos 'nombre' o 'identificador'"}, 400

            required_fields = [
                "valor_noche",
                "moneda",
                "categoria_habitacion",
                "vigencia_inicio",
                "vigencia_fin",
            ]
            for field in required_fields:
                if data.get(field) in (None, ""):
                    return {"error": f"El campo '{field}' es requerido"}, 400

            valor_noche = float(data.get("valor_noche"))
            if valor_noche <= 0:
                return {"error": "El campo 'valor_noche' debe ser mayor a 0"}, 400

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
                identificador=identificador,
                descripcion=data.get("descripcion", ""),
                valor_noche=valor_noche,
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


class TarifaResource(Resource):
    def get(self, tarifa_id):
        try:
            tarifa_uuid = UUID(tarifa_id)
            tarifa = Tarifa.query.filter_by(id=tarifa_uuid).first()
            if not tarifa:
                return {"error": "Tarifa no encontrada"}, 404
            return _serialize_tarifa(tarifa), 200
        except ValueError:
            return {"error": "El id de la tarifa no tiene un formato UUID valido"}, 400
        except Exception as exc:
            return {"error": str(exc)}, 500

    def put(self, tarifa_id):
        try:
            tarifa_uuid = UUID(tarifa_id)
            tarifa = Tarifa.query.filter_by(id=tarifa_uuid).first()
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
            if "valor_noche" in data:
                valor_noche = float(data["valor_noche"])
                if valor_noche <= 0:
                    return {"error": "El campo 'valor_noche' debe ser mayor a 0"}, 400
                tarifa.valor_noche = valor_noche
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

    def delete(self, tarifa_id):
        try:
            tarifa_uuid = UUID(tarifa_id)
            tarifa = Tarifa.query.filter_by(id=tarifa_uuid).first()
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


class SeedDB(Resource):
    def post(self):
        try:
            if Tarifa.query.first() is not None:
                return {"message": "Base de datos ya contiene datos"}, 200

            tarifas_ejemplo = [
                Tarifa(
                    nombre="Tarifa Basica",
                    identificador="TAR-BASICA-001",
                    descripcion="Tarifa basica para alojamiento",
                    valor_noche=50.0,
                    moneda="COP",
                    categoria_habitacion="SENCILLA",
                    vigencia_inicio=datetime(2026, 1, 1, 0, 0, 0),
                    vigencia_fin=datetime(2026, 12, 31, 23, 59, 59),
                ),
                Tarifa(
                    nombre="Tarifa Premium",
                    identificador="TAR-PREM-001",
                    descripcion="Tarifa premium con servicios adicionales",
                    valor_noche=100.0,
                    moneda="USD",
                    categoria_habitacion="DELUXE",
                    vigencia_inicio=datetime(2026, 1, 1, 0, 0, 0),
                    vigencia_fin=datetime(2026, 8, 31, 23, 59, 59),
                ),
                Tarifa(
                    nombre="Tarifa Legacy",
                    identificador="TAR-LEG-001",
                    descripcion="Tarifa historica no vigente",
                    valor_noche=30.0,
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
