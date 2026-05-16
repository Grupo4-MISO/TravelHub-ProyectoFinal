# Docker Compose - Inventario App con PostgreSQL

Este archivo `docker-compose.yml` levanta dos servicios:
1. **PostgreSQL 16** - Base de datos principal
2. **inventario_app** - Aplicación Flask

## Requisitos

- Docker Desktop instalado
- Docker Compose (incluido en Docker Desktop)

## Instrucciones para levantar localmente

### 1. Desde el directorio `inventario_app`:

```bash
cd inventario_app
```

### 2. Construir e iniciar los contenedores:

```bash
docker-compose up --build
```

Esto:
- Construirá la imagen Docker de la aplicación
- Levantará PostgreSQL en puerto 5432
- Levantará la aplicación Flask en puerto 3000
- Creará volúmenes persistentes para la BD

### 3. Acceder a la aplicación:

- **API**: http://localhost:3000
- **Swagger Docs**: http://localhost:3000/swagger/

### 4. Para ver los logs:

```bash
docker-compose logs -f inventario_app
```

## Configuración de Base de Datos

Las credenciales por defecto en el docker-compose son:

- **Usuario**: `travelhub_user`
- **Contraseña**: `travelhub_password`
- **Base de datos**: `inventario_db`
- **Host**: `postgres` (dentro de la red Docker)
- **Puerto**: `5432`

## Conectarse a PostgreSQL desde fuera del contenedor

Si quieres conectarte con un cliente SQL (pgAdmin, DBeaver, etc):

```
Host: localhost
Port: 5432
User: travelhub_user
Password: travelhub_password
Database: inventario_db
```

## Detener y limpiar

### Detener los contenedores:

```bash
docker-compose down
```

### Detener y eliminar volúmenes (borra datos):

```bash
docker-compose down -v
```

## Desarrollo

- Los archivos locales están sincronizados con el contenedor (`volumes: - .:/app`)
- Los cambios en Python se recargarán automáticamente (Flask development mode)
- Para instalar nuevas dependencias, edita `requirements.txt` y reconstruye:

```bash
docker-compose build
docker-compose up
```

## Troubleshooting

### Puerto ya en uso

Si el puerto 3000 o 5432 ya está en uso, edita el `docker-compose.yml` y cambia los puertos:

```yaml
ports:
  - "3001:3000"  # Cambia 3001 por otro puerto disponible
```

### Base de datos no responde

Verifica que el contenedor de Postgres esté sano:

```bash
docker-compose ps
docker-compose logs postgres
```

### Eliminar contenedores dañados

```bash
docker-compose down -v
docker system prune -a
docker-compose up --build
```

## Variables de entorno personalizadas

Copia `.env.example` a `.env` y modifica según sea necesario:

```bash
cp .env.example .env
```

Luego edita `.env` con tus valores personalizados.
