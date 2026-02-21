# Sistema de Gestión de Suscriptores y Finanzas

Software libre (MIT) para la gestión completa de suscriptores, pagos mensuales, ingresos y gastos, con persistencia en PostgreSQL.

## 📋 Características

- ✅ Gestión completa de suscriptores/contratos
- ✅ Registro de pagos mensuales con historial
- ✅ Generación automática de recibos
- ✅ Registro automático de ingresos desde pagos
- ✅ Gestión de gastos (compras, pagos a trabajadores, etc.)
- ✅ Cálculo automático de balances financieros
- ✅ Consultas por rango de fechas
- ✅ API REST completa con documentación automática
- ✅ Base de datos PostgreSQL con triggers y validaciones

## 🏗️ Arquitectura

El sistema está construido con:

- **Backend**: FastAPI (Python)
- **Base de datos**: PostgreSQL
- **ORM**: SQLAlchemy
- **Validación**: Pydantic
- **API**: RESTful con documentación automática en `/docs`

### Estructura del Proyecto

```
Padre/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación principal FastAPI
│   ├── database.py          # Configuración de conexión a BD
│   ├── models.py            # Modelos SQLAlchemy
│   ├── schemas.py           # Esquemas Pydantic
│   └── routes/              # Endpoints de la API
│       ├── __init__.py
│       ├── suscriptores.py  # CRUD de suscriptores
│       ├── pagos.py         # Gestión de pagos
│       ├── recibos.py       # Consulta de recibos
│       ├── gastos.py        # CRUD de gastos
│       └── balance.py       # Consultas de balance
├── database/
│   └── schema.sql           # Script SQL completo
├── requirements.txt         # Dependencias Python
├── .env.example            # Ejemplo de configuración
└── README.md               # Este archivo
```

## 🚀 Instalación y Configuración (Usuario Final)

### Opción 1: Instalador Automático (Recomendado)

Para usuarios sin conocimientos técnicos:

1. **Ejecuta el instalador**: Haz doble clic en `install_and_run.ps1`
   - El script verificará e instalará Docker Desktop automáticamente si no está presente.
   - Requiere permisos de administrador la primera vez.
   - Una vez instalado, iniciará la aplicación automáticamente.

2. **Accede a la aplicación**:
   - Interfaz gráfica completa: http://localhost:8000
   - Panel de administración avanzado: http://localhost:8000/docs

### Opción 2: Instalación Manual

Si prefieres instalar manualmente:

#### Requisitos Previos

- Docker Desktop instalado (descárgalo desde https://www.docker.com/products/docker-desktop)

#### Pasos

1. **Ejecuta el script de inicio**:
   ```powershell
   .\run.ps1
   ```

2. **Accede a la aplicación**:
   - Interfaz gráfica: http://localhost:8000/ui
   - Documentación API: http://localhost:8000/docs

## 📱 Interfaz de Usuario

La aplicación incluye una interfaz web completa con:

- **Gestión de Suscriptores**: Crear y listar suscriptores
- **Registro de Pagos**: Formularios para pagos en efectivo o transferencia
- **Consulta de Balance**: Ver ingresos, gastos y balance general

No se requiere conocimiento técnico para operar el sistema.

## 🔌 Endpoints Principales

### Suscriptores

- `POST /suscriptores` - Crear suscriptor
- `GET /suscriptores` - Listar todos los suscriptores
- `GET /suscriptores/{id}` - Obtener suscriptor por ID
- `GET /suscriptores/por-contrato/{numero}` - Obtener por número de contrato
- `PUT /suscriptores/{id}` - Actualizar suscriptor
- `DELETE /suscriptores/{id}` - Eliminar suscriptor

### Pagos

- `POST /pagos` - Registrar pago (genera recibo e ingreso automáticamente)
- `GET /pagos` - Listar pagos (con filtros opcionales)
- `GET /pagos/{id}` - Obtener pago por ID
- `GET /pagos/suscriptor/{id}` - Listar pagos de un suscriptor
- `DELETE /pagos/{id}` - Eliminar pago

### Recibos

- `GET /recibos` - Listar todos los recibos
- `GET /recibos/{id}` - Obtener recibo por ID
- `GET /recibos/por-pago/{pago_id}` - Obtener recibo de un pago
- `GET /recibos/por-numero/{numero}` - Obtener recibo por número

### Gastos

- `POST /gastos` - Registrar gasto
- `GET /gastos` - Listar gastos (con filtros opcionales)
- `GET /gastos/{id}` - Obtener gasto por ID
- `PUT /gastos/{id}` - Actualizar gasto
- `DELETE /gastos/{id}` - Eliminar gasto

### Balance Financiero

- `GET /balance` - Balance general (todos los ingresos y gastos)
- `GET /balance/por-fechas?fecha_inicio=YYYY-MM-DD&fecha_fin=YYYY-MM-DD` - Balance por rango
- `GET /balance/ingresos` - Listar todos los ingresos

## 📝 Ejemplos de Uso

### Crear un suscriptor

```bash
curl -X POST "http://localhost:8000/suscriptores" \
  -H "Content-Type: application/json" \
  -d '{
    "numero_contrato": "CONT-001",
    "cedula": "1234567890",
    "nombre_completo": "Juan Pérez",
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

### Consultar balance por rango de fechas

```bash
curl "http://localhost:8000/balance/por-fechas?fecha_inicio=2024-01-01&fecha_fin=2024-01-31"
```

## 🗄️ Modelo de Base de Datos

### Tablas Principales

1. **suscriptores**: Información de suscriptores/contratos
2. **pagos**: Registro de pagos mensuales
3. **recibos**: Recibos generados automáticamente
4. **ingresos**: Ingresos registrados automáticamente desde pagos
5. **gastos**: Gastos del negocio

### Características de la BD

- Triggers automáticos para generar recibos
- Triggers automáticos para registrar ingresos
- Validaciones a nivel de base de datos
- Índices para optimizar consultas
- Vistas para balances financieros

## 🔒 Seguridad

- Validación de datos con Pydantic
- Restricciones a nivel de base de datos
- Validación de tipos de pago
- Prevención de duplicados (mismo mes/año por suscriptor)

## 📄 Licencia

Este proyecto está bajo la licencia MIT (Software Libre). Ver archivo LICENSE para más detalles.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o pull request.

## 📧 Soporte

Para problemas o preguntas, abre un issue en el repositorio del proyecto.

## 📝 TODO

- ✅ Analizar README y archivos principales
- ✅ Extraer endpoints y modelos
- ✅ Resumir propósito y sugerir próximos pasos
- ✅ Añadir empaquetado Docker y UI mínima
- ✅ Crear script de ejecución para usuario no técnico
- ✅ Generar instalador Windows con auto-instalación de Docker
- ✅ Implementar interfaz gráfica completa con formularios

---

**Desarrollado con ❤️ usando FastAPI y PostgreSQL**

