"""
Rutas para gestión de pagos - Versión para ejecutable standalone (SQLite)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import date
from app import schemas
from app.models_sqlite import Suscriptor, Pago, Recibo, Ingreso
from app.database_sqlite import get_db
from app.triggers_sqlite import crear_recibo_y_ingreso_despues_pago

router = APIRouter(prefix="/pagos", tags=["Pagos"])


@router.post("/", response_model=schemas.Pago, status_code=status.HTTP_201_CREATED)
def crear_pago(pago: schemas.PagoCreate, db: Session = Depends(get_db)):
    """
    Registrar un nuevo pago de suscriptor
    Genera automáticamente el recibo y el ingreso correspondiente
    """
    # Verificar que el suscriptor existe
    suscriptor = db.query(Suscriptor).filter(Suscriptor.id == pago.suscriptor_id).first()
    if not suscriptor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suscriptor no encontrado"
        )
    
    # Verificar que no exista un pago para el mismo mes/año del mismo suscriptor
    pago_existente = db.query(Pago).filter(
        and_(
            Pago.suscriptor_id == pago.suscriptor_id,
            Pago.mes == pago.mes,
            Pago.anio == pago.anio
        )
    ).first()
    
    if pago_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un pago para este suscriptor en {pago.mes}/{pago.anio}"
        )
    
    # Crear el pago
    pago_data = pago.dict()
    db_pago = Pago(**pago_data)
    db.add(db_pago)
    db.commit()
    db.refresh(db_pago)
    
    # Crear recibo e ingreso automáticamente (versión SQLite)
    try:
        crear_recibo_y_ingreso_despues_pago(
            pago_id=db_pago.id,
            suscriptor_nombre=suscriptor.nombre_completo,
            valor=float(db_pago.valor),
            fecha_pago=db_pago.fecha_pago
        )
    except Exception as e:
        # Si hay error creando recibo/ingreso, eliminar el pago
        db.delete(db_pago)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando recibo e ingreso: {str(e)}"
        )
    
    return db_pago


@router.get("/", response_model=List[schemas.Pago])
def listar_pagos(
    skip: int = 0,
    limit: int = 100,
    suscriptor_id: Optional[int] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Listar pagos con filtros opcionales
    """
    query = db.query(Pago)
    
    if suscriptor_id:
        query = query.filter(Pago.suscriptor_id == suscriptor_id)
    
    if fecha_inicio:
        query = query.filter(Pago.fecha_pago >= fecha_inicio)
    
    if fecha_fin:
        query = query.filter(Pago.fecha_pago <= fecha_fin)
    
    pagos = query.order_by(Pago.fecha_pago.desc()).offset(skip).limit(limit).all()
    return pagos


@router.get("/{pago_id}", response_model=schemas.Pago)
def obtener_pago(pago_id: int, db: Session = Depends(get_db)):
    """
    Obtener un pago por ID
    """
    pago = db.query(Pago).filter(Pago.id == pago_id).first()
    if not pago:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pago no encontrado"
        )
    return pago


@router.get("/suscriptor/{suscriptor_id}", response_model=List[schemas.Pago])
def listar_pagos_por_suscriptor(suscriptor_id: int, db: Session = Depends(get_db)):
    """
    Listar todos los pagos de un suscriptor específico
    """
    # Verificar que el suscriptor existe
    suscriptor = db.query(Suscriptor).filter(Suscriptor.id == suscriptor_id).first()
    if not suscriptor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suscriptor no encontrado"
        )
    
    pagos = db.query(Pago).filter(
        Pago.suscriptor_id == suscriptor_id
    ).order_by(Pago.anio.desc(), Pago.mes.desc()).all()
    
    return pagos


@router.delete("/{pago_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_pago(pago_id: int, db: Session = Depends(get_db)):
    """
    Eliminar un pago (también elimina el recibo e ingreso relacionados)
    """
    pago = db.query(Pago).filter(Pago.id == pago_id).first()
    if not pago:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pago no encontrado"
        )
    
    db.delete(pago)
    db.commit()
    return None
