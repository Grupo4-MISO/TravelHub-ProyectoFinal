from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import validates
from flask_sqlalchemy import SQLAlchemy
from app.domain.reserva_estado import ReservaEstado
import uuid

#Creamos base de datos
db = SQLAlchemy()

class ReservaORM(db.Model):
    __tablename__ = 'reservas'
    id = db.Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    public_id = db.Column(db.String(12), unique=True, nullable=False, index=True, default=lambda: "RSV-" + uuid.uuid4().hex[:8].upper())
    habitacion_id = db.Column(UUID(as_uuid = True), nullable = False)
    check_in = db.Column(db.Date, nullable = False)
    check_out = db.Column(db.Date, nullable = False)
    estado = db.Column(db.String(20), nullable = False, default = ReservaEstado.PENDIENTE.value)
    created_at = db.Column(db.DateTime, nullable = False, default = db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable = False, default = db.func.current_timestamp(), onupdate = db.func.current_timestamp())

    @validates('estado')
    def validate_estado(self, _key, estado):
        estado_normalizado = estado.value if isinstance(estado, ReservaEstado) else str(estado)
        estados_validos = {value.value for value in ReservaEstado}
        if estado_normalizado not in estados_validos:
            raise ValueError(f"Estado de reserva inválido: {estado_normalizado}")
        return estado_normalizado

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    reserva_id = db.Column(UUID(as_uuid = True), db.ForeignKey('reservas.id'), nullable = False)
    amount = db.Column(db.Float, nullable = False) # El monto total a pagar
    currency = db.Column(db.String(3), nullable = False) # Ejemplo: 'USD', 'COP', etc.
    payment_method = db.Column(db.String(50), nullable = False) # Ejemplo: 'tarjeta_credito', 'paypal', etc.
    status = db.Column(db.String(20), nullable = False, default = 'pendiente')
    created_at = db.Column(db.DateTime, nullable = False, default = db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable = False, default = db.func.current_timestamp(), onupdate = db.func.current_timestamp())