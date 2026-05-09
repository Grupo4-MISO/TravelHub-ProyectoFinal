from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import uuid
import enum

# Crear instancia
db = SQLAlchemy()


class TarifaStatus(enum.Enum):
    Active = "Active"
    Inactive = "Inactive"
    Archived = "Archived"


class Tarifa(db.Model):
    __tablename__ = "tarifas"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = db.Column(db.String(100), nullable=True, index=True)
    hotel_id = db.Column(db.String(50), nullable=False, index=True)
    identificador = db.Column(db.String(100), nullable=True, unique=True, index=True)
    descripcion = db.Column(db.String(500), nullable=True)
    valor_base = db.Column(db.Float, nullable=False)
    moneda = db.Column(db.String(3), nullable=False)
    categoria_habitacion = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.Enum(TarifaStatus), nullable=False, default=TarifaStatus.Active)
    vigencia_inicio = db.Column(db.DateTime(timezone=True), nullable=False)
    vigencia_fin = db.Column(db.DateTime(timezone=True), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    descuentos = db.relationship('Descuento', backref='tarifa', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Tarifa {self.nombre}>'


class Descuento(db.Model):
    __tablename__ = "descuentos"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = db.Column(db.String(100), nullable=True, index=True)
    tarifa_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tarifas.id'), nullable=False, index=True)
    porcentaje = db.Column(db.Float, nullable=False)
    activo = db.Column(db.Boolean, nullable=False, default=True, index=True)
    vigencia_inicio = db.Column(db.DateTime(timezone=True), nullable=False)
    vigencia_fin = db.Column(db.DateTime(timezone=True), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
