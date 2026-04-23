from app.db.models import db, ReservaORM
from sqlalchemy import text
from datetime import date, timedelta
import random
import uuid

# Ventana temporal del seed: desde hoy hasta 6 meses adelante
_VENTANA_DIAS = 180
# Duración mínima y máxima de una estadía (noches)
_DURACION_MIN = 1
_DURACION_MAX = 14
# Intentos máximos por reserva antes de abandonar (evita bucle infinito)
_MAX_INTENTOS_FACTOR = 300
_MAX_RESERVAS_POR_USUARIO = 15

TRAVELERS_FALLBACK = [
    {"id": uuid.UUID("ed4be7ea-b9f0-42b7-97fc-4808d359ba70"), "reservas": 0},
    {"id": uuid.UUID("f12f3c5d-da80-4a54-b9d8-f6b1a3cb272a"), "reservas": 0},
    {"id": uuid.UUID("a1aaf0dc-36b6-422d-87fe-3c04173c88ef"), "reservas": 0},
    {"id": uuid.UUID("8a6f2b3c-1d4e-4a8d-9c1f-4bb3f6d7a101"), "reservas": 0},
    {"id": uuid.UUID("c1e4d5f6-2a3b-4c4d-8e9f-5a6b7c8d9e10"), "reservas": 0},
    {"id": uuid.UUID("d2f3a4b5-6c7d-4e8f-9a10-1b2c3d4e5f60"), "reservas": 0},
    {"id": uuid.UUID("e3a4b5c6-7d8e-4f90-9a11-2c3d4e5f6071"), "reservas": 0},
    {"id": uuid.UUID("f4b5c6d7-8e9f-4012-8a13-3d4e5f607182"), "reservas": 0},
    {"id": uuid.UUID("a5c6d7e8-9f01-4123-8a14-4e5f60718293"), "reservas": 0},
    {"id": uuid.UUID("b6d7e8f9-0a12-4234-8a15-5f60718293a4"), "reservas": 0},
    {"id": uuid.UUID("c7e8f90a-1b23-4345-8a16-60718293a4b5"), "reservas": 0},
    {"id": uuid.UUID("d8f90a1b-2c34-4456-8a17-718293a4b5c6"), "reservas": 0},
    {"id": uuid.UUID("e90a1b2c-3d45-4567-8a18-8293a4b5c6d7"), "reservas": 0},
    {"id": uuid.UUID("0a1b2c3d-4e56-4678-8a19-93a4b5c6d7e8"), "reservas": 0},
    {"id": uuid.UUID("1b2c3d4e-5f67-4789-8a1a-a4b5c6d7e8f9"), "reservas": 0},
    {"id": uuid.UUID("2c3d4e5f-6071-4890-8a1b-b5c6d7e8f90a"), "reservas": 0},
    {"id": uuid.UUID("3d4e5f60-7182-4901-8a1c-c6d7e8f90a1b"), "reservas": 0},
    {"id": uuid.UUID("4e5f6071-8293-4a12-8a1d-d7e8f90a1b2c"), "reservas": 0},
    {"id": uuid.UUID("5f607182-93a4-4b23-8a1e-e8f90a1b2c3d"), "reservas": 0},
    {"id": uuid.UUID("60718293-a4b5-4c34-8a1f-f90a1b2c3d4e"), "reservas": 0},
    {"id": uuid.UUID("3520ec74-3072-4f7f-b9fc-52bc993d649d"), "reservas": 0}
]

DEFAULT_USER = {"id": uuid.UUID("b3b2fc2c-914a-4210-8cb2-2db02c8d796b")}


def _obtener_habitacion_ids():
    """
    Consulta la tabla habitaciones (gestionada por inventario_app) y
    devuelve una lista de UUIDs como strings.
    """
    resultado = db.session.execute(text("SELECT id FROM habitaciones"))
    return [str(fila[0]) for fila in resultado.fetchall()]


def _hay_solapamiento(ocupaciones, nuevo_ci, nuevo_co):
    """
    Retorna True si [nuevo_ci, nuevo_co) se solapa con alguna reserva
    ya registrada para esa habitación.
    Condición de solapamiento: nuevo_ci < co_existente AND nuevo_co > ci_existente
    """
    for (ci, co) in ocupaciones:
        if nuevo_ci < co and nuevo_co > ci:
            return True
    return False


class SeedHelper:
    """Genera reservas aleatorias respetando la no-superposición de fechas."""

    @staticmethod
    def reset_and_seed(cantidad: int):
        """
        Borra todas las reservas existentes e inserta `cantidad` reservas
        aleatorias distribuidas en una ventana de 6 meses desde hoy.

        Restricciones:
          - habitacion_id debe existir en la tabla habitaciones.
          - Los rangos [check_in, check_out) de una misma habitación no se cruzan.
          - Estado: 'confirmada' o 'pendiente' de forma aleatoria.

        Args:
            cantidad (int): Número de reservas a generar.
            habitacion_ids (list[str]): Lista de IDs de habitaciones válidas.

        Returns:
            dict con ok, reservas_insertadas, solicitadas y, si aplica, advertencia.
        """
        try:
            # ── 1. Obtener habitaciones válidas ──────────────────────────────
            habitacion_ids = _obtener_habitacion_ids()

            if not habitacion_ids:
                return {
                    "ok": False,
                    "error": "No existen habitaciones en la base de datos. "
                             "Ejecuta primero el seed de inventario_app.",
                }

            # ── 2. Limpiar reservas existentes ───────────────────────────────
            ReservaORM.query.delete()
            db.session.flush()

            # ── 3. Preparar ventana temporal ─────────────────────────────────
            hoy = date.today()
            fecha_fin = hoy + timedelta(days=_VENTANA_DIAS)
            reservas_totales = 0

            for habitacion in habitacion_ids:
                reservas_insertadas = 0
                intentos = 0
                ocupaciones = []
                while reservas_insertadas < cantidad and intentos < _MAX_INTENTOS_FACTOR:
                    intentos += 1
                    # check_in aleatorio dentro de la ventana (dejando al menos 1 noche)
                    margen_dias = (fecha_fin - hoy).days - _DURACION_MIN
                    if margen_dias <= 0:
                        continue

                    offset_ci = random.randint(0, margen_dias)
                    check_in = hoy + timedelta(days=offset_ci)

                    # Duración aleatoria sin salir de la ventana
                    max_duracion = min(_DURACION_MAX, (fecha_fin - check_in).days)
                    if max_duracion < _DURACION_MIN:
                        continue

                    duracion = random.randint(_DURACION_MIN, max_duracion)
                    check_out = check_in + timedelta(days=duracion)

                    # Verificar solapamiento
                    if _hay_solapamiento(ocupaciones, check_in, check_out):
                        continue

                    # Registrar ocupación
                    ocupaciones.append((check_in, check_out))

                    # Estado aleatorio
                    estado = random.choice(["confirmada", "pendiente"])

                    usuario_aleatorio = random.choice(TRAVELERS_FALLBACK)
                    if usuario_aleatorio["reservas"] >= _MAX_RESERVAS_POR_USUARIO:
                        usuario_aleatorio = DEFAULT_USER

                    reserva = ReservaORM(
                        habitacion_id=uuid.UUID(habitacion),
                        user_id = usuario_aleatorio["id"],
                        check_in=check_in,
                        check_out=check_out,
                        estado=estado,
                    )
                    db.session.add(reserva)
                    reservas_insertadas += 1
                    reservas_totales += 1

            db.session.commit()

            result = {
                "ok": True,
                "solicitadas": cantidad,
                "reservas_insertadas": reservas_totales,
            }

            return result

        except Exception as e:
            db.session.rollback()
            return {"ok": False, "error": str(e)}
