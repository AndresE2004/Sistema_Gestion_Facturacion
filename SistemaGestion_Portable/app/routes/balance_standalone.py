"""
Rutas para consultas de balance financiero - Versión para ejecutable standalone (SQLite)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import Optional
from datetime import date, datetime
from app import schemas
from app.models_sqlite import Ingreso, Gasto, Pago, Suscriptor
from app.database_sqlite import get_db
from app.triggers_sqlite import obtener_balance_general, obtener_balance_por_fechas

router = APIRouter(prefix="/balance", tags=["Balance"])


@router.get("/")
def obtener_balance_general_endpoint(db: Session = Depends(get_db)):
    """
    Obtener balance general de todos los ingresos y gastos
    """
    try:
        balance = obtener_balance_general()
        return balance
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculando balance general: {str(e)}"
        )


@router.get("/por-fechas")
def obtener_balance_por_fechas_endpoint(
    fecha_inicio: date,
    fecha_fin: date,
    db: Session = Depends(get_db)
):
    """
    Obtener balance por rango de fechas
    """
    if fecha_inicio > fecha_fin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de inicio no puede ser mayor que la fecha de fin"
        )
    
    try:
        balance = obtener_balance_por_fechas(fecha_inicio, fecha_fin)
        return balance
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculando balance por fechas: {str(e)}"
        )


@router.get("/ingresos")
def listar_ingresos(
    skip: int = 0,
    limit: int = 100,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Listar todos los ingresos con filtros opcionales
    """
    query = db.query(Ingreso)
    
    if fecha_inicio:
        query = query.filter(Ingreso.fecha >= fecha_inicio)
    
    if fecha_fin:
        query = query.filter(Ingreso.fecha <= fecha_fin)
    
    ingresos = query.order_by(Ingreso.fecha.desc()).offset(skip).limit(limit).all()
    
    return [
        {
            "id": ingreso.id,
            "pago_id": ingreso.pago_id,
            "monto": float(ingreso.monto),
            "fecha": ingreso.fecha,
            "origen": ingreso.origen,
            "fecha_creacion": ingreso.fecha_creacion
        }
        for ingreso in ingresos
    ]


@router.get("/detallado")
def obtener_balance_detallado(
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Obtener balance detallado con desglose de ingresos y gastos
    """
    # Query para ingresos
    ingresos_query = db.query(Ingreso)
    if fecha_inicio:
        ingresos_query = ingresos_query.filter(Ingreso.fecha >= fecha_inicio)
    if fecha_fin:
        ingresos_query = ingresos_query.filter(Ingreso.fecha <= fecha_fin)
    
    ingresos = ingresos_query.order_by(Ingreso.fecha.desc()).all()
    
    # Query para gastos
    gastos_query = db.query(Gasto)
    if fecha_inicio:
        gastos_query = gastos_query.filter(Gasto.fecha >= fecha_inicio)
    if fecha_fin:
        gastos_query = gastos_query.filter(Gasto.fecha <= fecha_fin)
    
    gastos = gastos_query.order_by(Gasto.fecha.desc()).all()
    
    # Calcular totales
    total_ingresos = sum(float(ing.monto) for ing in ingresos)
    total_gastos = sum(float(gas.valor) for gas in gastos)
    balance_total = total_ingresos - total_gastos
    
    return {
        "resumen": {
            "total_ingresos": total_ingresos,
            "total_gastos": total_gastos,
            "balance_total": balance_total,
            "cantidad_ingresos": len(ingresos),
            "cantidad_gastos": len(gastos)
        },
        "ingresos": [
            {
                "id": ing.id,
                "monto": float(ing.monto),
                "fecha": ing.fecha,
                "origen": ing.origen
            }
            for ing in ingresos
        ],
        "gastos": [
            {
                "id": gas.id,
                "tipo_gasto": gas.tipo_gasto,
                "descripcion": gas.descripcion,
                "valor": float(gas.valor),
                "fecha": gas.fecha,
                "lugar_compra": gas.lugar_compra,
                "motivo": gas.motivo
            }
            for gas in gastos
        ]
    }


@router.get("/mensual")
def obtener_balance_mensual(
    anio: int,
    db: Session = Depends(get_db)
):
    """
    Obtener balance mensual para un año específico
    """
    from sqlalchemy import extract
    
    # Ingresos mensuales
    ingresos_mensuales = db.query(
        extract('month', Ingreso.fecha).label('mes'),
        func.sum(Ingreso.monto).label('total')
    ).filter(
        extract('year', Ingreso.fecha) == anio
    ).group_by(
        extract('month', Ingreso.fecha)
    ).all()
    
    # Gastos mensuales
    gastos_mensuales = db.query(
        extract('month', Gasto.fecha).label('mes'),
        func.sum(Gasto.valor).label('total')
    ).filter(
        extract('year', Gasto.fecha) == anio
    ).group_by(
        extract('month', Gasto.fecha)
    ).all()
    
    # Combinar resultados
    balance_mensual = []
    for mes in range(1, 13):
        ingresos_mes = next((float(item.total) for item in ingresos_mensuales if int(item.mes) == mes), 0.0)
        gastos_mes = next((float(item.total) for item in gastos_mensuales if int(item.mes) == mes), 0.0)
        balance_mes = ingresos_mes - gastos_mes
        
        balance_mensual.append({
            "mes": mes,
            "ingresos": ingresos_mes,
            "gastos": gastos_mes,
            "balance": balance_mes
        })
    
    return balance_mensual


@router.get("/suscriptores-activos")
def obtener_balance_suscriptores_activos(
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Obtener balance por suscriptores activos en un período
    """
    # Query base para pagos en el período
    pagos_query = db.query(Pago).join(Suscriptor)
    if fecha_inicio:
        pagos_query = pagos_query.filter(Pago.fecha_pago >= fecha_inicio)
    if fecha_fin:
        pagos_query = pagos_query.filter(Pago.fecha_pago <= fecha_fin)
    
    pagos = pagos_query.order_by(Suscriptor.nombre_completo).all()
    
    # Agrupar por suscriptor
    suscriptores_balance = {}
    for pago in pagos:
        if pago.suscriptor_id not in suscriptores_balance:
            suscriptores_balance[pago.suscriptor_id] = {
                "suscriptor_id": pago.suscriptor_id,
                "nombre_completo": pago.suscriptor.nombre_completo,
                "numero_contrato": pago.suscriptor.numero_contrato,
                "total_pagado": 0.0,
                "cantidad_pagos": 0,
                "pagos": []
            }
        
        suscriptores_balance[pago.suscriptor_id]["total_pagado"] += float(pago.valor)
        suscriptores_balance[pago.suscriptor_id]["cantidad_pagos"] += 1
        suscriptores_balance[pago.suscriptor_id]["pagos"].append({
            "id": pago.id,
            "mes": pago.mes,
            "anio": pago.anio,
            "fecha_pago": pago.fecha_pago,
            "valor": float(pago.valor),
            "tipo_pago": pago.tipo_pago
        })
    
    return list(suscriptores_balance.values())
