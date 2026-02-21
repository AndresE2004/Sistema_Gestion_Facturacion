"""
Rutas para gestión de suscriptores - Versión para ejecutable standalone (SQLite)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from app import schemas
from app.models_sqlite import Suscriptor, Pago
from app.database_sqlite import get_db

router = APIRouter(prefix="/suscriptores", tags=["Suscriptores"])


@router.post("/", response_model=schemas.Suscriptor, status_code=status.HTTP_201_CREATED)
def crear_suscriptor(suscriptor: schemas.SuscriptorCreate, db: Session = Depends(get_db)):
    """
    Crear un nuevo suscriptor
    """
    # Verificar que no exista el mismo número de contrato
    existente_contrato = db.query(Suscriptor).filter(
        Suscriptor.numero_contrato == suscriptor.numero_contrato
    ).first()
    
    if existente_contrato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un suscriptor con este número de contrato"
        )
    
    # Verificar que no exista la misma cédula
    existente_cedula = db.query(Suscriptor).filter(
        Suscriptor.cedula == suscriptor.cedula
    ).first()
    
    if existente_cedula:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un suscriptor con esta cédula"
        )
    
    # Crear suscriptor
    db_suscriptor = Suscriptor(**suscriptor.dict())
    db.add(db_suscriptor)
    db.commit()
    db.refresh(db_suscriptor)
    
    return db_suscriptor


@router.get("/", response_model=List[schemas.Suscriptor])
def listar_suscriptores(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Listar todos los suscriptores
    """
    suscriptores = db.query(Suscriptor).offset(skip).limit(limit).all()
    return suscriptores


@router.get("/{suscriptor_id}", response_model=schemas.Suscriptor)
def obtener_suscriptor(suscriptor_id: int, db: Session = Depends(get_db)):
    """
    Obtener un suscriptor por ID
    """
    suscriptor = db.query(Suscriptor).filter(Suscriptor.id == suscriptor_id).first()
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
    suscriptor = db.query(Suscriptor).filter(
        Suscriptor.numero_contrato == numero_contrato
    ).first()
    
    if not suscriptor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suscriptor no encontrado con ese número de contrato"
        )
    return suscriptor


@router.get("/por-cedula/{cedula}", response_model=schemas.Suscriptor)
def obtener_suscriptor_por_cedula(cedula: str, db: Session = Depends(get_db)):
    """
    Obtener un suscriptor por cédula
    """
    suscriptor = db.query(Suscriptor).filter(
        Suscriptor.cedula == cedula
    ).first()
    
    if not suscriptor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suscriptor no encontrado con esa cédula"
        )
    return suscriptor


@router.put("/{suscriptor_id}", response_model=schemas.Suscriptor)
def actualizar_suscriptor(
    suscriptor_id: int, 
    suscriptor_update: schemas.SuscriptorUpdate, 
    db: Session = Depends(get_db)
):
    """
    Actualizar un suscriptor
    """
    suscriptor = db.query(Suscriptor).filter(Suscriptor.id == suscriptor_id).first()
    if not suscriptor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suscriptor no encontrado"
        )
    
    # Verificar que no exista otro suscriptor con el mismo contrato
    if suscriptor_update.numero_contrato:
        existente = db.query(Suscriptor).filter(
            and_(
                Suscriptor.numero_contrato == suscriptor_update.numero_contrato,
                Suscriptor.id != suscriptor_id
            )
        ).first()
        
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe otro suscriptor con este número de contrato"
            )
    
    # Verificar que no exista otro suscriptor con la misma cédula
    if suscriptor_update.cedula:
        existente = db.query(Suscriptor).filter(
            and_(
                Suscriptor.cedula == suscriptor_update.cedula,
                Suscriptor.id != suscriptor_id
            )
        ).first()
        
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe otro suscriptor con esta cédula"
            )
    
    # Actualizar campos
    update_data = suscriptor_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(suscriptor, field, value)
    
    db.commit()
    db.refresh(suscriptor)
    
    return suscriptor


@router.delete("/{suscriptor_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_suscriptor(suscriptor_id: int, db: Session = Depends(get_db)):
    """
    Eliminar un suscriptor (también elimina todos sus pagos relacionados)
    """
    suscriptor = db.query(Suscriptor).filter(Suscriptor.id == suscriptor_id).first()
    if not suscriptor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suscriptor no encontrado"
        )
    
    db.delete(suscriptor)
    db.commit()
    return None


@router.get("/buscar/{termino}", response_model=List[schemas.Suscriptor])
def buscar_suscriptores(termino: str, db: Session = Depends(get_db)):
    """
    Buscar suscriptores por nombre, contrato o cédula
    """
    busqueda = f"%{termino}%"
    suscriptores = db.query(Suscriptor).filter(
        or_(
            Suscriptor.nombre_completo.ilike(busqueda),
            Suscriptor.numero_contrato.ilike(busqueda),
            Suscriptor.cedula.ilike(busqueda)
        )
    ).limit(50).all()
    
    return suscriptores
