"""
Rutas para gestión de recibos - Versión para ejecutable standalone (SQLite)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schemas
from app.models_sqlite import Recibo, Pago, Suscriptor
from app.database_sqlite import get_db

router = APIRouter(prefix="/recibos", tags=["Recibos"])


@router.get("/", response_model=List[schemas.Recibo])
def listar_recibos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Listar todos los recibos
    """
    recibos = db.query(Recibo).order_by(Recibo.fecha_emision.desc()).offset(skip).limit(limit).all()
    return recibos


@router.get("/{recibo_id}", response_model=schemas.Recibo)
def obtener_recibo(recibo_id: int, db: Session = Depends(get_db)):
    """
    Obtener un recibo por ID
    """
    recibo = db.query(Recibo).filter(Recibo.id == recibo_id).first()
    if not recibo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recibo no encontrado"
        )
    return recibo


@router.get("/por-pago/{pago_id}", response_model=schemas.Recibo)
def obtener_recibo_por_pago(pago_id: int, db: Session = Depends(get_db)):
    """
    Obtener el recibo de un pago específico
    """
    # Verificar que el pago existe
    pago = db.query(Pago).filter(Pago.id == pago_id).first()
    if not pago:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pago no encontrado"
        )
    
    recibo = db.query(Recibo).filter(Recibo.pago_id == pago_id).first()
    if not recibo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recibo no encontrado para este pago"
        )
    
    return recibo


@router.get("/por-numero/{numero_recibo}", response_model=schemas.Recibo)
def obtener_recibo_por_numero(numero_recibo: str, db: Session = Depends(get_db)):
    """
    Obtener un recibo por número de recibo
    """
    recibo = db.query(Recibo).filter(Recibo.numero_recibo == numero_recibo).first()
    if not recibo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recibo no encontrado con ese número"
        )
    return recibo


@router.get("/suscriptor/{suscriptor_id}", response_model=List[schemas.Recibo])
def listar_recibos_por_suscriptor(suscriptor_id: int, db: Session = Depends(get_db)):
    """
    Listar todos los recibos de un suscriptor específico
    """
    # Verificar que el suscriptor existe
    suscriptor = db.query(Suscriptor).filter(Suscriptor.id == suscriptor_id).first()
    if not suscriptor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suscriptor no encontrado"
        )
    
    recibos = db.query(Recibo).join(Pago).filter(
        Pago.suscriptor_id == suscriptor_id
    ).order_by(Recibo.fecha_emision.desc()).all()
    
    return recibos


@router.get("/detalle/{recibo_id}")
def obtener_detalle_recibo(recibo_id: int, db: Session = Depends(get_db)):
    """
    Obtener detalle completo del recibo con información del pago y suscriptor
    """
    recibo = db.query(Recibo).filter(Recibo.id == recibo_id).first()
    if not recibo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recibo no encontrado"
        )
    
    # Obtener información del pago
    pago = db.query(Pago).filter(Pago.id == recibo.pago_id).first()
    if not pago:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pago asociado no encontrado"
        )
    
    # Obtener información del suscriptor
    suscriptor = db.query(Suscriptor).filter(Suscriptor.id == pago.suscriptor_id).first()
    if not suscriptor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suscriptor asociado no encontrado"
        )
    
    return {
        "recibo": {
            "id": recibo.id,
            "numero_recibo": recibo.numero_recibo,
            "fecha_emision": recibo.fecha_emision
        },
        "pago": {
            "id": pago.id,
            "mes": pago.mes,
            "anio": pago.anio,
            "fecha_pago": pago.fecha_pago,
            "valor": pago.valor,
            "tipo_pago": pago.tipo_pago,
            "entidad_bancaria": pago.entidad_bancaria,
            "nombre_transferente": pago.nombre_transferente,
            "monto_efectivo": pago.monto_efectivo
        },
        "suscriptor": {
            "id": suscriptor.id,
            "numero_contrato": suscriptor.numero_contrato,
            "cedula": suscriptor.cedula,
            "nombre_completo": suscriptor.nombre_completo,
            "fecha_suscripcion": suscriptor.fecha_suscripcion
        }
    }
