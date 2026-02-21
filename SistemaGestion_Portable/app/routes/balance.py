"""
Rutas para consulta de balances financieros
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional
from datetime import date
from decimal import Decimal
from app import schemas, models
from app.database import get_db

router = APIRouter(prefix="/balance", tags=["Balance Financiero"])


@router.get("/", response_model=schemas.Balance)
def obtener_balance_general(db: Session = Depends(get_db)):
    """
    Obtener el balance financiero general (todos los ingresos y gastos)
    """
    total_ingresos = db.query(func.coalesce(func.sum(models.Ingreso.monto), 0)).scalar() or Decimal('0')
    total_gastos = db.query(func.coalesce(func.sum(models.Gasto.valor), 0)).scalar() or Decimal('0')
    
    balance_total = float(total_ingresos) - float(total_gastos)
    
    return schemas.Balance(
        total_ingresos=float(total_ingresos),
        total_gastos=float(total_gastos),
        balance_total=balance_total
    )


@router.get("/por-fechas", response_model=schemas.BalanceRango)
def obtener_balance_por_rango(
    fecha_inicio: date,
    fecha_fin: date,
    db: Session = Depends(get_db)
):
    """
    Obtener balance financiero para un rango de fechas específico
    """
    if fecha_inicio > fecha_fin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de inicio debe ser anterior a la fecha de fin"
        )
    
    # Calcular ingresos en el rango
    total_ingresos = db.query(func.coalesce(func.sum(models.Ingreso.monto), 0)).filter(
        and_(
            models.Ingreso.fecha >= fecha_inicio,
            models.Ingreso.fecha <= fecha_fin
        )
    ).scalar() or Decimal('0')
    
    # Calcular gastos en el rango
    total_gastos = db.query(func.coalesce(func.sum(models.Gasto.valor), 0)).filter(
        and_(
            models.Gasto.fecha >= fecha_inicio,
            models.Gasto.fecha <= fecha_fin
        )
    ).scalar() or Decimal('0')
    
    balance_total = float(total_ingresos) - float(total_gastos)
    
    return schemas.BalanceRango(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        total_ingresos=float(total_ingresos),
        total_gastos=float(total_gastos),
        balance_total=balance_total
    )


@router.get("/ingresos", response_model=List[schemas.Ingreso])
def listar_ingresos(
    skip: int = 0,
    limit: int = 100,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Listar todos los ingresos registrados
    """
    query = db.query(models.Ingreso)
    
    if fecha_inicio:
        query = query.filter(models.Ingreso.fecha >= fecha_inicio)
    
    if fecha_fin:
        query = query.filter(models.Ingreso.fecha <= fecha_fin)
    
    ingresos = query.order_by(models.Ingreso.fecha.desc()).offset(skip).limit(limit).all()
    return ingresos

