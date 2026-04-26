from enum import Enum


class ReservaEstado(str, Enum):
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
