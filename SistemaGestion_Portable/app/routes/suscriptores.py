"""
Rutas para gestión de suscriptores
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import schemas, models
from app.database import get_db

router = APIRouter(prefix="/suscriptores", tags=["Suscriptores"])


@router.post("/", response_model=schemas.Suscriptor, status_code=status.HTTP_201_CREATED)
def crear_suscriptor(suscriptor: schemas.SuscriptorCreate, db: Session = Depends(get_db)):
    """
    Crear un nuevo suscriptor/contrato
    """
    # Verificar que el número de contrato no exista
    if db.query(models.Suscriptor).filter(models.Suscriptor.numero_contrato == suscriptor.numero_contrato).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un suscriptor con este número de contrato"
        )
    
    # Verificar que la cédula no exista
    if db.query(models.Suscriptor).filter(models.Suscriptor.cedula == suscriptor.cedula).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un suscriptor con esta cédula"
        )
    
    db_suscriptor = models.Suscriptor(**suscriptor.dict())
    db.add(db_suscriptor)
    db.commit()
    db.refresh(db_suscriptor)
    return db_suscriptor


@router.get("/", response_model=List[schemas.Suscriptor])
def listar_suscriptores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Listar todos los suscriptores
    """
    suscriptores = db.query(models.Suscriptor).offset(skip).limit(limit).all()
    return suscriptores


@router.get("/{suscriptor_id}", response_model=schemas.Suscriptor)
def obtener_suscriptor(suscriptor_id: int, db: Session = Depends(get_db)):
    """
    Obtener un suscriptor por ID
    """
    suscriptor = db.query(models.Suscriptor).filter(models.Suscriptor.id == suscriptor_id).first()
    if not suscriptor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suscriptor no encontrado"
        )
    return suscriptor


@router.get("/por-contrato/{numero_contrato}", response_model=schemas.Suscriptor)
def obtener_suscriptor_por_contrato(numero_contrato: str, db: Session = Depends(get_db)):
    """
    Obtener un suscriptor por número de contrato
    """
    suscriptor = db.query(models.Suscriptor).filter(models.Suscriptor.numero_contrato == numero_contrato).first()
    if not suscriptor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suscriptor no encontrado"
        )
    return suscriptor


@router.put("/{suscriptor_id}", response_model=schemas.Suscriptor)
def actualizar_suscriptor(
    suscriptor_id: int,
    suscriptor_update: schemas.SuscriptorUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar información de un suscriptor
    """
    suscriptor = db.query(models.Suscriptor).filter(models.Suscriptor.id == suscriptor_id).first()
    if not suscriptor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suscriptor no encontrado"
        )
    
    # Verificar unicidad si se actualiza número de contrato o cédula
    update_data = suscriptor_update.dict(exclude_unset=True)
    
    if "numero_contrato" in update_data:
        if db.query(models.Suscriptor).filter(
            models.Suscriptor.numero_contrato == update_data["numero_contrato"],
            models.Suscriptor.id != suscriptor_id
        ).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe otro suscriptor con este número de contrato"
            )
    
    if "cedula" in update_data:
        if db.query(models.Suscriptor).filter(
            models.Suscriptor.cedula == update_data["cedula"],
            models.Suscriptor.id != suscriptor_id
        ).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe otro suscriptor con esta cédula"
            )
    
    for field, value in update_data.items():
        setattr(suscriptor, field, value)
    
    db.commit()
    db.refresh(suscriptor)
    return suscriptor


@router.delete("/{suscriptor_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_suscriptor(suscriptor_id: int, db: Session = Depends(get_db)):
    """
    Eliminar un suscriptor (también elimina sus pagos relacionados)
    """
    suscriptor = db.query(models.Suscriptor).filter(models.Suscriptor.id == suscriptor_id).first()
    if not suscriptor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suscriptor no encontrado"
        )
    
    db.delete(suscriptor)
    db.commit()
    return None

