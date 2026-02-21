"""
Aplicación principal FastAPI para ejecutable autónomo
Sistema de Gestión de Suscriptores y Finanzas
"""
import os
import sys
import webbrowser
import threading
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

# Añadir el directorio actual al path para importaciones
if getattr(sys, 'frozen', False):
    # Si está empaquetado como ejecutable
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Si está en desarrollo
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, BASE_DIR)

# Importar rutas y configuración
from app.database_sqlite import init_database, get_database_path
from app.routes import suscriptores_standalone, pagos_standalone, recibos_standalone, gastos_standalone, balance_standalone

# Crear instancia de FastAPI
app = FastAPI(
    title="Sistema de Gestión de Suscriptores y Finanzas",
    description="Software libre para gestión de suscriptores, pagos mensuales, ingresos y gastos",
    version="1.0.0",
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


def main():
    """
    Función principal para ejecutar la aplicación
    """
    print("=" * 60)
    print("🏢 SISTEMA DE GESTIÓN DE SUSCRIPTORES Y FINANZAS")
    print("=" * 60)
    print("📋 Licencia: MIT (Software Libre)")
    print("🔧 Versión: 1.0.0 - Ejecutable Autónomo")
    print("=" * 60)
    
    # Iniciar navegador en un hilo separado
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    import uvicorn
    
    # Ejecutar servidor
    uvicorn.run(
        "app.main_standalone:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()
