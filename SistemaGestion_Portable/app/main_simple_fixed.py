"""
Aplicación principal FastAPI - Versión Simple sin SQLAlchemy
Sistema de Gestión de Suscriptores y Finanzas
"""
import os
import sys
import webbrowser
import threading
import time
import sqlite3
from datetime import datetime, date, timedelta
from typing import List, Optional
from pathlib import Path

# Configurar paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURRENT_DIR)

# Importar FastAPI
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime, timedelta
import sqlite3
import hashlib
from database_simple import get_connection, init_database

# Modelos de datos
class SuscriptorCreate(BaseModel):
    numero_contrato: str
    cedula: str
    nombre_completo: str
    email: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    fecha_suscripcion: str

class SuscriptorResponse(BaseModel):
    id: int
    numero_contrato: str
    cedula: str
    nombre_completo: str
    email: str
    telefono: Optional[str]
    direccion: Optional[str]
    fecha_suscripcion: str
    fecha_creacion: str
    fecha_actualizacion: str

class PagoCreate(BaseModel):
    suscriptor_id: int
    mes: int
    anio: int
    fecha_pago: str
    valor: float
    tipo_pago: str
    monto_efectivo: Optional[float] = None
    entidad_bancaria: Optional[str] = None
    nombre_transferente: Optional[str] = None

class PagoResponse(BaseModel):
    id: int
    suscriptor_id: int
    mes: int
    anio: int
    fecha_pago: str
    valor: float
    tipo_pago: str
    monto_efectivo: Optional[float]
    entidad_bancaria: Optional[str]
    nombre_transferente: Optional[str]

class GastoCreate(BaseModel):
    tipo_gasto: str
    valor: float
    descripcion: str
    fecha: str
    lugar_compra: Optional[str] = None
    motivo: Optional[str] = None
    suscriptor_id: Optional[int] = None

class GastoResponse(BaseModel):
    id: int
    tipo_gasto: str
    valor: float
    descripcion: str
    fecha: str
    lugar_compra: Optional[str]
    motivo: Optional[str]
    suscriptor_id: Optional[int]

class UserCreate(BaseModel):
    email: str
    password: str
    nombre_completo: str
    rol: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    nombre_completo: str
    rol: str
    fecha_creacion: str
    fecha_actualizacion: str

class UserUpdate(BaseModel):
    rol: str

# Dependency para obtener usuario actual simplificado
async def get_current_user_simple():
    """Obtener usuario actual - Simplificado"""
    # Para simplificar, devolver un usuario fijo
    return {
        "id": 1,
        "email": "admin@gmail.com", 
        "nombre_completo": "Administrador",
        "rol": "admin",
        "fecha_creacion": "2026-02-08 05:35:00",
        "fecha_actualizacion": "2026-02-08 05:35:00"
    }

# Configuración simple sin JWT
SECRET_KEY = "sistema_simple_sin_jwt"  # Ya no se usa
ALGORITHM = "HS256"  # Ya no se usa

def hash_password(password: str) -> str:
    """Hashear contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña"""
    return hash_password(plain_password) == hashed_password

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

# Servir archivos estáticos en /ui
static_dir = os.path.join(CURRENT_DIR, "static")
if os.path.exists(static_dir):
    app.mount("/ui", StaticFiles(directory=static_dir, html=True), name="static")

# Endpoint raíz - redirigir a login
@app.get("/")
def root():
    return RedirectResponse(url="/ui/login.html")

# Endpoint raíz de UI - redirigir a la página mejorada
@app.get("/ui")
def ui_root():
    return RedirectResponse(url="/ui/mejorado_con_auth.html")

# Endpoint para limpiar token (para testing)
@app.get("/auth/clear")
def clear_token():
    """Limpiar token de localStorage (para testing)"""
    return """
    <script>
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/ui/login.html';
    </script>
    """

# Endpoints de Autenticación
@app.post("/auth/login")
async def login(user_credentials: UserLogin):
    """Iniciar sesión - Simplificado sin JWT"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM usuarios WHERE email = ?', (user_credentials.email,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        
        if not verify_password(user_credentials.password, user['password']):
            raise HTTPException(status_code=401, detail="Contraseña incorrecta")
        
        # Simplificado: Devolver usuario directamente sin token
        user_dict = dict(user)
        del user_dict['password']
        
        return {
            "usuario": user_dict,
            "mensaje": "Login exitoso"
        }
    finally:
        conn.close()

# Endpoint eliminado - estaba duplicado y causando conflicto

@app.post("/auth/register")
async def register(user_data: UserCreate):
    """Registrar nuevo usuario"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar si el email ya existe
        cursor.execute('SELECT id FROM usuarios WHERE email = ?', (user_data.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="El email ya está registrado")
        
        # Crear usuario
        hashed_password = hash_password(user_data.password)
        cursor.execute('''
            INSERT INTO usuarios (email, password, nombre_completo, rol)
            VALUES (?, ?, ?, ?)
        ''', (user_data.email, hashed_password, user_data.nombre_completo, 'user'))
        
        conn.commit()
        
        return {"message": "Usuario creado exitosamente"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user_simple)):
    """Obtener información del usuario actual"""
    if not current_user:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    return current_user

@app.get("/auth/users")
async def list_users(current_user: dict = Depends(get_current_user_simple)):
    """Listar usuarios (solo admin)"""
    if not current_user or current_user['rol'] != 'admin':
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, email, nombre_completo, rol, fecha_creacion FROM usuarios ORDER BY fecha_creacion DESC')
    users = cursor.fetchall()
    conn.close()
    
    return [dict(user) for user in users]

@app.put("/auth/users/{user_id}/role", response_model=UserResponse)
async def update_user_role(user_id: int, role_data: dict, current_user: dict = Depends(get_current_user_simple)):
    """Actualizar rol de usuario"""
    if not current_user or current_user['rol'] != 'admin':
        raise HTTPException(status_code=403, detail="Solo los administradores pueden actualizar roles")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('UPDATE usuarios SET rol = ?, fecha_actualizacion = ? WHERE id = ?', 
                   (role_data['rol'], datetime.utcnow(), user_id))
        conn.commit()
        
        # Obtener usuario actualizado
        cursor.execute('SELECT * FROM usuarios WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        return dict(result)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/health")
def health_check():
    return {"status": "ok", "mensaje": "Sistema operativo"}

# Endpoints de Suscriptores
@app.post("/suscriptores/", response_model=SuscriptorResponse, status_code=status.HTTP_201_CREATED)
def crear_suscriptor(suscriptor: SuscriptorCreate, current_user: dict = Depends(get_current_user_simple)):
    if not current_user:
        raise HTTPException(status_code=401, detail="No autenticado")
    
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
        
        cursor.execute('SELECT id FROM suscriptores WHERE email = ?', (suscriptor.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Ya existe un suscriptor con este email")
        
        # Insertar suscriptor
        cursor.execute('''
            INSERT INTO suscriptores (numero_contrato, cedula, nombre_completo, email, telefono, direccion, fecha_suscripcion, fecha_creacion, fecha_actualizacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            suscriptor.numero_contrato,
            suscriptor.cedula,
            suscriptor.nombre_completo,
            suscriptor.email,
            suscriptor.telefono,
            suscriptor.direccion,
            suscriptor.fecha_suscripcion,
            datetime.utcnow(),
            datetime.utcnow()
        ))
        
        suscriptor_id = cursor.lastrowid
        conn.commit()
        
        # Obtener suscriptor creado
        cursor.execute('SELECT * FROM suscriptores WHERE id = ?', (suscriptor_id,))
        result = cursor.fetchone()
        conn.close()
        
        return dict(result)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/suscriptores/", response_model=List[SuscriptorResponse])
def listar_suscriptores(skip: int = 0, limit: int = 100, current_user: dict = Depends(get_current_user_simple), email: str = ""):
    if not current_user:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Búsqueda por email
    if email:
        cursor.execute('SELECT * FROM suscriptores WHERE email LIKE ? ORDER BY nombre_completo LIMIT ? OFFSET ?', 
                   (f'%{email}%', limit, skip))
    else:
        cursor.execute('SELECT * FROM suscriptores ORDER BY nombre_completo LIMIT ? OFFSET ?', (limit, skip))
    
    results = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in results]

@app.get("/suscriptores/buscar", response_model=List[SuscriptorResponse])
def buscar_suscriptores(q: str = "", current_user: dict = Depends(get_current_user_simple)):
    if not current_user:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    if q:
        cursor.execute('''
            SELECT * FROM suscriptores 
            WHERE nombre_completo LIKE ? OR 
                 cedula LIKE ? OR 
                 email LIKE ? OR 
                 numero_contrato LIKE ?
            ORDER BY nombre_completo
            LIMIT 50
        ''', (f'%{q}%', f'%{q}%', f'%{q}%', f'%{q}%'))
    else:
        cursor.execute('SELECT * FROM suscriptores ORDER BY nombre_completo LIMIT 50')
    
    results = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in results]

@app.get("/suscriptores/{suscriptor_id}", response_model=SuscriptorResponse)
def obtener_suscriptor(suscriptor_id: int, current_user: dict = Depends(get_current_user_simple)):
    if not current_user:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM suscriptores WHERE id = ?', (suscriptor_id,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        raise HTTPException(status_code=404, detail="Suscriptor no encontrado")
    
    return dict(result)

@app.put("/suscriptores/{suscriptor_id}", response_model=SuscriptorResponse)
def actualizar_suscriptor(suscriptor_id: int, datos: dict, current_user: dict = Depends(get_current_user_simple)):
    if not current_user:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar que el suscriptor existe
        cursor.execute('SELECT * FROM suscriptores WHERE id = ?', (suscriptor_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Suscriptor no encontrado")
        
        # Construir consulta dinámica
        set_clause = []
        values = []
        
        for campo, valor in datos.items():
            if campo in ['nombre_completo', 'numero_contrato', 'cedula', 'fecha_suscripcion', 'email', 'telefono', 'direccion']:
                set_clause.append(f"{campo} = ?")
                values.append(valor)
        
        if not set_clause:
            raise HTTPException(status_code=400, detail="No hay campos válidos para actualizar")
        
        # Agregar fecha de actualización
        set_clause.append("fecha_actualizacion = ?")
        values.append(datetime.utcnow())
        values.append(suscriptor_id)
        
        query = f"UPDATE suscriptores SET {', '.join(set_clause)} WHERE id = ?"
        cursor.execute(query, values)
        
        conn.commit()
        
        # Obtener suscriptor actualizado
        cursor.execute('SELECT * FROM suscriptores WHERE id = ?', (suscriptor_id,))
        result = cursor.fetchone()
        
        return dict(result)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.delete("/suscriptores/{suscriptor_id}")
def eliminar_suscriptor(suscriptor_id: int, current_user: dict = Depends(get_current_user_simple)):
    if not current_user:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar que el suscriptor existe
        cursor.execute('SELECT * FROM suscriptores WHERE id = ?', (suscriptor_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Suscriptor no encontrado")
        
        # Eliminar todos los registros relacionados en cascada
        cursor.execute('DELETE FROM ingresos WHERE pago_id IN (SELECT id FROM pagos WHERE suscriptor_id = ?)', (suscriptor_id,))
        cursor.execute('DELETE FROM recibos WHERE pago_id IN (SELECT id FROM pagos WHERE suscriptor_id = ?)', (suscriptor_id,))
        cursor.execute('DELETE FROM pagos WHERE suscriptor_id = ?', (suscriptor_id,))
        cursor.execute('DELETE FROM suscriptores WHERE id = ?', (suscriptor_id,))
        
        conn.commit()
        
        return {"message": "Suscriptor eliminado exitosamente"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

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

@app.delete("/pagos/{pago_id}")
def eliminar_pago(pago_id: int, current_user: dict = Depends(get_current_user_simple)):
    if not current_user:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar que el pago existe
        cursor.execute('SELECT * FROM pagos WHERE id = ?', (pago_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Pago no encontrado")
        
        # Eliminar pago y sus registros relacionados en cascada
        cursor.execute('DELETE FROM ingresos WHERE pago_id = ?', (pago_id,))
        cursor.execute('DELETE FROM recibos WHERE pago_id = ?', (pago_id,))
        cursor.execute('DELETE FROM pagos WHERE id = ?', (pago_id,))
        
        conn.commit()
        
        return {"message": "Pago eliminado exitosamente"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.delete("/gastos/{gasto_id}")
def eliminar_gasto(gasto_id: int, current_user: dict = Depends(get_current_user_simple)):
    if not current_user:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar que el gasto existe
        cursor.execute('SELECT * FROM gastos WHERE id = ?', (gasto_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Gasto no encontrado")
        
        # Eliminar gasto
        cursor.execute('DELETE FROM gastos WHERE id = ?', (gasto_id,))
        
        conn.commit()
        
        return {"message": "Gasto eliminado exitosamente"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/ingresos/")
def listar_ingresos(skip: int = 0, limit: int = 100):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM ingresos ORDER BY fecha DESC LIMIT ? OFFSET ?', (limit, skip))
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
        # Verificar si ya hay una ventana abierta para evitar duplicados
        import subprocess
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq chrome.exe'], capture_output=True, text=True)
        if 'chrome.exe' not in result.stdout:
            webbrowser.open("http://localhost:8000")
            print("Navegador abierto en http://localhost:8000")
        else:
            print("Navegador ya está abierto, abriendo nueva pestaña...")
            webbrowser.open("http://localhost:8000")
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
    
    # Limpiar datos huérfanos automáticamente
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM ingresos WHERE pago_id NOT IN (SELECT id FROM pagos)')
        cursor.execute('DELETE FROM recibos WHERE pago_id NOT IN (SELECT id FROM pagos)')
        conn.commit()
        print("🧹 Datos huérfanos limpiados automáticamente")
    except Exception as e:
        print(f"Error limpiando datos: {e}")
    finally:
        conn.close()
    
    print(f"Base de datos creada en: {sistema_suscriptores.db}")
    print("Sistema iniciado correctamente")
    print("Servidor web iniciado en http://localhost:8000")
    print("Interfaz web disponible en http://localhost:8000/ui")
    
    # Iniciar navegador
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

if __name__ == "__main__":
    main()
