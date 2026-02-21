"""
Módulo de conexión a la base de datos PostgreSQL
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Configuración de la base de datos desde variables de entorno
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/sistema_suscriptores"
)

# Crear motor de base de datos
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

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

