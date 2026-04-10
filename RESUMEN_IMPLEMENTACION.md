# Resumen: Función Asincrónica de Creación de Usuarios

## ✅ Implementación Completada

Se ha construido exitosamente una función asincrónica que permite crear Usuarios en `autenticadorapp` desde `proveedoresapp`, integrando ambos servicios de forma transparente.

---

## 📋 Archivos Creados/Modificados

### 1. **Nuevo Servicio Asincrónico**
- **Archivo**: `proveedoresapp/app/services/async_user_service.py`
- **Descripción**: Módulo que encapsula la lógica de comunicación con autenticadorapp
- **Funciones principales**:
  - `create_user_in_auth_service()` - Crea usuario en autenticadorapp
  - `validate_user_creation_data()` - Valida datos antes de enviar

### 2. **API Actualizada**
- **Archivo**: `proveedoresapp/app/api/api.py`
- **Cambios**:
  - Importado `AsyncUserService`
  - Modificado endpoint POST `/api/v1/Managers` para usar la función asincrónica
  - Ahora recibe: `email`, `first_name`, `last_name`, `hospedajeId`
  - Devuelve: Manager + datos del usuario creado en autenticadorapp

### 3. **Documentación**
- `ASYNC_USER_CREATION_GUIDE.md` - Guía completa de uso con ejemplos
- `ASYNC_USER_SERVICE_TECH_DOCS.md` - Documentación técnica detallada
- `test_async_user_creation.py` - Script de testing

---

## 🔄 Flujo de Ejecución

```
Cliente POST /api/v1/Managers en proveedoresapp:5005
    ↓
[1] Validación de datos (email, nombres)
    ↓
[2] Llamada a async_user_service.create_user_in_auth_service()
    ↓
[3] HTTP POST a autenticadorapp:5000/api/v1/auth/users
    ├─ Email
    ├─ Password (generada automáticamente)
    ├─ Role: "Manager"
    ├─ First Name
    └─ Last Name
    ↓
[4] Usuario creado en autenticadorapp
    └─ Devuelve: userId, username, email
    ↓
[5] Crear Manager en proveedoresapp con userId devuelto
    ↓
[6] Response 201 con Manager + User Data
```

---

## 🧪 Tests Ejecutados

Todos los tests pasaron correctamente:

✅ **Test 1**: Crear Usuario Administrador  
✅ **Test 2**: Login y Obtener Token JWT  
✅ **Test 3**: Crear Manager (con Usuario Asincrónico)  
✅ **Test 4**: Obtener Manager Creado  
✅ **Test 5**: Error - Email Duplicado (manejo correcto)  

---

## 📊 Ejemplo de Request/Response

### Request: POST /api/v1/Managers

```bash
curl -X POST http://127.0.0.1:5005/api/v1/Managers \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "hospedajeId": "7e8b59cd-d1a1-4c1c-bcd4-5211584d23f0",
    "email": "manager@hotel.com",
    "first_name": "Juan",
    "last_name": "Pérez"
  }'
```

### Response: 201 Created

```json
{
  "message": "Manager y usuario creados exitosamente",
  "manager": {
    "id": "f9527557-af4c-4a82-9ef3-79001fded477",
    "hospedajeId": "7e8b59cd-d1a1-4c1c-bcd4-5211584d23f0",
    "userId": "ec026a3a-5adb-4add-bb91-63c4e35130b4",
    "userName": "manager",
    "email": "manager@hotel.com",
    "first_name": "Juan",
    "last_name": "Pérez",
    "created_at": "2026-04-10T00:34:19.630570",
    "updated_at": "2026-04-10T00:34:19.630573"
  },
  "user": {
    "id": "ec026a3a-5adb-4add-bb91-63c4e35130b4",
    "username": "manager",
    "email": "manager@hotel.com"
  }
}
```

---

## 🔐 Características de Seguridad

1. **Contraseña Temporal**: Se genera automáticamente una contraseña segura
   - Ejemplo: `FvV_7m-kQ_VWxJ9Y8Z1-MQ`
   - El usuario debe cambiarla en primer login

2. **Validación Pre-envío**: Los datos se validan ANTES de hacer la petición

3. **Manejo de Errores**: 
   - Captura excepciones de red
   - Manejo de timeouts
   - Detección de duplicados
   - Mensajes de error descriptivos

4. **Username Generado**: Se deriva automáticamente del email
   - `manager@hotel.com` → `manager`

---

## ⚠️ Manejo de Errores

| Error | Status | Mensaje |
|-------|--------|---------|
| Email duplicado | 409 | "El email ya está registrado en el servicio de autenticación" |
| Datos inválidos | 400 | "Faltan campos requeridos: ..." |
| Conexión fallida | 500 | "Error de conexión: No se pudo conectar..." |
| Timeout | 500 | "Timeout: El servicio de autenticación no respondió..." |

---

## 🚀 Cómo Usar

### 1. Verificar que ambos servicios estén corriendo:

```bash
# Terminal 1: autenticadorapp
cd autenticadorapp
python main.py  # Puerto 5000

# Terminal 2: proveedoresapp
cd proveedoresapp
python main.py  # Puerto 5005
```

### 2. Ejecutar los tests:

```bash
python test_async_user_creation.py
```

### 3. Usar vía API:

```python
import requests

token = "tu_token_jwt"
headers = {"Authorization": f"Bearer {token}"}

response = requests.post(
    "http://127.0.0.1:5005/api/v1/Managers",
    json={
        "hospedajeId": "uuid-aqui",
        "email": "nuevo@manager.com",
        "first_name": "Nombre",
        "last_name": "Apellido"
    },
    headers=headers
)

if response.status_code == 201:
    data = response.json()
    print(f"Manager ID: {data['manager']['id']}")
    print(f"User ID: {data['user']['id']}")
```

---

## 📦 Dependencias Utilizadas

- `requests==2.32.3` - HTTP requests (ya incluido en requirements.txt)
- `secrets` - Generación segura de contraseñas (built-in Python)
- `typing` - Type hints (built-in Python)

---

## 🔧 Configuración

### URLs Configuradas

```python
AUTH_SERVICE_URL = "http://127.0.0.1:5000/api/v1/auth"
AUTH_SERVICE_TIMEOUT = 10  # segundos
```

Se pueden modificar en `async_user_service.py` si es necesario.

---

## 📚 Documentación Adicional

- **Guía de Uso**: [ASYNC_USER_CREATION_GUIDE.md](ASYNC_USER_CREATION_GUIDE.md)
- **Documentación Técnica**: [ASYNC_USER_SERVICE_TECH_DOCS.md](ASYNC_USER_SERVICE_TECH_DOCS.md)
- **Script de Testing**: [test_async_user_creation.py](test_async_user_creation.py)

---

## ✨ Mejoras Futuras Opcionales

1. Implementar reintentos automáticos en caso de fallo
2. Agregar logging detallado
3. Implementar async/await con asyncio para mejor rendimiento
4. Rate limiting para prevenir abuso
5. Caché de validaciones

---

## 📝 Notas Importantes

- La contraseña temporal se genera en autenticadorapp y NO se devuelve en la respuesta por seguridad
- El user debe cambiar la contraseña en su primer login
- El flujo es **transaccional**: si falla la creación del usuario, no se crea el Manager
- Todos los servicios deben estar corriendo para que funcione el flujo completo
