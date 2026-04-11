from app.errors.exceptions import DatababaseError
from app.db.models import ReservaORM, db
from sqlalchemy import not_
from datetime import date
from uuid import UUID

class ReservaCRUD:
    def __init__(self) -> None:
        self.db = db.session

    def _obtener_habitaciones_ocupadas(self, habitacion_ids: list[int | str], check_in: date, check_out: date) -> set[str] | str:
        try:
            # Definimos consulta para verificar habitaciones ocupadas
            query = self.db.query(ReservaORM).filter(
                ReservaORM.habitacion_id.in_(habitacion_ids),
                ReservaORM.estado == 'confirmada',
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
            return str(e)
    
    def verificarDisponibilidad(self, habitacion_ids: list[int | str], check_in: date, check_out: date) -> list[str] | str:
        habitaciones_ids_ocupadas = self._obtener_habitaciones_ocupadas(habitacion_ids, check_in, check_out)
        if isinstance(habitaciones_ids_ocupadas, str):
            return habitaciones_ids_ocupadas

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

    def verificarDisponibilidadHabitacion(self, habitacion_id: int | str, check_in: date, check_out: date) -> bool | str:
        habitaciones_ids_ocupadas = self._obtener_habitaciones_ocupadas([habitacion_id], check_in, check_out)
        if isinstance(habitaciones_ids_ocupadas, str):
            return habitaciones_ids_ocupadas

        return str(habitacion_id) not in habitaciones_ids_ocupadas
    
    def obtenerReservasPorHabitacion(self, habitacion_id: int | str) -> list[ReservaORM] | str:
        try: 
            habitacion_uuid = UUID(str(habitacion_id))
            reservas = self.db.query(ReservaORM).filter_by(habitacion_id=habitacion_uuid).all()
            return [
                {
                    "id": str(reserva.id),
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
        