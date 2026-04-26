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

DEFAULT_USER = {"id": uuid.UUID("b3b2fc2c-914a-4210-8cb2-2db02c8d796b"), "reservas":0}

ROOMS_DEFAULT = [
    {"id": uuid.UUID("46f50af3-f0c8-401a-93b1-2f1c17ad36e8")}, 
    {"id": uuid.UUID("6c0b7f21-e00e-4801-bd3e-edb755489be2")}, 
    {"id": uuid.UUID("58f2f88e-43ab-48c9-981e-9345d4f0d7e4")}, 
    {"id": uuid.UUID("a8b7436f-2329-480b-8826-857296842dc6")}, 
    {"id": uuid.UUID("c12d9860-6980-4305-bd0f-6bc023e484c8")}, 
    {"id": uuid.UUID("168fdd6d-ceea-4f03-a029-f65dc61c148b")}, 
    {"id": uuid.UUID("aee846a4-b540-5ab1-83be-aea569053393")}, 
    {"id": uuid.UUID("930c3fab-34a2-56de-be9f-defcef0c1ee5")}, 
    {"id": uuid.UUID("011db853-35f6-5891-af51-688c01727518")}, 
    {"id": uuid.UUID("f03b6889-443f-5d1b-b101-af14a11095d6")}, 
    {"id": uuid.UUID("cd818041-b021-5a23-93f7-d31cf4ea784b")}, 
    {"id": uuid.UUID("81471e49-54d5-5f85-8b38-4e329bdd94ed")}, 
    {"id": uuid.UUID("71ff332b-b767-5338-924e-ce75f7c2bad5")}, 
    {"id": uuid.UUID("d1fcf297-72d9-5e97-a666-3ab1207adb08")}, 
    {"id": uuid.UUID("c046fcd9-8d33-5426-bee4-818f79859861")}, 
    {"id": uuid.UUID("f91d422a-45c2-519f-9453-7ff8681940ac")}, 
    {"id": uuid.UUID("c1eac988-2624-54c3-856c-753ba138a0d0")}, 
    {"id": uuid.UUID("8dcba403-556a-5969-a83a-3fd3c6c6bdcb")}, 
    {"id": uuid.UUID("0ad9b137-703f-56d5-ba88-ff0f89772847")}, 
    {"id": uuid.UUID("d639d4ba-ed4f-53fa-bce3-37c371afb661")}, 
    {"id": uuid.UUID("827a6c25-7d44-5606-ab4f-e44b154a9123")}, 
    {"id": uuid.UUID("fc607564-0b5f-57d5-8027-bd6d84f0fdd9")}, 
    {"id": uuid.UUID("776becf5-c253-5fdc-a891-a90b126c35d0")}, 
    {"id": uuid.UUID("df0f27ce-ca58-5aaf-ae4a-29e42a9a5d7f")}, 
    {"id": uuid.UUID("f4d97608-5a73-56ca-a48a-3131e656d298")}, 
    {"id": uuid.UUID("c37ad2ca-d293-512c-8245-4d01f57e210b")}, 
    {"id": uuid.UUID("494c0de6-286f-5646-b872-7b5ceab4657d")}, 
    {"id": uuid.UUID("123b67e5-4c70-58e3-ae45-7bd33b3bd675")}, 
    {"id": uuid.UUID("dbde0bf9-40b4-5b80-af74-fb3397892adf")}, 
    {"id": uuid.UUID("92a15cb7-b3ef-5a40-b544-adce6c1cd7d8")}, 
    {"id": uuid.UUID("dff85b84-ec52-5f09-b2c7-020eeac630dd")}, 
    {"id": uuid.UUID("51d47de0-6e91-5c38-a177-8827b4f4a76e")}, 
    {"id": uuid.UUID("f6fd45c0-9b4a-5c9d-b967-0aa3f5485e83")}, 
    {"id": uuid.UUID("d2db799c-00f5-5f5f-8e6d-eecb4983dbb5")}, 
    {"id": uuid.UUID("8336fb33-6844-517e-95d8-75e68fac3513")}, 
    {"id": uuid.UUID("6f4260dd-404b-5505-a6d2-ce3bbd163c6c")} 
]


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
                    estado = random.choice([ReservaEstado.CONFIRMADA.value, ReservaEstado.PENDIENTE.value])

                    if habitacion in [str(r["id"]) for r in ROOMS_DEFAULT]:
                        usuario_aleatorio = random.choice(TRAVELERS_FALLBACK)
                    else:
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
                    usuario_aleatorio["reservas"] += 1

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
