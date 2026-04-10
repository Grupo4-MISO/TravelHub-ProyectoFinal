# Documentación Técnica: Servicio Asincrónico de Creación de Usuarios

## Descripción

El módulo `AsyncUserService` proporciona funcionalidad para crear usuarios en el servicio `autenticadorapp` de forma asincrónica desde `proveedoresapp`. Esto permite una integración transparente entre los servicios de autenticación y gestión de proveedores.

## Archivo: `app/services/async_user_service.py`

### Clase: `AsyncUserService`

Servicio estático que contiene métodos para interactuar con el servicio de autenticación.

#### Método: `create_user_in_auth_service()`

```python
@staticmethod
def create_user_in_auth_service(
    email: str,
    first_name: str,
    last_name: str,
    role: str = "Manager"
) -> Tuple[Optional[Dict], Optional[str]]
```

**Descripción**: Crea un usuario en `autenticadorapp` haciendo una petición HTTP POST.

**Parámetros**:
- `email` (str): Email del usuario (requerido)
- `first_name` (str): Nombre del usuario (requerido)
- `last_name` (str): Apellido del usuario (requerido)
- `role` (str): Rol del usuario, por defecto "Manager". Roles válidos: "Administrator", "Traveler", "Manager"

**Retorno**:
- `Tuple[Optional[Dict], Optional[str]]`: Un tuple con:
  - Si exitoso: `(user_data_dict, None)`
  - Si error: `(None, error_message_string)`

**Datos devueltos en caso de éxito**:
```python
{
    "id": "uuid-del-usuario",
    "username": "email_base",  # Derivado del email
    "email": "usuario@example.com"
}
```

**Manejo de Errores**:
- **409 - Usuario duplicado**: Devuelve mensaje sobre email duplicado
- **400 - Datos inválidos**: Devuelve mensaje sobre datos inválidos
- **Connection Error**: Devuelve mensaje sobre falta de conexión
- **Timeout**: Devuelve mensaje sobre timeout (10 segundos)
- **Otros errores**: Devuelve mensaje genérico de error

**Flujo Interno**:
1. Genera una contraseña temporal segura con `secrets.token_urlsafe(16)`
2. Prepara el payload con los datos del usuario
3. Hace POST a `http://127.0.0.1:5000/api/v1/auth/users`
4. Evalúa el status code y retorna datos o error
5. Captura excepciones de red/timeout

#### Método: `validate_user_creation_data()`

```python
@staticmethod
def validate_user_creation_data(
    email: str,
    first_name: str,
    last_name: str
) -> Tuple[bool, Optional[str]]
```

**Descripción**: Valida los datos antes de hacer la petición a autenticadorapp.

**Parámetros**:
- `email` (str): Email a validar
- `first_name` (str): Nombre a validar
- `last_name` (str): Apellido a validar

**Retorno**:
- `Tuple[bool, Optional[str]]`:
  - Si válido: `(True, None)`
  - Si no válido: `(False, error_message)`

**Validaciones**:
- Email contiene "@"
- Name y last_name no están vacíos

## Integración en API

### Uso en `api.py` - Endpoint POST `/api/v1/Managers`

```python
from app.services.async_user_service import AsyncUserService

class ManagerResource(Resource):
    @token_required
    def post(current_user, self):
        payload = request.get_json()
        
        # 1. Validar datos
        is_valid, error = AsyncUserService.validate_user_creation_data(
            email=payload.get("email"),
            first_name=payload.get("first_name"),
            last_name=payload.get("last_name")
        )
        if not is_valid:
            return {"message": error}, 400
        
        # 2. Crear usuario en autenticadorapp
        user_data, user_error = AsyncUserService.create_user_in_auth_service(
            email=payload.get("email"),
            first_name=payload.get("first_name"),
            last_name=payload.get("last_name"),
            role="Manager"
        )
        
        if user_error:
            return {"message": user_error}, 409 or 500
        
        # 3. Crear Manager con userId devuelto
        manager_payload = {
            "hospedajeId": payload.get("hospedajeId"),
            "userId": user_data["id"],
            "userName": user_data["username"],
            "email": user_data["email"],
            "first_name": payload.get("first_name"),
            "last_name": payload.get("last_name")
        }
        
        manager = manager_crud.create_manager(manager_payload)
        return {"manager": manager, "user": user_data}, 201
```

## Flujo Completo

```
POST /api/v1/Managers (en proveedoresapp:5005)
    ↓
AsyncUserService.validate_user_creation_data()
    ↓ (si válido)
AsyncUserService.create_user_in_auth_service()
    ↓
POST /api/v1/auth/users (a autenticadorapp:5000)
    ↓
Usuario creado en autenticadorapp
    ↓ (devuelve userId)
manager_crud.create_manager()
    ↓
Manager creado con userId
    ↓
Response 201 + manager + user data
```

## Configuración

### Variables de Entorno (recomendado)

Se puede agregar en `.env`:

```
AUTH_SERVICE_URL=http://127.0.0.1:5000/api/v1/auth
AUTH_SERVICE_TIMEOUT=10
```

Y modificar el archivo para usarlas:

```python
import os

AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://127.0.0.1:5000/api/v1/auth')
AUTH_SERVICE_TIMEOUT = int(os.getenv('AUTH_SERVICE_TIMEOUT', '10'))
```

## Seguridad

### Contraseña Temporal

- Se genera automáticamente con `secrets.token_urlsafe(16)`
- Ejemplo: `FvV_7m-kQ_VWxJ9Y8Z1-MQ`
- El usuario debe cambiarla en su primer login

### Validación

- Los datos se validan ANTES de hacer la petición
- Se capturan todas las excepciones de red
- No se exponen detalles internos del servidor

## Testing

Ejemplo de test unitario:

```python
import pytest
from app.services.async_user_service import AsyncUserService

def test_create_user_successful(requests_mock):
    """Test creación de usuario exitosa"""
    mock_response = {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "username": "juan",
        "email": "juan@example.com"
    }
    
    requests_mock.post(
        'http://127.0.0.1:5000/api/v1/auth/users',
        json=mock_response,
        status_code=201
    )
    
    user_data, error = AsyncUserService.create_user_in_auth_service(
        email="juan@example.com",
        first_name="Juan",
        last_name="Pérez"
    )
    
    assert error is None
    assert user_data["id"] == "550e8400-e29b-41d4-a716-446655440000"

def test_validate_invalid_email():
    """Test validación de email inválido"""
    is_valid, error = AsyncUserService.validate_user_creation_data(
        email="invalid-email",
        first_name="Juan",
        last_name="Pérez"
    )
    
    assert not is_valid
    assert "Email inválido" in error
```

## Troubleshooting

### Error: "No se pudo conectar con el servicio de autenticación"

**Causa**: `autenticadorapp` no está corriendo o no está en puerto 5000

**Solución**:
```bash
cd autenticadorapp
python main.py
```

### Error: "Timeout: El servicio de autenticación no respondió a tiempo"

**Causa**: `autenticadorapp` tardó más de 10 segundos en responder

**Solución**: Aumentar timeout en `async_user_service.py` (línea con `timeout=10`)

### Error: "El email ya está registrado"

**Causa**: El email ya existe en `autenticadorapp`

**Solución**: El usuario debe usar otro email o recuperar acceso a la cuenta existente

## Mejoras Futuras

1. Implementar reintentos automáticos
2. Agregar caché para validaciones frecuentes
3. Implementar async/await con asyncio
4. Agregar métricas y logging
5. Rate limiting para prevenir abuso
