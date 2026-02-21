"""
Rutas para gestión de gastos
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app import schemas, models
from app.database import get_db

router = APIRouter(prefix="/gastos", tags=["Gastos"])


@router.post("/", response_model=schemas.Gasto, status_code=status.HTTP_201_CREATED)
def crear_gasto(gasto: schemas.GastoCreate, db: Session = Depends(get_db)):
    """
    Registrar un nuevo gasto
    """
    db_gasto = models.Gasto(**gasto.dict())
    db.add(db_gasto)
    db.commit()
    db.refresh(db_gasto)
    return db_gasto


@router.get("/", response_model=List[schemas.Gasto])
def listar_gastos(
    skip: int = 0,
    limit: int = 100,
    tipo_gasto: Optional[str] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Listar gastos con filtros opcionales
    """
    query = db.query(models.Gasto)
    
    if tipo_gasto:
        query = query.filter(models.Gasto.tipo_gasto == tipo_gasto)
    
    if fecha_inicio:
        query = query.filter(models.Gasto.fecha >= fecha_inicio)
    
    if fecha_fin:
        query = query.filter(models.Gasto.fecha <= fecha_fin)
    
    gastos = query.order_by(models.Gasto.fecha.desc()).offset(skip).limit(limit).all()
    return gastos


@router.get("/{gasto_id}", response_model=schemas.Gasto)
def obtener_gasto(gasto_id: int, db: Session = Depends(get_db)):
    """
    Obtener un gasto por ID
    """
    gasto = db.query(models.Gasto).filter(models.Gasto.id == gasto_id).first()
    if not gasto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gasto no encontrado"
        )
    return gasto


@router.put("/{gasto_id}", response_model=schemas.Gasto)
def actualizar_gasto(
    gasto_id: int,
    gasto_update: schemas.GastoUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar un gasto
    """
    gasto = db.query(models.Gasto).filter(models.Gasto.id == gasto_id).first()
    if not gasto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gasto no encontrado"
        )
    
    update_data = gasto_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(gasto, field, value)
    
    db.commit()
    db.refresh(gasto)
    return gasto


@router.delete("/{gasto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_gasto(gasto_id: int, db: Session = Depends(get_db)):
    """
    Eliminar un gasto
    """
    gasto = db.query(models.Gasto).filter(models.Gasto.id == gasto_id).first()
    if not gasto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gasto no encontrado"
        )
    
    db.delete(gasto)
    db.commit()
    return None

