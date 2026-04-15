import enum
import uuid
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON, Uuid
from sqlalchemy.dialects.postgresql import JSONB

# Crear instancia
db = SQLAlchemy()
JSON_TYPE = JSONB().with_variant(JSON(), "sqlite")

#Representa el estado FINAL del pago 
# (autorizado, capturado, fallido, etc)
class PaymentStatus(enum.Enum):
    pending = "pending"
    authorized = "authorized"
    captured = "captured"
    failed = "failed"
    cancelled = "cancelled"
    refunded = "refunded"

#Representa cada intento con el proveedor de pago, 
# puede haber varios por cada pago
class TransactionStatus(enum.Enum):
    pending = "pending"
    success = "success"
    failed = "failed"

class PaymentProvider(db.Model):
    __tablename__ = "payment_providers"

    id = db.Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    config = db.Column(JSON_TYPE)  # apiKey + secretKey
    is_active = db.Column(db.Boolean, default=True)
    logo = db.Column(db.String(255), nullable=True) # URL del logo del proveedor
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    payments = db.relationship("Payment", back_populates="provider")


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reserva_id = db.Column(Uuid(as_uuid=True), nullable=False) # ID de la reserva asociada a este pago
    provider_id = db.Column(Uuid(as_uuid=True), db.ForeignKey("payment_providers.id"), nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    status = db.Column(db.Enum(PaymentStatus), nullable=False, default=PaymentStatus.pending)
    provider_payment_id = db.Column(db.String(255), nullable=True)  # ID del proveedor para este pago
    description = db.Column(db.String(255), nullable=True) # Descripción del pago
    payment_metadata = db.Column("metadata", JSON_TYPE, nullable=True) # Información adicional
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    provider = db.relationship("PaymentProvider", back_populates="payments")
    transactions = db.relationship("PaymentTransaction", back_populates="payment")


class PaymentTransaction(db.Model):
    __tablename__ = "payment_transactions"

    id = db.Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_id = db.Column(Uuid(as_uuid=True), db.ForeignKey("payments.id"))
    status = db.Column(db.Enum(TransactionStatus), nullable=False, default=TransactionStatus.pending)
    provider_transaction_id = db.Column(db.String(255), nullable=False) # ID de la transacción en el proveedor
    url = db.Column(db.String(255), nullable=True) # URL para redirigir al usuario (si aplica) puede ser null si falla la solicitud al proveedor
    response = db.Column(JSON_TYPE, nullable=True) # Respuesta completa del proveedor para auditoría
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    payment = db.relationship("Payment", back_populates="transactions")