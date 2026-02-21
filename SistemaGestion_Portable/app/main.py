"""
Aplicación principal FastAPI
Sistema de Gestión de Suscriptores y Finanzas
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from app.routes import suscriptores, pagos, recibos, gastos, balance

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
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(suscriptores.router)
app.include_router(pagos.router)
app.include_router(recibos.router)
app.include_router(gastos.router)
app.include_router(balance.router)

# Servir interfaz estática mínima en /ui
app.mount("/ui", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def root():
    """
    Endpoint raíz con información del sistema
    """
    # Redirigir a la interfaz amigable por defecto
    return RedirectResponse(url="/ui")


@app.get("/health")
def health_check():
    """
    Endpoint de verificación de salud del sistema
    """
    return {"status": "ok", "mensaje": "Sistema operativo"}

