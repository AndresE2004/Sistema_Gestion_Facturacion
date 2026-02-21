"""
Aplicación principal FastAPI - Versión Simple sin SQLAlchemy
Sistema de Gestión de Suscriptores y Finanzas
"""
import os
import sys
import webbrowser
import sqlite3
from datetime import datetime, date
from typing import List, Optional
from pathlib import Path
from fastapi.staticfiles import StaticFiles

# Configurar paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURRENT_DIR)

# Servir interfaz estática en /ui
static_dir = os.path.join(CURRENT_DIR, "static")
if os.path.exists(static_dir):
    app = FastAPI()
    app.mount("/ui", StaticFiles(directory=static_dir, html=True), name="static")
else:
    # Importar FastAPI
    from fastapi import FastAPI, HTTPException, status
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import RedirectResponse, JSONResponse
    from pydantic import BaseModel
    from database_simple import init_database, get_database_path, crear_recibo_y_ingreso, get_connection
from pydantic import BaseModel
from database_simple import init_database, get_database_path, crear_recibo_y_ingreso, get_connection

# Modelos Pydantic
class SuscriptorCreate(BaseModel):
    numero_contrato: str
    cedula: str
    nombre_completo: str
    fecha_suscripcion: date

class SuscriptorResponse(BaseModel):
    id: int
    numero_contrato: str
    cedula: str
    nombre_completo: str
    fecha_suscripcion: date
    fecha_creacion: datetime
    fecha_actualizacion: datetime

class PagoCreate(BaseModel):
    suscriptor_id: int
    mes: int
    anio: int
    fecha_pago: date
    valor: float
    tipo_pago: str
    entidad_bancaria: Optional[str] = None
    nombre_transferente: Optional[str] = None
    monto_efectivo: Optional[float] = None

class PagoResponse(BaseModel):
    id: int
    suscriptor_id: int
    mes: int
    anio: int
    fecha_pago: date
    valor: float
    tipo_pago: str
    entidad_bancaria: Optional[str]
    nombre_transferente: Optional[str]
    monto_efectivo: Optional[float]
    fecha_creacion: datetime

class GastoCreate(BaseModel):
    tipo_gasto: str
    descripcion: str
    valor: float
    fecha: date
    lugar_compra: Optional[str] = None
    motivo: Optional[str] = None

class GastoResponse(BaseModel):
    id: int
    tipo_gasto: str
    descripcion: str
    valor: float
    fecha: date
    lugar_compra: Optional[str]
    motivo: Optional[str]
    fecha_creacion: datetime

# Crear aplicación FastAPI
app = FastAPI(
    title="Sistema de Gestión de Suscriptores y Finanzas",
    description="Software libre para gestión de suscriptores, pagos mensuales, ingresos y gastos",
    version="1.0.0 - Simple",
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint raíz
@app.get("/")
def root():
    return RedirectResponse(url="/ui")

@app.get("/health")
def health_check():
    return {"status": "ok", "mensaje": "Sistema operativo"}

# Endpoints de Suscriptores
@app.post("/suscriptores/", response_model=SuscriptorResponse, status_code=status.HTTP_201_CREATED)
def crear_suscriptor(suscriptor: SuscriptorCreate):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar duplicados
        cursor.execute('SELECT id FROM suscriptores WHERE numero_contrato = ?', (suscriptor.numero_contrato,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Ya existe un suscriptor con este número de contrato")
        
        cursor.execute('SELECT id FROM suscriptores WHERE cedula = ?', (suscriptor.cedula,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Ya existe un suscriptor con esta cédula")
        
        # Crear suscriptor
        cursor.execute('''
            INSERT INTO suscriptores (numero_contrato, cedula, nombre_completo, fecha_suscripcion)
            VALUES (?, ?, ?, ?)
        ''', (suscriptor.numero_contrato, suscriptor.cedula, suscriptor.nombre_completo, suscriptor.fecha_suscripcion))
        
        suscriptor_id = cursor.lastrowid
        conn.commit()
        
        # Obtener suscriptor creado
        cursor.execute('SELECT * FROM suscriptores WHERE id = ?', (suscriptor_id,))
        result = cursor.fetchone()
        
        return dict(result)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/suscriptores/", response_model=List[SuscriptorResponse])
def listar_suscriptores(skip: int = 0, limit: int = 100):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM suscriptores ORDER BY fecha_creacion DESC LIMIT ? OFFSET ?', (limit, skip))
    results = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in results]

@app.get("/suscriptores/{suscriptor_id}", response_model=SuscriptorResponse)
def obtener_suscriptor(suscriptor_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM suscriptores WHERE id = ?', (suscriptor_id,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        raise HTTPException(status_code=404, detail="Suscriptor no encontrado")
    
    return dict(result)

# Endpoints de Pagos
@app.post("/pagos/", response_model=PagoResponse, status_code=status.HTTP_201_CREATED)
def crear_pago(pago: PagoCreate):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar suscriptor
        cursor.execute('SELECT nombre_completo FROM suscriptores WHERE id = ?', (pago.suscriptor_id,))
        suscriptor = cursor.fetchone()
        if not suscriptor:
            raise HTTPException(status_code=404, detail="Suscriptor no encontrado")
        
        # Verificar duplicado
        cursor.execute('''
            SELECT id FROM pagos 
            WHERE suscriptor_id = ? AND mes = ? AND anio = ?
        ''', (pago.suscriptor_id, pago.mes, pago.anio))
        
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail=f"Ya existe un pago para este suscriptor en {pago.mes}/{pago.anio}")
        
        # Crear pago
        cursor.execute('''
            INSERT INTO pagos (suscriptor_id, mes, anio, fecha_pago, valor, tipo_pago, entidad_bancaria, nombre_transferente, monto_efectivo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (pago.suscriptor_id, pago.mes, pago.anio, pago.fecha_pago, pago.valor, pago.tipo_pago, 
               pago.entidad_bancaria, pago.nombre_transferente, pago.monto_efectivo))
        
        pago_id = cursor.lastrowid
        conn.commit()
        
        # Crear recibo e ingreso automáticamente
        crear_recibo_y_ingreso(pago_id, suscriptor['nombre_completo'], pago.valor, pago.fecha_pago)
        
        # Obtener pago creado
        cursor.execute('SELECT * FROM pagos WHERE id = ?', (pago_id,))
        result = cursor.fetchone()
        
        return dict(result)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/pagos/", response_model=List[PagoResponse])
def listar_pagos(skip: int = 0, limit: int = 100):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM pagos ORDER BY fecha_pago DESC LIMIT ? OFFSET ?', (limit, skip))
    results = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in results]

# Endpoints de Gastos
@app.post("/gastos/", response_model=GastoResponse, status_code=status.HTTP_201_CREATED)
def crear_gasto(gasto: GastoCreate):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO gastos (tipo_gasto, descripcion, valor, fecha, lugar_compra, motivo)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (gasto.tipo_gasto, gasto.descripcion, gasto.valor, gasto.fecha, gasto.lugar_compra, gasto.motivo))
        
        gasto_id = cursor.lastrowid
        conn.commit()
        
        cursor.execute('SELECT * FROM gastos WHERE id = ?', (gasto_id,))
        result = cursor.fetchone()
        
        return dict(result)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/gastos/", response_model=List[GastoResponse])
def listar_gastos(skip: int = 0, limit: int = 100):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM gastos ORDER BY fecha DESC LIMIT ? OFFSET ?', (limit, skip))
    results = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in results]

# Endpoint de Balance
@app.get("/balance/")
def obtener_balance():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Total ingresos
    cursor.execute('SELECT SUM(monto) as total FROM ingresos')
    ingresos_result = cursor.fetchone()
    total_ingresos = ingresos_result['total'] or 0
    
    # Total gastos
    cursor.execute('SELECT SUM(valor) as total FROM gastos')
    gastos_result = cursor.fetchone()
    total_gastos = gastos_result['total'] or 0
    
    balance_total = total_ingresos - total_gastos
    
    conn.close()
    
    return {
        "total_ingresos": total_ingresos,
        "total_gastos": total_gastos,
        "balance_total": balance_total
    }

def open_browser():
    time.sleep(3)  # Esperar más tiempo para que el servidor inicie completamente
    try:
        webbrowser.open("http://localhost:8000")
        print("Navegador abierto en http://localhost:8000")
    except Exception as e:
        print(f"No se pudo abrir el navegador automáticamente: {e}")
        print("Por favor, abre manualmente: http://localhost:8000")

def main():
    print("=" * 60)
    print("SISTEMA DE GESTION DE SUSCRIPTORES Y FINANZAS")
    print("=" * 60)
    print("Licencia: MIT (Software Libre)")
    print("Version: 1.0.0 - Simple (Sin SQLAlchemy)")
    print("=" * 60)
    
    # Inicializar base de datos
    init_database()
    print(f"Base de datos creada en: {get_database_path()}")
    print("Sistema iniciado correctamente")
    print("Servidor web iniciado en http://localhost:8000")
    
    # Iniciar navegador
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

if __name__ == "__main__":
    main()
