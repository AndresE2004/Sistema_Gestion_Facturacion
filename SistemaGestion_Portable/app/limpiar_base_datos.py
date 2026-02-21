"""
Script para limpiar datos huérfanos de la base de datos
"""
import os
import sqlite3
from database_simple import get_connection

def limpiar_base_datos():
    """Eliminar datos huérfanos de la base de datos"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        print("🧹 Limpiando base de datos...")
        
        # Eliminar ingresos sin pago asociado
        cursor.execute('''
            DELETE FROM ingresos 
            WHERE pago_id NOT IN (SELECT id FROM pagos)
        ''')
        ingresos_huerfanos = cursor.rowcount
        print(f"📊 Eliminados {ingresos_huerfanos} ingresos huérfanos")
        
        # Eliminar recibos sin pago asociado
        cursor.execute('''
            DELETE FROM recibos 
            WHERE pago_id NOT IN (SELECT id FROM pagos)
        ''')
        recibos_huerfanos = cursor.rowcount
        print(f"🧾 Eliminados {recibos_huerfanos} recibos huérfanos")
        
        # Verificar y mostrar estado actual
        cursor.execute('SELECT COUNT(*) as total FROM suscriptores')
        suscriptores = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as total FROM pagos')
        pagos = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as total FROM ingresos')
        ingresos = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as total FROM gastos')
        gastos = cursor.fetchone()['total']
        
        cursor.execute('SELECT COALESCE(SUM(monto), 0) as total FROM ingresos')
        total_ingresos = cursor.fetchone()['total']
        
        cursor.execute('SELECT COALESCE(SUM(valor), 0) as total FROM gastos')
        total_gastos = cursor.fetchone()['total']
        
        balance = total_ingresos - total_gastos
        
        conn.commit()
        
        print("\n" + "="*50)
        print("📋 ESTADO ACTUAL DE LA BASE DE DATOS")
        print("="*50)
        print(f"👥 Suscriptores: {suscriptores}")
        print(f"💳 Pagos: {pagos}")
        print(f"💰 Ingresos: {ingresos}")
        print(f"💸 Gastos: {gastos}")
        print(f"💵 Total Ingresos: ${total_ingresos:.2f}")
        print(f"💳 Total Gastos: ${total_gastos:.2f}")
        print(f"📊 Balance: ${balance:.2f}")
        print("="*50)
        
        if ingresos_huerfanos > 0 or recibos_huerfanos > 0:
            print("✅ Base de datos limpiada correctamente")
        else:
            print("✅ No se encontraron datos huérfanos")
            
    except Exception as e:
        conn.rollback()
        print(f"❌ Error al limpiar base de datos: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    limpiar_base_datos()
    input("\nPresione Enter para continuar...")
