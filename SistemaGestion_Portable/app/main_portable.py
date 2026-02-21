"""
Aplicación principal FastAPI - Versión Portable
Sistema de Gestión de Suscriptores y Finanzas
"""
import os
import sys
import webbrowser
import threading
import time
import subprocess
from pathlib import Path

# Añadir el directorio actual al path para importaciones
if getattr(sys, 'frozen', False):
    # Si está empaquetado como ejecutable
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Si está en desarrollo
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, BASE_DIR)

# Importar FastAPI y componentes
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

# Importar rutas y configuración
from app.database_sqlite import init_database, get_database_path
from app.routes import suscriptores_standalone, pagos_standalone, recibos_standalone, gastos_standalone, balance_standalone

# Crear instancia de FastAPI
app = FastAPI(
    title="Sistema de Gestión de Suscriptores y Finanzas",
    description="Software libre para gestión de suscriptores, pagos mensuales, ingresos y gastos",
    version="1.0.0 - Portable",
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

# Incluir routers
app.include_router(suscriptores_standalone.router)
app.include_router(pagos_standalone.router)
app.include_router(recibos_standalone.router)
app.include_router(gastos_standalone.router)
app.include_router(balance_standalone.router)

# Servir interfaz estática mínima en /ui
static_dir = os.path.join(BASE_DIR, "app", "static")
if os.path.exists(static_dir):
    app.mount("/ui", StaticFiles(directory=static_dir), name="static")


@app.on_event("startup")
async def startup_event():
    """
    Inicializar la base de datos al iniciar la aplicación
    """
    print("🚀 Iniciando Sistema de Gestión de Suscriptores y Finanzas...")
    
    # Inicializar base de datos
    init_database()
    
    # Mostrar información de la base de datos
    db_path = get_database_path()
    print(f"📁 Base de datos creada en: {db_path}")
    
    print("✅ Sistema iniciado correctamente")
    print("🌐 Servidor web iniciado en http://localhost:8000")
    print("📊 Documentación API disponible en http://localhost:8000/docs")


@app.get("/")
def root():
    """
    Endpoint raíz con información del sistema
    """
    return RedirectResponse(url="/ui")


@app.get("/health")
def health_check():
    """
    Endpoint de verificación de salud del sistema
    """
    return {"status": "ok", "mensaje": "Sistema operativo"}


def open_browser():
    """
    Abrir navegador automáticamente después de un pequeño retraso
    """
    time.sleep(2)  # Esperar a que el servidor inicie
    webbrowser.open("http://localhost:8000")


def install_dependencies():
    """
    Instalar dependencias automáticamente si no están presentes
    """
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import pydantic
        print("✅ Dependencias ya instaladas")
        return True
    except ImportError as e:
        print(f"⚠️  Dependencia faltante: {e}")
        print("📦 Instalando dependencias automáticamente...")
        
        try:
            # Instalar dependencias
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "-r", os.path.join(BASE_DIR, "requirements_portable.txt")
            ])
            print("✅ Dependencias instaladas correctamente")
            return True
        except subprocess.CalledProcessError:
            print("❌ Error instalando dependencias")
            return False


def main():
    """
    Función principal para ejecutar la aplicación
    """
    print("=" * 60)
    print("🏢 SISTEMA DE GESTIÓN DE SUSCRIPTORES Y FINANZAS")
    print("=" * 60)
    print("📋 Licencia: MIT (Software Libre)")
    print("🔧 Versión: 1.0.0 - Portable")
    print("=" * 60)
    
    # Verificar/instalar dependencias
    if not install_dependencies():
        input("Presione Enter para salir...")
        return
    
    # Iniciar navegador en un hilo separado
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    import uvicorn
    
    # Ejecutar servidor
    uvicorn.run(
        "app.main_portable:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()
