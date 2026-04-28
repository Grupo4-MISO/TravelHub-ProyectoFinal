# TravelHub Gateway - Instrucciones de Arranque

Este documento contiene las instrucciones para levantar el gateway y todos los microservicios del proyecto TravelHub en una máquina local.

## Requisitos Previos

- Python 3.14+ (compatible con el proyecto)
- Virtual environment (`.venv`) ya configurado en el directorio raíz del proyecto
- Node.js (para `localtunnel` o `ngrok`, si quieres exponer públicamente)

## Problema Conocido: Python 3.14

El proyecto usa `pydantic==2.9.2` y `psycopg2-binary==2.9.10` que NO tienen wheels precompilados para Python 3.14.

**Solución:** Instalar versiones binarias compatibles:

```bash
cd d:\TRAVELHUB\BackEnd\TravelHub-ProyectoFinal
(& .\.venv\Scripts\Activate.ps1)
pip install "pydantic>=2.13" "psycopg2-binary>=2.9.12"
```

## Paso 1: Activar el Entorno Virtual

```bash
cd d:\TRAVELHUB\BackEnd\TravelHub-ProyectoFinal
(Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned)
(& .\.venv\Scripts\Activate.ps1)
```

## Paso 2: Instalar Dependencias Compatibles

```bash
pip install "pydantic>=2.13" "psycopg2-binary>=2.9.12"
```

## Paso 3: Levantar todos los Microservicios

Abre **8 terminales nuevas** (una por servicio) en la carpeta raíz del proyecto, activa el entorno virtual en cada una, y ejecuta:

### Terminal 1 - inventario_app (Puerto 3000)
```bash
(& .\.venv\Scripts\python.exe) inventario_app\main.py
```

### Terminal 2 - reserva_app (Puerto 3001)
```bash
(& .\.venv\Scripts\python.exe) reserva_app\main.py
```

### Terminal 3 - busquedas_app (Puerto 3002)
```bash
(& .\.venv\Scripts\python.exe) busquedas_app\main.py
```

### Terminal 4 - comentariosapp (Puerto 3003)
```bash
(& .\.venv\Scripts\python.exe) comentariosapp\main.py
```

### Terminal 5 - autenticadorapp (Puerto 3004)
```bash
(& .\.venv\Scripts\python.exe) autenticadorapp\main.py
```

### Terminal 6 - transaccionesapp (Puerto 3005)
```bash
(& .\.venv\Scripts\python.exe) transaccionesapp\main.py
```

### Terminal 7 - proveedoresapp (Puerto 3006)
```bash
(& .\.venv\Scripts\python.exe) proveedoresapp\main.py
```

### Terminal 8 - clientesapp (Puerto 3007)
```bash
(& .\.venv\Scripts\python.exe) clientesapp\main.py
```

## Paso 4: Levantar el Gateway

En una **terminal adicional** (Terminal 9), ejecuta:

```bash
(& .\.venv\Scripts\python.exe) gatewayapp\main.py
```

El gateway estará disponible en: **http://127.0.0.1:3010**

Documentación Swagger: **http://127.0.0.1:3010/swagger/**

## Paso 5: Verificar que Todos los Servicios Estén Corriendo

Ejecuta en PowerShell para verificar los puertos abiertos:

```powershell
3000..3010 | ForEach-Object { 
    $p = $_
    $ok = (Test-NetConnection -ComputerName 127.0.0.1 -Port $p -InformationLevel Quiet)
    Write-Output "Puerto $p = $ok"
}
```

**Resultado esperado:**
```
Puerto 3000 = True
Puerto 3001 = True
Puerto 3002 = True
Puerto 3003 = True
Puerto 3004 = True
Puerto 3005 = True
Puerto 3006 = True
Puerto 3007 = True
Puerto 3010 = True
```

## Paso 6: Exponer el Gateway Públicamente (Opcional)

### Opción A: Usar localtunnel

```bash
npm install -g localtunnel
lt --port 3010
```

**Nota:** Si obtienes error de conexión rechazada, es un problema de firewall del servidor de localtunnel.

### Opción B: Usar ngrok

```bash
ngrok http 3010
```

## Estructura de Puertos

| Servicio | Puerto | URL |
|----------|--------|-----|
| Gateway | 3010 | http://127.0.0.1:3010 |
| inventario_app | 3000 | http://127.0.0.1:3000 |
| reserva_app | 3001 | http://127.0.0.1:3001 |
| busquedas_app | 3002 | http://127.0.0.1:3002 |
| comentariosapp | 3003 | http://127.0.0.1:3003 |
| autenticadorapp | 3004 | http://127.0.0.1:3004 |
| transaccionesapp | 3005 | http://127.0.0.1:3005 |
| proveedoresapp | 3006 | http://127.0.0.1:3006 |
| clientesapp | 3007 | http://127.0.0.1:3007 |

## Endpoint Importante del Gateway

**POST** `/api/v1/Gateway/start-services`

Inicia automáticamente todos los microservicios (si están disponibles en sus rutas). Útil si quieres automatizar el arranque en producción.

**Health Check:**

**GET** `/api/v1/Gateway/health`

Verifica que el gateway esté funcionando correctamente.

## Troubleshooting

### Error: `ModuleNotFoundError: No module named 'pydantic'`

Asegúrate de:
1. Haber activado `.venv`
2. Haber instalado `pip install "pydantic>=2.13"`
3. Usar `(& .\.venv\Scripts\python.exe)` explícitamente al ejecutar los servicios

### Error: `Address already in use` (Puerto ocupado)

Algún servicio ya está corriendo en ese puerto. Libéralo:

```powershell
# Encuentra el proceso en el puerto (ej: 3000)
Get-NetTCPConnection -LocalPort 3000 | Select-Object -ExpandProperty OwningProcess | Get-Process | Stop-Process -Force
```

### Error de conexión en localtunnel

El servidor de localtunnel puede estar caído o bloqueado por firewall. Intenta con `ngrok` como alternativa.

## Notas de Desarrollo

- Todos los servicios corren en **debug mode** con Flask (desarrollo)
- Los cambios en código se recargan automáticamente (autoreload)
- Para usar en **producción**, reemplaza Flask con `gunicorn` (ya incluido en `requirements.txt`)
