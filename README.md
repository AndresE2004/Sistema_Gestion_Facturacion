# Sistema de Gestión de Suscriptores y Finanzas

Software libre (MIT) para la gestión completa de suscriptores, pagos mensuales, ingresos y gastos, con persistencia en SQLite.

##  Características

-  Gestión completa de suscriptores/contratos
-  Registro de pagos mensuales con historial
-  Generación automática de recibos
-  Registro automático de ingresos desde pagos
-  Gestión de gastos (compras, pagos a trabajadores, etc.)
-  Cálculo automático de balances financieros
-  Consultas por rango de fechas
-  API REST completa con documentación automática
-  Base de datos SQLite con validaciones
-  Autenticación simplificada sin JWT
-  Búsqueda de suscriptores por ID
-  Edición inline de datos
-  Email como dato de contacto principal

##  Arquitectura

El sistema está construido con:

- **Backend**: FastAPI (Python)
- **Base de datos**: SQLite simple
- **Frontend**: HTML/JavaScript vanilla
- **Autenticación**: Simplificada sin JWT
- **API**: RESTful con documentación automática en `/docs`

### Estructura del Proyecto

```
Padre/
├── SistemaGestion_Portable/
│   ├── app/
│   │   ├── main_simple_fixed.py    # Aplicación principal FastAPI
│   │   ├── database_simple.py     # Configuración de conexión a BD SQLite
│   │   ├── static/               # Archivos frontend
│   │   │   ├── login.html        # Página de login
│   │   │   ├── mejorado_con_auth.html  # Dashboard principal
│   │   │   └── login_simple.html # Login alternativo
│   │   ├── actualizar_db.py       # Script para actualizar BD
│   │   └── sistema_suscriptores.db  # Base de datos SQLite
│   ├── INICIAR.bat             # Script de inicio para Windows
│   └── README.md               # Este archivo
└── README.md                   # Este archivo
```

##  Instalación y Configuración (Usuario Final)

### Requisitos Previos

- Python 3.7+ instalado
- Módulos Python: fastapi, uvicorn, pydantic

### Instalación Rápida

1. **Clona o descarga el proyecto**
2. **Instala dependencias**:
   ```bash
   pip install fastapi uvicorn pydantic
   ```
3. **Ejecuta el sistema**:
   ```bash
   cd SistemaGestion_Portable/app
   python main_simple_fixed.py
   ```

### Acceso a la Aplicación

- **Interfaz principal**: http://localhost:8000/mejorado_con_auth.html
- **Documentación API**: http://localhost:8000/docs
- **API directa**: http://localhost:8000/

### Script de Inicio Automático (Windows)

Ejecuta `INICIAR.bat` para iniciar el sistema automáticamente en Windows.

##  Interfaz de Usuario

La aplicación incluye una interfaz web completa con:

- **Login**: Autenticación simplificada
- **Dashboard**: Panel principal con pestañas organizadas
- **Gestión de Suscriptores**: Crear, editar, listar suscriptores
- **Registro de Pagos**: Formularios para pagos en efectivo o transferencia
- **Consulta de Balance**: Ver ingresos, gastos y balance general
- **Administración**: Gestión de usuarios (solo admin)
- **Búsqueda**: Búsqueda de suscriptores por ID con verificación

### Características Especiales

- **Edición Inline**: Haz clic en cualquier celda para editar
- **Búsqueda por ID**: Ingresa ID de suscriptor para verificar datos
- **Email como Contacto**: Email visible en listas y formularios
- **Validación Automática**: Verificación de datos antes de guardar
- **Sin Pop-ups**: Información mostrada directamente en la interfaz

##  Endpoints Principales

### Autenticación

- `POST /auth/login` - Iniciar sesión
- `GET /auth/me` - Obtener usuario actual
- `GET /auth/users` - Listar usuarios (admin)

### Suscriptores

- `POST /suscriptores` - Crear suscriptor
- `GET /suscriptores` - Listar todos los suscriptores
- `GET /suscriptores/{id}` - Obtener suscriptor por ID
- `GET /suscriptores/buscar?q=` - Buscar suscriptores
- `PUT /suscriptores/{id}` - Actualizar suscriptor
- `DELETE /suscriptores/{id}` - Eliminar suscriptor

### Pagos

- `POST /pagos` - Registrar pago (genera recibo e ingreso automáticamente)
- `GET /pagos` - Listar pagos (con filtros opcionales)
- `GET /pagos/{id}` - Obtener pago por ID
- `GET /pagos/suscriptor/{id}` - Listar pagos de un suscriptor
- `DELETE /pagos/{id}` - Eliminar pago

### Gastos

- `POST /gastos` - Registrar gasto
- `GET /gastos` - Listar gastos (con filtros opcionales)
- `GET /gastos/{id}` - Obtener gasto por ID
- `PUT /gastos/{id}` - Actualizar gasto
- `DELETE /gastos/{id}` - Eliminar gasto

### Balance Financiero

- `GET /balance` - Balance general (todos los ingresos y gastos)
- `GET /balance/ingresos` - Listar todos los ingresos
- `GET /gastos` - Listar todos los gastos

##  Ejemplos de Uso

### Crear un suscriptor

```bash
curl -X POST "http://localhost:8000/suscriptores" \
  -H "Content-Type: application/json" \
  -d '{
    "numero_contrato": "CONT-001",
    "cedula": "1234567890",
    "nombre_completo": "Juan Pérez",
    "email": "juan@email.com",
    "telefono": "555-1234",
    "direccion": "Calle Principal 123",
    "fecha_suscripcion": "2024-01-15"
  }'
```

### Registrar un pago en efectivo

```bash
curl -X POST "http://localhost:8000/pagos" \
  -H "Content-Type: application/json" \
  -d '{
    "suscriptor_id": 1,
    "mes": 1,
    "anio": 2024,
    "fecha_pago": "2024-01-20",
    "valor": 50.00,
    "tipo_pago": "efectivo",
    "monto_efectivo": 50.00
  }'
```

### Registrar un pago por transferencia

```bash
curl -X POST "http://localhost:8000/pagos" \
  -H "Content-Type: application/json" \
  -d '{
    "suscriptor_id": 1,
    "mes": 2,
    "anio": 2024,
    "fecha_pago": "2024-02-15",
    "valor": 50.00,
    "tipo_pago": "transferencia",
    "entidad_bancaria": "Banco del Pacífico",
    "nombre_transferente": "Juan Pérez"
  }'
```

### Registrar un gasto

```bash
curl -X POST "http://localhost:8000/gastos" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_gasto": "compra_repuestos",
    "descripcion": "Compra de llaves",
    "valor": 25.50,
    "fecha": "2024-01-25",
    "lugar_compra": "Ferretería Central"
  }'
```

### Consultar balance general

```bash
curl "http://localhost:8000/balance"
```

##  Modelo de Base de Datos

### Tablas Principales

1. **suscriptores**: Información de suscriptores/contratos
2. **pagos**: Registro de pagos mensuales
3. **recibos**: Recibos generados automáticamente
4. **ingresos**: Ingresos registrados automáticamente desde pagos
5. **gastos**: Gastos del negocio
6. **usuarios**: Usuarios del sistema

### Características de la BD

- Base de datos SQLite simple
- Validaciones a nivel de aplicación
- Índices para optimizar consultas
- Datos de contacto completos (email, teléfono, dirección)

##  Seguridad

- Validación de datos con Pydantic
- Autenticación simplificada sin JWT
- Validación de tipos de pago
- Prevención de duplicados (mismo mes/año por suscriptor)
- Roles de usuario (admin/user)



### Versión 1.0.0 - Simple

-  Sistema básico de gestión de suscriptores
-  Registro de pagos con generación de recibos
-  Gestión de gastos
-  Balance financiero
-  Autenticación simplificada
-  Interfaz web completa
-  Búsqueda por ID de suscriptor
-  Edición inline de datos
-  Email como dato de contacto

---



