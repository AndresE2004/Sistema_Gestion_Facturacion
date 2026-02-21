import sqlite3
import hashlib
from database_simple import get_connection

def hash_password(password: str) -> str:
    """Hashear contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

# Verificar si el usuario admin existe
conn = get_connection()
cursor = conn.cursor()

print('=== VERIFICANDO USUARIO ADMIN ===')
cursor.execute('SELECT * FROM usuarios WHERE email = ?', ('admin@gmail.com',))
user = cursor.fetchone()

if user:
    print('Usuario encontrado:', dict(user))
    print('Email:', user['email'])
    print('Contraseña hasheada:', user['password'])
    print('Contraseña admin123 hasheada:', hash_password('admin123'))
    print('¿Contraseñas coinciden?:', user['password'] == hash_password('admin123'))
else:
    print('❌ Usuario admin NO encontrado')

conn.close()
