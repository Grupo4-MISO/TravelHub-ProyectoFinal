from app.db.models import db, ReservaORM
from app.domain.reserva_estado import ReservaEstado
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
                    estado = random.choice([ReservaEstado.CONFIRMADA.value, ReservaEstado.PENDIENTE.value])

                    reserva = ReservaORM(
                        habitacion_id=uuid.UUID(habitacion),
                        check_in=check_in,
                        check_out=check_out,
                        estado=estado,
                    )
                    db.session.add(reserva)
                    reservas_insertadas += 1

            db.session.commit()

            result = {
                "ok": True,
                "solicitadas": cantidad,
                "reservas_insertadas": reservas_insertadas,
            }

            return result

        except Exception as e:
            db.session.rollback()
            return {"ok": False, "error": str(e)}
