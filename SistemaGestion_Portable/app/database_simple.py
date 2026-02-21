"""
Base de datos SQLite simplificada - Sin SQLAlchemy
"""
import sqlite3
import os
import hashlib
from datetime import datetime, date

# Obtener el directorio donde se ejecuta la aplicación
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "sistema_suscriptores.db")

def get_connection():
    """Obtener conexión a la base de datos"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Inicializar la base de datos"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Crear tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            nombre_completo TEXT NOT NULL,
            rol TEXT NOT NULL CHECK (rol IN ('admin', 'user')),
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Crear tablas principales
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS suscriptores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_contrato TEXT UNIQUE NOT NULL,
            cedula TEXT UNIQUE NOT NULL,
            nombre_completo TEXT NOT NULL,
            fecha_suscripcion DATE NOT NULL,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pagos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            suscriptor_id INTEGER NOT NULL,
            mes INTEGER NOT NULL CHECK (mes >= 1 AND mes <= 12),
            anio INTEGER NOT NULL CHECK (anio >= 2000),
            fecha_pago DATE NOT NULL,
            valor REAL NOT NULL CHECK (valor > 0),
            tipo_pago TEXT NOT NULL CHECK (tipo_pago IN ('efectivo', 'transferencia')),
            entidad_bancaria TEXT,
            nombre_transferente TEXT,
            monto_efectivo REAL,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (suscriptor_id) REFERENCES suscriptores(id) ON DELETE CASCADE,
            UNIQUE(suscriptor_id, mes, anio)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recibos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pago_id INTEGER UNIQUE NOT NULL,
            numero_recibo TEXT UNIQUE NOT NULL,
            fecha_emision TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pago_id) REFERENCES pagos(id) ON DELETE CASCADE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ingresos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pago_id INTEGER UNIQUE NOT NULL,
            monto REAL NOT NULL CHECK (monto > 0),
            fecha DATE NOT NULL,
            origen TEXT NOT NULL DEFAULT 'pago de suscriptor',
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pago_id) REFERENCES pagos(id) ON DELETE CASCADE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_gasto TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            valor REAL NOT NULL CHECK (valor > 0),
            fecha DATE NOT NULL,
            lugar_compra TEXT,
            motivo TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Crear índices para búsquedas
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_suscriptores_numero_contrato ON suscriptores(numero_contrato)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_suscriptores_cedula ON suscriptores(cedula)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_suscriptores_email ON suscriptores(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_suscriptores_nombre ON suscriptores(nombre_completo)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_pagos_suscriptor ON pagos(suscriptor_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_pagos_fecha ON pagos(fecha_pago)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_recibos_pago ON recibos(pago_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ingresos_pago ON ingresos(pago_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_gastos_fecha ON gastos(fecha)')
    
    # Crear usuario admin por defecto si no existe
    cursor.execute('SELECT COUNT(*) as count FROM usuarios WHERE email = ?', ('admin@gmail.com',))
    if cursor.fetchone()['count'] == 0:
        hashed_password = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute('''
            INSERT INTO usuarios (email, password, nombre_completo, rol)
            VALUES (?, ?, ?, ?)
        ''', ('admin@gmail.com', hashed_password, 'Administrador', 'admin'))
        print("👤 Usuario admin creado: admin@gmail.com / admin123")
    else:
        # Verificar si la contraseña está hasheada correctamente
        cursor.execute('SELECT password FROM usuarios WHERE email = ?', ('admin@gmail.com',))
        current_password = cursor.fetchone()['password']
        correct_hash = hashlib.sha256('admin123'.encode()).hexdigest()
        
        if current_password != correct_hash:
            print("🔧 Corrigiendo contraseña del admin...")
            cursor.execute('''
                UPDATE usuarios SET password = ? WHERE email = ?
            ''', (correct_hash, 'admin@gmail.com'))
            conn.commit()
            print("✅ Contraseña del admin corregida")
    
    conn.commit()
    conn.close()

def generar_numero_recibo():
    """Generar número de recibo automático"""
    conn = get_connection()
    cursor = conn.cursor()
    
    fecha_str = datetime.now().strftime("%Y%m%d")
    
    cursor.execute('''
        SELECT COUNT(*) as contador 
        FROM recibos 
        WHERE numero_recibo LIKE ?
    ''', (f"REC-{fecha_str}-%",))
    
    contador = cursor.fetchone()['contador'] + 1
    numero_recibo = f"REC-{fecha_str}-{contador:05d}"
    
    conn.close()
    return numero_recibo

def crear_recibo_y_ingreso(pago_id: int, suscriptor_nombre: str, valor: float, fecha_pago: date):
    """Crear recibo e ingreso automáticamente"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Generar número de recibo
        numero_recibo = generar_numero_recibo()
        
        # Crear recibo
        cursor.execute('''
            INSERT INTO recibos (pago_id, numero_recibo, fecha_emision)
            VALUES (?, ?, ?)
        ''', (pago_id, numero_recibo, datetime.utcnow()))
        
        # Crear ingreso
        origen = f"Pago de suscriptor: {suscriptor_nombre}"
        cursor.execute('''
            INSERT INTO ingresos (pago_id, monto, fecha, origen, fecha_creacion)
            VALUES (?, ?, ?, ?, ?)
        ''', (pago_id, valor, fecha_pago, origen, datetime.utcnow()))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_database_path():
    """Obtener ruta de la base de datos"""
    return DB_PATH
