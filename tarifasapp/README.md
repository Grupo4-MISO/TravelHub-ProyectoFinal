# Tarifas App

Microservicio de TravelHub para la gestión de tarifas de servicios de viaje.

## Estructura

```
tarifasapp/
├── app/
│   ├── api/          # Endpoints REST
│   ├── db/           # Modelos de base de datos
│   ├── services/     # Lógica de negocio
│   ├── utils/        # Utilidades
│   └── data/         # Datos iniciales
├── tests/            # Tests unitarios e integración
├── chart/            # Helm charts para deployment
├── instance/         # Configuración por instancia
├── main.py           # Punto de entrada
├── requirements.txt  # Dependencias
├── Dockerfile        # Imagen Docker
├── buildspec_CI.yml  # Pipeline CI
└── buildspec_CD.yml  # Pipeline CD
```

## Requisitos

- Python 3.12+
- PostgreSQL (opcional, usa SQLite por defecto)

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecutar localmente

```bash
python main.py
```

El servidor estará disponible en `http://localhost:3008`

## API Endpoints

- `GET /health` - Health check
- `GET /tarifas` - Obtener todas las tarifas
- `POST /tarifas` - Crear nueva tarifa
- `GET /tarifas/<id>` - Obtener tarifa por ID
- `PUT /tarifas/<id>` - Actualizar tarifa
- `DELETE /tarifas/<id>` - Eliminar tarifa
- `GET /descuentos` - Obtener descuentos con filtros por activos y tarifa
- `POST /descuentos` - Crear nuevo descuento por porcentaje
- `GET /descuentos/<id>` - Obtener descuento por ID
- `PUT /descuentos/<id>` - Actualizar descuento
- `DELETE /descuentos/<id>` - Eliminar descuento
- `POST /seed` - Poblar base de datos con datos de ejemplo
- `GET /swagger/` - Documentación interactiva

## Descuentos

Un descuento pertenece a una tarifa existente mediante `tarifa_id` y aplica como porcentaje sobre `valor_base`, por lo que es independiente de la moneda de la tarifa.

Ejemplo de creación:

```json
{
	"nombre": "Promo verano",
	"tarifa_id": "550e8400-e29b-41d4-a716-446655440000",
	"porcentaje": 15,
	"activo": true,
	"vigencia_inicio": "2026-05-01T00:00:00Z",
	"vigencia_fin": "2026-12-31T23:59:59Z"
}
```

## Contrato de tarifa

El API usa estos campos principales para crear y devolver tarifas:

- `hotel_id`
- `valor_base`
- `valor_descuento_total`
- `valor_final`
- `moneda`
- `categoria_habitacion`
- `vigencia_inicio`
- `vigencia_fin`

La respuesta de tarifa incluye también `descuentos_activos`, donde cada descuento devuelve su `valor_descuento_calculado` sobre la tarifa base.

## Migración de base de datos

Si ya existe una base de datos creada con el esquema anterior, ejecuta una migración para agregar `hotel_id` y renombrar el concepto de precio a `valor_base`.

Ejemplo SQL para PostgreSQL:

```sql
ALTER TABLE tarifas ADD COLUMN hotel_id VARCHAR(50) NOT NULL DEFAULT '';
ALTER TABLE tarifas RENAME COLUMN valor_noche TO valor_base;
```

Si el error indica que la relación `tarifas` no existe, primero crea las tablas del esquema actual dentro del contenedor de la app:

```bash
python -c "from main import app, db; ctx = app.app_context(); ctx.push(); db.create_all(); ctx.pop()"
```

## Testing

```bash
pytest tests/ -v
```

## Variables de Entorno

- `DATABASE_URL` - URL de conexión a base de datos
- `FLASK_ENV` - Entorno (development, testing, production)

## Docker

```bash
docker build -t tarifas-app .
docker run -p 3008:3008 tarifas-app
```
