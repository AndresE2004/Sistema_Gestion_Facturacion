"""
Triggers y funciones automáticas para SQLite (adaptados de PostgreSQL)
"""
from datetime import datetime
from sqlalchemy import text
from .database_sqlite import engine


def generar_numero_recibo():
    """
    Generar número de recibo automático para SQLite
    Formato: REC-YYYYMMDD-XXXXX
    """
    connection = engine.connect()
    
    # Obtener fecha actual
    fecha_str = datetime.now().strftime("%Y%m%d")
    
    # Contar recibos del día
    result = connection.execute(text("""
        SELECT COUNT(*) as contador 
        FROM recibos 
        WHERE numero_recibo LIKE :fecha_prefix
    """), {"fecha_prefix": f"REC-{fecha_str}-%"})
    
    contador = result.fetchone()[0] + 1
    
    # Generar número
    numero_recibo = f"REC-{fecha_str}-{contador:05d}"
    
    connection.close()
    return numero_recibo


def crear_recibo_y_ingreso_despues_pago(pago_id, suscriptor_nombre, valor, fecha_pago):
    """
    Crear recibo e ingreso automáticamente después de registrar un pago
    """
    connection = engine.connect()
    
    try:
        # Generar número de recibo
        numero_recibo = generar_numero_recibo()
        
        # Crear recibo
        connection.execute(text("""
            INSERT INTO recibos (pago_id, numero_recibo, fecha_emision)
            VALUES (:pago_id, :numero_recibo, :fecha_emision)
        """), {
            "pago_id": pago_id,
            "numero_recibo": numero_recibo,
            "fecha_emision": datetime.utcnow()
        })
        
        # Crear ingreso
        origen = f"Pago de suscriptor: {suscriptor_nombre}"
        connection.execute(text("""
            INSERT INTO ingresos (pago_id, monto, fecha, origen, fecha_creacion)
            VALUES (:pago_id, :monto, :fecha, :origen, :fecha_creacion)
        """), {
            "pago_id": pago_id,
            "monto": valor,
            "fecha": fecha_pago,
            "origen": origen,
            "fecha_creacion": datetime.utcnow()
        })
        
        connection.commit()
        
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        connection.close()


def obtener_balance_general():
    """
    Obtener balance general para SQLite
    """
    connection = engine.connect()
    
    result = connection.execute(text("""
        SELECT 
            COALESCE(SUM(ingresos.monto), 0) as total_ingresos,
            COALESCE(SUM(gastos.valor), 0) as total_gastos,
            COALESCE(SUM(ingresos.monto), 0) - COALESCE(SUM(gastos.valor), 0) as balance_total
        FROM ingresos
        CROSS JOIN gastos
    """))
    
    balance = result.fetchone()
    connection.close()
    
    return {
        "total_ingresos": float(balance[0]),
        "total_gastos": float(balance[1]),
        "balance_total": float(balance[2])
    }


def obtener_balance_por_fechas(fecha_inicio, fecha_fin):
    """
    Obtener balance por rango de fechas para SQLite
    """
    connection = engine.connect()
    
    result = connection.execute(text("""
        SELECT 
            COALESCE(SUM(CASE WHEN ingresos.fecha BETWEEN :fecha_inicio AND :fecha_fin 
                           THEN ingresos.monto ELSE 0 END), 0) as total_ingresos,
            COALESCE(SUM(CASE WHEN gastos.fecha BETWEEN :fecha_inicio AND :fecha_fin 
                           THEN gastos.valor ELSE 0 END), 0) as total_gastos,
            COALESCE(SUM(CASE WHEN ingresos.fecha BETWEEN :fecha_inicio AND :fecha_fin 
                           THEN ingresos.monto ELSE 0 END), 0) - 
            COALESCE(SUM(CASE WHEN gastos.fecha BETWEEN :fecha_inicio AND :fecha_fin 
                           THEN gastos.valor ELSE 0 END), 0) as balance_total
        FROM ingresos
        CROSS JOIN gastos
    """), {
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin
    })
    
    balance = result.fetchone()
    connection.close()
    
    return {
        "total_ingresos": float(balance[0]),
        "total_gastos": float(balance[1]),
        "balance_total": float(balance[2])
    }
