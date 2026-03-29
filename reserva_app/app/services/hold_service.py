from app.utils.hold_cache_helper import HoldCacheHelper
from app.db.models import db
from app.services.reserva_crud import ReservaCRUD
from flask import current_app

class HoldService:
    def __init__(self):
        self.db = db.session
        self.reserva_crud = ReservaCRUD()

    def _get_hold_ttl_seconds(self):
        ttl_config = current_app.config.get('HOLD_TTL_SECONDS', 900)
        try:
            ttl = int(ttl_config)
        except (TypeError, ValueError):
            ttl = 900

        return max(1, ttl)

    # ------------------------------------------------------------------
    # Método principal: orquesta el flujo de reserva temporal
    # ------------------------------------------------------------------
    def crear_hold(self, user_id, habitacion_id, check_in, check_out):
        """
        Crea una reserva temporal por 15 minutos (900 segundos).

        Flujo:
          1. Verifica que no exista una reserva real confirmada en BD.
          2. Verifica que no exista una reserva temporal en caché.
          3. Crea el bloqueo temporal en caché.
          4. Retorna el resultado del hold.

        Retorna:
          dict  con el resultado del hold, o
          str   con el mensaje de error (sigue la convención de reserva_crud).
        """
        try:
            hold_ttl_seconds = self._get_hold_ttl_seconds()

            # Paso 1 — Verificar disponibilidad en base de datos
            disponible_en_bd = self._verificar_disponibilidad_bd(habitacion_id, check_in, check_out)
            if isinstance(disponible_en_bd, str):
                return disponible_en_bd
            if not disponible_en_bd:
                return {'disponible': False, 'motivo': 'La habitación ya tiene una reserva confirmada en esas fechas'}

            # Paso 2 — Si existe hold exacto del mismo usuario, renovamos TTL
            hold_existente = HoldCacheHelper.buscar_hold_cache(habitacion_id, check_in, check_out)
            if hold_existente:
                if str(hold_existente.get('user_id')) != str(user_id):
                    return {'disponible': False, 'motivo': 'La habitación ya tiene una reserva temporal activa en esas fechas'}

                hold_actualizado = HoldCacheHelper.actualizar_hold_cache(
                    habitacion_id=habitacion_id,
                    check_in=check_in,
                    check_out=check_out,
                    user_id=user_id,
                    ttl_segundos=hold_ttl_seconds,
                )
                if hold_actualizado:
                    return {'disponible': True, 'hold': hold_actualizado}

            # Paso 3 — Verificar que no haya un hold activo en caché
            disponible_en_cache = HoldCacheHelper.verificar_disponibilidad_cache(habitacion_id, check_in, check_out)
            if not disponible_en_cache:
                return {'disponible': False, 'motivo': 'La habitación ya tiene una reserva temporal activa en esas fechas'}

            # Paso 4 — Crear el hold en caché (TTL = 15 minutos)
            hold = HoldCacheHelper.crear_hold_cache(
                user_id=user_id,
                habitacion_id=habitacion_id,
                check_in=check_in,
                check_out=check_out,
                ttl_segundos=hold_ttl_seconds
            )

            # Paso 5 — Retornar resultado
            return {
                'disponible': True,
                'hold': hold
            }

        except Exception as e:
            return str(e)

    # ------------------------------------------------------------------
    # Método privado: verifica disponibilidad en base de datos
    # ------------------------------------------------------------------
    def _verificar_disponibilidad_bd(self, habitacion_id, check_in, check_out):
        """
        Verifica disponibilidad consultando ReservaCRUD.

        Retorna:
          bool si la habitación está disponible.
          str  con el mensaje de error en caso de falla.
        """
        # TODO: Reemplazar esta consulta directa por el servicio externo de consultas
        # cuando se implemente el patrón CQRS.
        return self.reserva_crud.verificarDisponibilidadHabitacion(habitacion_id, check_in, check_out)
