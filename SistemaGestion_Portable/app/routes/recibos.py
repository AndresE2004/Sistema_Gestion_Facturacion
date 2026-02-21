"""
Rutas para gestión de recibos
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import schemas, models
from app.database import get_db

router = APIRouter(prefix="/recibos", tags=["Recibos"])


@router.get("/", response_model=List[schemas.Recibo])
def listar_recibos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Listar todos los recibos generados
    """
    recibos = db.query(models.Recibo).order_by(models.Recibo.fecha_emision.desc()).offset(skip).limit(limit).all()
    return recibos


@router.get("/{recibo_id}", response_model=schemas.Recibo)
def obtener_recibo(recibo_id: int, db: Session = Depends(get_db)):
    """
    Obtener un recibo por ID
    """
    recibo = db.query(models.Recibo).filter(models.Recibo.id == recibo_id).first()
    if not recibo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recibo no encontrado"
        )
    return recibo


@router.get("/por-pago/{pago_id}", response_model=schemas.Recibo)
def obtener_recibo_por_pago(pago_id: int, db: Session = Depends(get_db)):
    """
    Obtener el recibo asociado a un pago específico
    """
    recibo = db.query(models.Recibo).filter(models.Recibo.pago_id == pago_id).first()
    if not recibo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró recibo para este pago"
        )
    return recibo


@router.get("/por-numero/{numero_recibo}", response_model=schemas.Recibo)
def obtener_recibo_por_numero(numero_recibo: str, db: Session = Depends(get_db)):
    """
    Obtener un recibo por número de recibo
    """
    recibo = db.query(models.Recibo).filter(models.Recibo.numero_recibo == numero_recibo).first()
    if not recibo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recibo no encontrado"
        )
    return recibo

