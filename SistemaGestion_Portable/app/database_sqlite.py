"""
Módulo de conexión a la base de datos SQLite para ejecutable autónomo
"""
import os
import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Obtener el directorio donde se ejecuta el aplicación
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "sistema_suscriptores.db")

# Configuración de la base de datos SQLite
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Crear motor de base de datos con configuración específica para SQLite
engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
    connect_args={
        "check_same_thread": False,
        "timeout": 20
    },
    echo=False
)

# Crear sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()


def get_db():
    """
    Generador de sesión de base de datos para dependencias de FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """
    Inicializar la base de datos creando todas las tablas
    """
    # Importar modelos aquí para evitar circular imports
    from app.models import Suscriptor, Pago, Recibo, Ingreso, Gasto
    
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    # Crear índices adicionales si no existen
    create_sqlite_indexes()


def create_sqlite_indexes():
    """
    Crear índices específicos para SQLite
    """
    connection = engine.connect()
    
    # Índices para suscriptores
    connection.execute(text("CREATE INDEX IF NOT EXISTS idx_suscriptores_numero_contrato ON suscriptores(numero_contrato)"))
    connection.execute(text("CREATE INDEX IF NOT EXISTS idx_suscriptores_cedula ON suscriptores(cedula)"))
    connection.execute(text("CREATE INDEX IF NOT EXISTS idx_suscriptores_fecha_suscripcion ON suscriptores(fecha_suscripcion)"))
    
    # Índices para pagos
    connection.execute(text("CREATE INDEX IF NOT EXISTS idx_pagos_suscriptor ON pagos(suscriptor_id)"))
    connection.execute(text("CREATE INDEX IF NOT EXISTS idx_pagos_fecha ON pagos(fecha_pago)"))
    connection.execute(text("CREATE INDEX IF NOT EXISTS idx_pagos_mes_anio ON pagos(mes, anio)"))
    connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS idx_pagos_unico_mes_anio ON pagos(suscriptor_id, mes, anio)"))
    
    # Índices para recibos
    connection.execute(text("CREATE INDEX IF NOT EXISTS idx_recibos_pago ON recibos(pago_id)"))
    connection.execute(text("CREATE INDEX IF NOT EXISTS idx_recibos_numero ON recibos(numero_recibo)"))
    
    # Índices para ingresos
    connection.execute(text("CREATE INDEX IF NOT EXISTS idx_ingresos_pago ON ingresos(pago_id)"))
    connection.execute(text("CREATE INDEX IF NOT EXISTS idx_ingresos_fecha ON ingresos(fecha)"))
    
    # Índices para gastos
    connection.execute(text("CREATE INDEX IF NOT EXISTS idx_gastos_tipo ON gastos(tipo_gasto)"))
    connection.execute(text("CREATE INDEX IF NOT EXISTS idx_gastos_fecha ON gastos(fecha)"))
    
    connection.close()


def get_database_path():
    """
    Obtener la ruta completa de la base de datos
    """
    return DB_PATH
