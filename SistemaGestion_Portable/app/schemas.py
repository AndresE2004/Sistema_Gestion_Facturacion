"""
Esquemas Pydantic para validación de datos
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator


# ============================================
# Esquemas de Suscriptor
# ============================================
class SuscriptorBase(BaseModel):
    numero_contrato: str = Field(..., min_length=1, max_length=50, description="Número único de contrato")
    cedula: str = Field(..., min_length=1, max_length=20, description="Cédula del suscriptor")
    nombre_completo: str = Field(..., min_length=1, max_length=255, description="Nombre completo")
    fecha_suscripcion: date = Field(..., description="Fecha de suscripción")


class SuscriptorCreate(SuscriptorBase):
    pass


class SuscriptorUpdate(BaseModel):
    numero_contrato: Optional[str] = Field(None, min_length=1, max_length=50)
    cedula: Optional[str] = Field(None, min_length=1, max_length=20)
    nombre_completo: Optional[str] = Field(None, min_length=1, max_length=255)
    fecha_suscripcion: Optional[date] = None


class Suscriptor(SuscriptorBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True


# ============================================
# Esquemas de Pago
# ============================================
class PagoEfectivo(BaseModel):
    monto_efectivo: float = Field(..., gt=0, description="Monto pagado en efectivo")


class PagoTransferencia(BaseModel):
    entidad_bancaria: str = Field(..., min_length=1, max_length=100, description="Entidad bancaria")
    nombre_transferente: str = Field(..., min_length=1, max_length=255, description="Nombre de quien realizó la transferencia")


class PagoBase(BaseModel):
    suscriptor_id: int = Field(..., description="ID del suscriptor")
    mes: int = Field(..., ge=1, le=12, description="Mes del pago (1-12)")
    anio: int = Field(..., ge=2000, description="Año del pago")
    fecha_pago: date = Field(..., description="Fecha exacta en que se realizó el pago")
    valor: float = Field(..., gt=0, description="Valor pagado")
    tipo_pago: str = Field(..., description="Tipo de pago: 'efectivo' o 'transferencia'")


class PagoCreate(PagoBase):
    # Campos opcionales según tipo de pago
    entidad_bancaria: Optional[str] = Field(None, max_length=100)
    nombre_transferente: Optional[str] = Field(None, max_length=255)
    monto_efectivo: Optional[float] = Field(None, gt=0)

    @field_validator('tipo_pago')
    @classmethod
    def validar_tipo_pago(cls, v):
        if v not in ['efectivo', 'transferencia']:
            raise ValueError("tipo_pago debe ser 'efectivo' o 'transferencia'")
        return v

    @model_validator(mode='after')
    def validar_campos_segun_tipo(self):
        if self.tipo_pago == 'transferencia':
            if not self.entidad_bancaria or not self.nombre_transferente:
                raise ValueError("entidad_bancaria y nombre_transferente son requeridos para transferencias")
        elif self.tipo_pago == 'efectivo':
            if self.monto_efectivo is None:
                raise ValueError("monto_efectivo es requerido para pagos en efectivo")
        return self


class Pago(PagoBase):
    id: int
    entidad_bancaria: Optional[str]
    nombre_transferente: Optional[str]
    monto_efectivo: Optional[float]
    fecha_creacion: datetime
    suscriptor: Optional[Suscriptor] = None

    class Config:
        from_attributes = True


# ============================================
# Esquemas de Recibo
# ============================================
class Recibo(BaseModel):
    id: int
    pago_id: int
    numero_recibo: str
    fecha_emision: datetime
    pago: Optional[Pago] = None

    class Config:
        from_attributes = True


# ============================================
# Esquemas de Ingreso
# ============================================
class IngresoBase(BaseModel):
    monto: float = Field(..., gt=0)
    fecha: date
    origen: str


class Ingreso(IngresoBase):
    id: int
    pago_id: int
    fecha_creacion: datetime
    pago: Optional[Pago] = None

    class Config:
        from_attributes = True


# ============================================
# Esquemas de Gasto
# ============================================
class GastoBase(BaseModel):
    tipo_gasto: str = Field(..., min_length=1, max_length=50, description="Tipo de gasto (ej: compra_repuestos, pago_trabajador)")
    descripcion: str = Field(..., min_length=1, description="Descripción del gasto")
    valor: float = Field(..., gt=0, description="Valor del gasto")
    fecha: date = Field(..., description="Fecha en que se realizó el gasto")
    lugar_compra: Optional[str] = Field(None, max_length=255, description="Lugar donde se compró (para compras)")
    motivo: Optional[str] = Field(None, max_length=255, description="Motivo del gasto (ej: arreglo, mantenimiento)")


class GastoCreate(GastoBase):
    pass


class GastoUpdate(BaseModel):
    tipo_gasto: Optional[str] = Field(None, min_length=1, max_length=50)
    descripcion: Optional[str] = Field(None, min_length=1)
    valor: Optional[float] = Field(None, gt=0)
    fecha: Optional[date] = None
    lugar_compra: Optional[str] = Field(None, max_length=255)
    motivo: Optional[str] = Field(None, max_length=255)


class Gasto(GastoBase):
    id: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True


# ============================================
# Esquemas de Balance
# ============================================
class Balance(BaseModel):
    total_ingresos: float
    total_gastos: float
    balance_total: float


class BalancePorFecha(BaseModel):
    fecha: date
    ingresos_dia: float
    gastos_dia: float
    balance_dia: float


class BalanceRango(BaseModel):
    fecha_inicio: date
    fecha_fin: date
    total_ingresos: float
    total_gastos: float
    balance_total: float

