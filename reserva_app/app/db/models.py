from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy
import uuid

#Creamos base de datos
db = SQLAlchemy()

class ReservaORM(db.Model):
    __tablename__ = 'reservas'

    id = db.Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    habitacion_id = db.Column(UUID(as_uuid = True), nullable = False)
    check_in = db.Column(db.Date, nullable = False)
    check_out = db.Column(db.Date, nullable = False)
    estado = db.Column(db.String(20), nullable = False, default = 'pendiente')
    created_at = db.Column(db.DateTime, nullable = False, default = db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable = False, default = db.func.current_timestamp(), onupdate = db.func.current_timestamp())

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