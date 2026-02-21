"""
Modelos SQLAlchemy para SQLite con triggers adaptados
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, DateTime, Decimal, ForeignKey, Text, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from .database_sqlite import Base


class Suscriptor(Base):
    __tablename__ = "suscriptores"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_contrato = Column(String(50), unique=True, nullable=False, index=True)
    cedula = Column(String(20), unique=True, nullable=False, index=True)
    nombre_completo = Column(String(255), nullable=False)
    fecha_suscripcion = Column(Date, nullable=False, index=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    pagos = relationship("Pago", back_populates="suscriptor", cascade="all, delete-orphan")


class Pago(Base):
    __tablename__ = "pagos"
    
    id = Column(Integer, primary_key=True, index=True)
    suscriptor_id = Column(Integer, ForeignKey("suscriptores.id", ondelete="CASCADE"), nullable=False, index=True)
    mes = Column(Integer, nullable=False, index=True)
    anio = Column(Integer, nullable=False, index=True)
    fecha_pago = Column(Date, nullable=False, index=True)
    valor = Column(Decimal(10, 2), nullable=False)
    tipo_pago = Column(String(20), nullable=False)  # 'efectivo' o 'transferencia'
    
    # Campos específicos para transferencia
    entidad_bancaria = Column(String(100), nullable=True)
    nombre_transferente = Column(String(255), nullable=True)
    
    # Campos específicos para efectivo
    monto_efectivo = Column(Decimal(10, 2), nullable=True)
    
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    # Restricciones
    __table_args__ = (
        CheckConstraint('mes >= 1 AND mes <= 12', name='check_mes_rango'),
        CheckConstraint('anio >= 2000', name='check_anio_minimo'),
        CheckConstraint('valor > 0', name='check_valor_positivo'),
        CheckConstraint("tipo_pago IN ('efectivo', 'transferencia')", name='check_tipo_pago'),
        UniqueConstraint('suscriptor_id', 'mes', 'anio', name='uq_pago_mes_anio'),
    )
    
    # Relaciones
    suscriptor = relationship("Suscriptor", back_populates="pagos")
    recibo = relationship("Recibo", back_populates="pago", uselist=False, cascade="all, delete-orphan")
    ingreso = relationship("Ingreso", back_populates="pago", uselist=False, cascade="all, delete-orphan")


class Recibo(Base):
    __tablename__ = "recibos"
    
    id = Column(Integer, primary_key=True, index=True)
    pago_id = Column(Integer, ForeignKey("pagos.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    numero_recibo = Column(String(50), unique=True, nullable=False, index=True)
    fecha_emision = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    pago = relationship("Pago", back_populates="recibo")


class Ingreso(Base):
    __tablename__ = "ingresos"
    
    id = Column(Integer, primary_key=True, index=True)
    pago_id = Column(Integer, ForeignKey("pagos.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    monto = Column(Decimal(10, 2), nullable=False)
    fecha = Column(Date, nullable=False, index=True)
    origen = Column(String(255), nullable=False, default='pago de suscriptor')
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    # Restricciones
    __table_args__ = (
        CheckConstraint('monto > 0', name='check_monto_positivo'),
    )
    
    # Relaciones
    pago = relationship("Pago", back_populates="ingreso")


class Gasto(Base):
    __tablename__ = "gastos"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo_gasto = Column(String(50), nullable=False, index=True)
    descripcion = Column(Text, nullable=False)
    valor = Column(Decimal(10, 2), nullable=False)
    fecha = Column(Date, nullable=False, index=True)
    
    # Campos adicionales según tipo de gasto
    lugar_compra = Column(String(255), nullable=True)
    motivo = Column(String(255), nullable=True)
    
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    # Restricciones
    __table_args__ = (
        CheckConstraint('valor > 0', name='check_gasto_valor_positivo'),
    )
