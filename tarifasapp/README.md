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
- `POST /seed` - Poblar base de datos con datos de ejemplo
- `GET /swagger/` - Documentación interactiva

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
