from app.errors.exceptions import DatababaseError, NotFoundError
from app.db.models import ReservaORM, db
from app.domain.reserva_estado import ReservaEstado
from app.utils.hold_cache_helper import HoldCacheHelper
from sqlalchemy import not_
from datetime import date, datetime
from uuid import UUID

class ReservaCRUD:
    def __init__(self) -> None:
        self.db = db.session

    def cambiarEstadoReserva(self, data_reserva: dict):
        try:
            #Filtramos reserva por ID
            reserva_id = UUID(str(data_reserva.get('reserva_id')))
            reserva = self.db.query(ReservaORM).filter_by(id = reserva_id).first()

            #Validamos que la reserva exista
            if not reserva:
                raise NotFoundError(f"No se encontró la reserva con ID {data_reserva.get('reserva_id')}")

            #Actualizamos el estado de la reserva
            reserva.estado = data_reserva.get('status')
            self.db.commit()

        except Exception as e:
            self.db.rollback()
            raise DatababaseError(f"Error al cambiar estado de reserva: {str(e)}")

    def _obtener_habitaciones_ocupadas(self, habitacion_ids: list[int | str], check_in: date, check_out: date) -> set[str] | str:
        try:
            habitacion_ids_normalizados = self._normalizar_habitacion_ids(habitacion_ids)

            # Definimos consulta para verificar habitaciones ocupadas
            query = self.db.query(ReservaORM).filter(
                ReservaORM.habitacion_id.in_(habitacion_ids),
                ReservaORM.estado == ReservaEstado.CONFIRMADA.value,
                not_(
                    (ReservaORM.check_out <= check_in) |
                    (ReservaORM.check_in >= check_out)
                )
            )

            # Resultados de las reservas ocupadas
            reservas_ocupadas = query.all()

            # IDs de habitaciones ocupadas normalizados a string
            return {str(reserva_ocupada.habitacion_id) for reserva_ocupada in reservas_ocupadas}

        except Exception as e:
            self.db.rollback()
            raise DatababaseError(f"Error al verificar disponibilidad: {str(e)}")

    def _obtener_habitaciones_ocupadas_cache(self, habitacion_ids: list[int | str], check_in: date, check_out: date) -> set[str] | str:
        try:
            ocupadas_en_cache = set()

            for habitacion_id in habitacion_ids:
                habitacion_id_str = str(habitacion_id)
                disponible_en_cache = HoldCacheHelper.verificar_disponibilidad_cache(
                    habitacion_id_str,
                    check_in,
                    check_out,
                )

                if not disponible_en_cache:
                    ocupadas_en_cache.add(habitacion_id_str)

            return ocupadas_en_cache
        except Exception as e:
            return str(e)

    def existeReservaEnCache(self, habitacion_id: int | str, check_in: date, check_out: date, user_id: int | str | None = None) -> bool | str:
        try:
            if user_id is not None:
                return not HoldCacheHelper.verificar_disponibilidad_cache_para_usuario(
                    str(habitacion_id),
                    check_in,
                    check_out,
                    user_id,
                )

            return not HoldCacheHelper.verificar_disponibilidad_cache(str(habitacion_id), check_in, check_out)
        except Exception as e:
            return str(e)
    
    def verificarDisponibilidad(self, habitacion_ids: list[int | str], check_in: date, check_out: date) -> list[str] | str:
        habitaciones_ids_ocupadas = self._obtener_habitaciones_ocupadas(habitacion_ids, check_in, check_out)
        if isinstance(habitaciones_ids_ocupadas, str):
            return habitaciones_ids_ocupadas

        habitaciones_ids_ocupadas_cache = self._obtener_habitaciones_ocupadas_cache(habitacion_ids, check_in, check_out)
        if isinstance(habitaciones_ids_ocupadas_cache, str):
            return habitaciones_ids_ocupadas_cache

        habitaciones_ids_ocupadas = habitaciones_ids_ocupadas.union(habitaciones_ids_ocupadas_cache)

        # Habitaciones disponibles
        disponibilidad = dict()

        for habitacion_id in habitacion_ids:
            # Convertimos a string para comparar con los IDs ocupados
            habitacion_id = str(habitacion_id)

            # Llenamos el diccionario de disponibilidad
            disponibilidad[habitacion_id] = habitacion_id not in habitaciones_ids_ocupadas

        # Filtramos habitaciones disponibles
        disponibles = list(set(filter(lambda habitacion_id: disponibilidad.get(habitacion_id) is True, disponibilidad.keys())))

        return disponibles

    def verificarDisponibilidadHabitacion(self, habitacion_id: int | str, check_in: date, check_out: date, user_id: int | str | None = None) -> bool | str:
        habitaciones_ids_ocupadas = self._obtener_habitaciones_ocupadas([habitacion_id], check_in, check_out)
        if isinstance(habitaciones_ids_ocupadas, str):
            return habitaciones_ids_ocupadas

        reserva_en_cache = self.existeReservaEnCache(habitacion_id, check_in, check_out, user_id=user_id)
        if isinstance(reserva_en_cache, str):
            return reserva_en_cache

        return (str(habitacion_id) not in habitaciones_ids_ocupadas) and (reserva_en_cache is False)

    @staticmethod
    def _serializar_reserva(reserva: ReservaORM) -> dict:
        created_at_iso = reserva.created_at.isoformat() if reserva.created_at else None
        updated_at_iso = reserva.updated_at.isoformat() if reserva.updated_at else None

        return {
            "id": str(reserva.id),
            "public_id": str(reserva.public_id),
            "habitacion_id": str(reserva.habitacion_id),
            "check_in": reserva.check_in.isoformat(),
            "check_out": reserva.check_out.isoformat(),
            "estado": reserva.estado,
            "created_at": created_at_iso,
            "updated_at": updated_at_iso,
            "fecha_creacion": created_at_iso,
            "fecha_actualizacion": updated_at_iso,
        }

    def crearReserva(self, habitacion_id: int | str, check_in: date, check_out: date, user_id: int | str | None = None) -> dict | str:
        disponible = self.verificarDisponibilidadHabitacion(habitacion_id, check_in, check_out, user_id=user_id)
        if isinstance(disponible, str):
            return disponible

        if not disponible:
            return 'La habitación no está disponible para las fechas seleccionadas'

        try:
            habitacion_uuid = UUID(str(habitacion_id))
        except Exception:
            return 'El habitacion_id debe ser un UUID válido'

        try:
            now = datetime.now()
            reserva = ReservaORM(
                habitacion_id=habitacion_uuid,
                check_in=check_in,
                check_out=check_out,
                estado=ReservaEstado.PENDIENTE.value,
                created_at=now,
                updated_at=now,
            )
            self.db.add(reserva)
            self.db.commit()
            self.db.refresh(reserva)

            if user_id is not None:
                HoldCacheHelper.eliminar_hold_cache(
                    habitacion_id,
                    check_in,
                    check_out,
                    user_id=user_id,
                )

            return self._serializar_reserva(reserva)
        except Exception as e:
            self.db.rollback()
            return str(e)
    
    def obtenerReservasPorHabitacion(self, habitacion_id: int | str) -> list[ReservaORM] | str:
        try: 
            habitacion_uuid = UUID(str(habitacion_id))
            reservas = self.db.query(ReservaORM).filter_by(habitacion_id=habitacion_uuid).all()
            return [
                {
                    "id": str(reserva.id),
                    "public_id": str(reserva.public_id),
                    "habitacion_id": str(reserva.habitacion_id),
                    "user_id": str(reserva.user_id),
                    "check_in": reserva.check_in.isoformat(),
                    "check_out": reserva.check_out.isoformat(),
                    "estado": reserva.estado,
                    "created_at": reserva.created_at.isoformat() if reserva.created_at else None,
                    "updated_at": reserva.updated_at.isoformat() if reserva.updated_at else None,
                }
                for reserva in reservas
            ]
        except Exception as e:
            return str(e)
    
    def confirmarReserva(self, reserva_id: int | str) -> bool | str:
        try:
            reserva_uuid = UUID(str(reserva_id))
            reserva = self.db.query(ReservaORM).filter_by(id=reserva_uuid).first()
            if not reserva:
                return f"No se encontró la reserva con ID {reserva_id}"

            reserva.estado = ReservaEstado.CONFIRMADA.value
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            return str(e)
    
    def revocarReserva(self, reserva_id: int | str) -> bool | str:
        try:
            reserva_uuid = UUID(str(reserva_id))
            reserva = self.db.query(ReservaORM).filter_by(id=reserva_uuid).first()
            if not reserva:
                return f"No se encontró la reserva con ID {reserva_id}"
            self.db.delete(reserva)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            return str(e)
        
    def obtenerReservasPorUsuario(self, user_id: int | str) -> list[ReservaORM] | str:
        try: 
            user_uuid = UUID(str(user_id))
            reservas = self.db.query(ReservaORM).filter_by(user_id=user_uuid).all()
            return [
                {
                    "id": str(reserva.id),
                    "public_id": str(reserva.public_id),
                    "habitacion_id": str(reserva.habitacion_id),
                    "check_in": reserva.check_in.isoformat(),
                    "check_out": reserva.check_out.isoformat(),
                    "estado": reserva.estado,
                    "created_at": reserva.created_at.isoformat() if reserva.created_at else None,
                    "updated_at": reserva.updated_at.isoformat() if reserva.updated_at else None,
                }
                for reserva in reservas
            ]
        except Exception as e:
            return str(e)
    
    def resetDb(self):
        try:
            # Reiniciamos la base de datos
            self.db.query(ReservaORM).delete()
            self.db.query(Payment).delete()
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            raise e
        