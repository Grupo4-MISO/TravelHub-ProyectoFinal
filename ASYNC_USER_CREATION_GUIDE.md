# Ejemplos de uso: Crear Manager con Usuario Asincrónico

## Flujo de Creación

Cuando haces un POST a `/api/v1/Managers`, ocurre lo siguiente:

1. **Validación**: Se validan los datos (email, first_name, last_name, hospedajeId)
2. **Creación de Usuario**: Se hace una llamada asincrónica a `autenticadorapp` para crear el usuario
3. **Creación de Manager**: Una vez creado el usuario, se crea el registro en `providers` con el userId devuelto
4. **Respuesta**: Se devuelve tanto el manager como los datos del usuario creado

## Primero: Obtener un Token

### Crear un usuario administrador en autenticadorapp:

```bash
curl -X POST http://127.0.0.1:5000/api/v1/auth/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@travelhub.com",
    "password": "admin123",
    "role": "Administrator",
    "first_name": "Admin",
    "last_name": "User"
  }'
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "admin",
  "email": "admin@travelhub.com"
}
```

### Login para obtener token:

```bash
curl -X POST http://127.0.0.1:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@travelhub.com",
    "password": "admin123"
  }'
```

Response:
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "admin",
    "role": "Administrator"
  }
}
```

## Crear un Manager con Usuario Asincrónico

### Con cURL:

```bash
curl -X POST http://127.0.0.1:5005/api/v1/Managers \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "hospedajeId": "550e8400-e29b-41d4-a716-446655440001",
    "email": "manager@hoteldelsol.com",
    "first_name": "Carlos",
    "last_name": "García"
  }'
```

Response (201 - Creado):
```json
{
  "message": "Manager y usuario creados exitosamente",
  "manager": {
    "id": "660e8400-e29b-41d4-a716-446655440002",
    "hospedajeId": "550e8400-e29b-41d4-a716-446655440001",
    "userId": "550e8400-e29b-41d4-a716-446655440003",
    "userName": "manager",
    "email": "manager@hoteldelsol.com",
    "first_name": "Carlos",
    "last_name": "García",
    "created_at": "2026-04-09T19:30:00",
    "updated_at": "2026-04-09T19:30:00"
  },
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440003",
    "username": "manager",
    "email": "manager@hoteldelsol.com"
  }
}
```

### Con Python:

```python
import requests

# Headers con token JWT
headers = {
    "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "Content-Type": "application/json"
}

# Datos del nuevo manager
manager_data = {
    "hospedajeId": "550e8400-e29b-41d4-a716-446655440001",
    "email": "manager@hoteldelsol.com",
    "first_name": "Carlos",
    "last_name": "García"
}

# POST al endpoint de managers
response = requests.post(
    "http://127.0.0.1:5005/api/v1/Managers",
    json=manager_data,
    headers=headers
)

if response.status_code == 201:
    result = response.json()
    print(f"✓ Manager creado: {result['manager']['id']}")
    print(f"✓ Usuario creado: {result['user']['id']}")
    print(f"Username generado: {result['user']['username']}")
    print(f"Contraseña temporal generada automáticamente en autenticadorapp")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

## Manejo de Errores

### Error: Campos faltantes

```json
{
  "message": "Faltan campos requeridos: email, first_name"
}
```

### Error: Email duplicado

```json
{
  "message": "El email ya está registrado en el servicio de autenticación"
}
```

### Error: autenticadorapp no disponible

```json
{
  "message": "Error de conexión: No se pudo conectar con el servicio de autenticación. Verifica que autenticadorapp esté corriendo en puerto 5000"
}
```

## Características de la Función Asincrónica

1. **Contraseña temporal**: Se genera automáticamente una contraseña segura
2. **Validación**: Se validan los datos antes de hacer la petición
3. **Username derivado**: Se genera automáticamente del email (ejemplo: manager@hoteldelsol.com → manager)
4. **Manejo de errores**: Captura y comunica errores de conexión, timeouts, duplicados, etc.
5. **Transacción atómica**: Si falla la creación del usuario, no se crea el Manager

## Archivo de Implementación

El servicio se encuentra en: `app/services/async_user_service.py`

Funciones principales:
- `AsyncUserService.create_user_in_auth_service()` - Crea el usuario en autenticadorapp
- `AsyncUserService.validate_user_creation_data()` - Valida los datos
