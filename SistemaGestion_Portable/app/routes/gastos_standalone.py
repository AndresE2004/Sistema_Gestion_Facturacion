"""
Rutas para gestión de gastos - Versión para ejecutable standalone (SQLite)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import date
from app import schemas
from app.models_sqlite import Gasto
from app.database_sqlite import get_db

router = APIRouter(prefix="/gastos", tags=["Gastos"])


@router.post("/", response_model=schemas.Gasto, status_code=status.HTTP_201_CREATED)
def crear_gasto(gasto: schemas.GastoCreate, db: Session = Depends(get_db)):
    """
    Registrar un nuevo gasto
    """
    # Crear gasto
    db_gasto = Gasto(**gasto.dict())
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
    query = db.query(Gasto)
    
    if tipo_gasto:
        query = query.filter(Gasto.tipo_gasto == tipo_gasto)
    
    if fecha_inicio:
        query = query.filter(Gasto.fecha >= fecha_inicio)
    
    if fecha_fin:
        query = query.filter(Gasto.fecha <= fecha_fin)
    
    gastos = query.order_by(Gasto.fecha.desc()).offset(skip).limit(limit).all()
    return gastos


@router.get("/{gasto_id}", response_model=schemas.Gasto)
def obtener_gasto(gasto_id: int, db: Session = Depends(get_db)):
    """
    Obtener un gasto por ID
    """
    gasto = db.query(Gasto).filter(Gasto.id == gasto_id).first()
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
    gasto = db.query(Gasto).filter(Gasto.id == gasto_id).first()
    if not gasto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gasto no encontrado"
        )
    
    # Actualizar campos
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
    gasto = db.query(Gasto).filter(Gasto.id == gasto_id).first()
    if not gasto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gasto no encontrado"
        )
    
    db.delete(gasto)
    db.commit()
    return None


@router.get("/tipos/", response_model=List[str])
def listar_tipos_gastos(db: Session = Depends(get_db)):
    """
    Listar todos los tipos de gastos únicos
    """
    tipos = db.query(Gasto.tipo_gasto).distinct().all()
    return [tipo[0] for tipo in tipos]


@router.get("/resumen/mensual")
def resumen_gastos_mensuales(
    anio: int,
    db: Session = Depends(get_db)
):
    """
    Obtener resumen de gastos mensuales para un año específico
    """
    from sqlalchemy import func, extract
    
    resumen = db.query(
        extract('month', Gasto.fecha).label('mes'),
        func.sum(Gasto.valor).label('total'),
        func.count(Gasto.id).label('cantidad')
    ).filter(
        extract('year', Gasto.fecha) == anio
    ).group_by(
        extract('month', Gasto.fecha)
    ).order_by(
        extract('month', Gasto.fecha)
    ).all()
    
    return [
        {
            "mes": int(item.mes),
            "total": float(item.total),
            "cantidad": item.cantidad
        }
        for item in resumen
    ]


@router.get("/buscar/{termino}", response_model=List[schemas.Gasto])
def buscar_gastos(termino: str, db: Session = Depends(get_db)):
    """
    Buscar gastos por descripción, lugar o motivo
    """
    busqueda = f"%{termino}%"
    gastos = db.query(Gasto).filter(
        or_(
            Gasto.descripcion.ilike(busqueda),
            Gasto.lugar_compra.ilike(busqueda),
            Gasto.motivo.ilike(busqueda)
        )
    ).limit(50).all()
    
    return gastos
