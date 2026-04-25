# 🏨 TravelHub — Sistema de Reservas de Hospedajes

> **Proyecto Final — Maestría en Ingeniería de Software (MISO)**  
> Universidad de los Andes · Grupo 4

---

## 📋 Descripción General

**TravelHub** es un sistema backend basado en microservicios orientado a la gestión de reservas de hospedajes. El sistema permite a los usuarios buscar hospedajes disponibles según ciudad, capacidad y fechas, y verifica la disponibilidad en tiempo real consultando los servicios de inventario y reservas, con soporte de caché distribuida para optimizar el rendimiento.

El backend está compuesto por **tres microservicios independientes**, desplegados sobre **Kubernetes (EKS)** en AWS, con infraestructura aprovisionada mediante **Terraform**.

---

## 👥 Equipo de Desarrollo

| Nombre | Rol |
|---|---|
| Neider Fajardo | Desarrollador |
| Juan Camilo Mora | Desarrollador |
| Daniel Andrade | Desarrollador |
| Daniel Oicata | Desarrollador |

---

## 🏗️ Arquitectura

El sistema está compuesto por tres microservicios que se comunican entre sí a través de HTTP. El microservicio de **Búsquedas** actúa como agregador (BFF), consultando a los otros dos servicios y retornando resultados unificados al cliente. Los resultados se almacenan en caché con **Redis (ElastiCache)** para reducir la latencia en búsquedas frecuentes.

```
Cliente
   │
   ▼
┌──────────────────────┐
│  busquedas-app       │  ←── API Gateway / Ingress NGINX
│  (Agregador / BFF)   │
└────────┬──────┬──────┘
         │      │
         ▼      ▼
┌─────────────┐  ┌─────────────┐
│inventario-  │  │  reserva-   │
│    app      │  │    app      │
│  (RDS/PG)   │  │  (RDS/PG)   │
└─────────────┘  └─────────────┘
         │
         ▼
     Redis Cache
    (ElastiCache)
```

### Infraestructura en AWS

| Componente | Servicio AWS |
|---|---|
| Contenedores | Amazon EKS (Kubernetes) |
| Base de datos | Amazon RDS (PostgreSQL) |
| Caché | Amazon ElastiCache (Redis) |
| Registro de imágenes | Amazon ECR |
| Redes / Tráfico | Ingress NGINX + Load Balancer |

---

## 📦 Microservicios

### 1. `busquedas_app` — Servicio de Búsquedas

Actúa como punto de entrada para las búsquedas de hospedajes. Agrega datos del servicio de inventario y reservas, aplica filtros de disponibilidad y utiliza Redis como caché de resultados.

**Endpoints:**

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/v1/busquedas/health` | Health check del servicio |
| `GET` | `/api/v1/busquedas/search` | Búsqueda de hospedajes disponibles |

**Parámetros de búsqueda (`/search`):**

| Parámetro | Tipo | Descripción |
|---|---|---|
| `ciudad` | `string` | Ciudad del hospedaje |
| `capacidad` | `int` | Número de personas |
| `check_in` | `date` | Fecha de entrada (`YYYY-MM-DD`) |
| `check_out` | `date` | Fecha de salida (`YYYY-MM-DD`) |

**Variables de entorno requeridas:**
- `INVENTARIOS_URL` — URL del microservicio de inventarios
- `RESERVAS_URL` — URL del microservicio de reservas
- `REDIS_HOST` — Host de Redis (ElastiCache)

---

### 2. `inventario_app` — Servicio de Inventario

Gestiona el catálogo de hospedajes y habitaciones. Permite filtrar habitaciones por ciudad y capacidad, y provee un endpoint para poblar la base de datos con datos de prueba.

**Endpoints:**

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/v1/inventarios/health` | Health check del servicio |
| `GET` | `/api/v1/inventarios/filtro` | Filtrar habitaciones por ciudad y capacidad |
| `POST` | `/api/v1/inventarios/seed` | Poblar BD con datos de prueba |

**Parámetros de filtro (`/filtro`):**

| Parámetro | Tipo | Descripción |
|---|---|---|
| `ciudad` | `string` | Ciudad del hospedaje |
| `capacidad` | `int` | Número de personas |

**Variables de entorno requeridas:**
- `DATABASE_URL` — URL de conexión a PostgreSQL

---

### 3. `reserva_app` — Servicio de Reservas

Gestiona el registro de reservas y verifica la disponibilidad de habitaciones en un rango de fechas dado.

**Endpoints:**

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/v1/reservas/health` | Health check del servicio |
| `POST` | `/api/v1/reservas/disponibilidad` | Verificar disponibilidad de habitaciones |
| `POST` | `/api/v1/reservas/crear` | Crear una reserva |
| `POST` | `/api/v1/reservas/seed/<cantidad>` | Generar reservas de prueba |

**Body de disponibilidad (`/disponibilidad`):**

```json
{
  "habitacion_ids": [1, 2, 3],
  "check_in": "2025-06-01",
  "check_out": "2025-06-05"
}
```

**Body de creación (`/crear`):**

```json
{
  "habitacion_id": "1ecf9ccf-fc58-4a44-95c9-b4dd8c5bf5b8",
  "check_in": "2026-05-10",
  "check_out": "2026-05-13",
  "user_id": "u1"
}
```

Campos del body:
- `habitacion_id` (string, requerido): UUID de la habitación.
- `check_in` (string, requerido): Fecha de entrada en formato `YYYY-MM-DD`.
- `check_out` (string, requerido): Fecha de salida en formato `YYYY-MM-DD`.
- `user_id` (string, opcional): Identificador del usuario que realiza la reserva.

**Respuesta exitosa de creación (`201 Created`):**

```json
{
  "msg": "Reserva creada correctamente",
  "reserva": {
    "id": "bd9f0966-e7c9-4cb6-9ab6-8cd444da0000",
    "public_id": "RSV-ABC12345",
    "habitacion_id": "1ecf9ccf-fc58-4a44-95c9-b4dd8c5bf5b8",
    "check_in": "2026-05-10",
    "check_out": "2026-05-13",
    "estado": "pendiente",
    "created_at": "2026-04-23T18:12:40",
    "updated_at": "2026-04-23T18:12:40",
    "fecha_creacion": "2026-04-23T18:12:40",
    "fecha_actualizacion": "2026-04-23T18:12:40"
  }
}
```

**Errores comunes de creación:**
- `400 Bad Request`: campos faltantes o fechas inválidas.
- `409 Conflict`: la habitación no está disponible para las fechas seleccionadas.
- `500 Internal Server Error`: error interno al crear la reserva.

**Variables de entorno requeridas:**
- `DATABASE_URL` — URL de conexión a PostgreSQL

---

## 🛠️ Stack Tecnológico

| Tecnología | Uso |
|---|---|
| Python + Flask | Framework de los microservicios |
| Flask-RESTful | Construcción de APIs REST |
| SQLAlchemy | ORM para acceso a base de datos |
| PostgreSQL (RDS) | Base de datos relacional |
| Redis (ElastiCache) | Caché distribuida |
| Docker | Contenerización de servicios |
| Kubernetes (EKS) | Orquestación de contenedores |
| Terraform | Infraestructura como código (IaC) |
| Amazon ECR | Registro de imágenes Docker |
| NGINX Ingress | Enrutamiento HTTP en Kubernetes |

---

## 🚀 Despliegue

El proyecto usa un `makefile` con targets para automatizar todo el ciclo de vida del despliegue.

### Requisitos previos

- AWS CLI configurado con credenciales válidas
- Docker instalado y corriendo
- `kubectl` instalado
- `terraform` instalado
- `helm` instalado

### Flujo completo de despliegue

```bash
# 1. Aprovisionar toda la infraestructura en AWS
make infra

# 2. Autenticarse en ECR, construir y subir las imágenes Docker
make images

# 3. Instalar Ingress NGINX en el clúster
make ingress

# O ejecutar todo de una vez
make deploy
```

### Targets disponibles en el Makefile

| Target | Descripción |
|---|---|
| `make ecr` | Crear repositorios en ECR |
| `make rds` | Aprovisionar base de datos RDS |
| `make eks` | Crear clúster EKS y configurar `kubectl` |
| `make elasticache` | Aprovisionar Redis en ElastiCache |
| `make ingress` | Instalar NGINX Ingress Controller |
| `make images` | Login ECR + build + push de imágenes |
| `make deploy` | Despliegue completo (infra + images + ingress) |
| `make destroy` | Destruir toda la infraestructura |

### Despliegue de manifiestos Kubernetes

Los manifiestos se encuentran en el directorio `k8s/`:

```bash
kubectl apply -f k8s/inventario-deployment.yaml
kubectl apply -f k8s/inventario-services.yaml
kubectl apply -f k8s/reservas-deployment.yaml
kubectl apply -f k8s/reservas-services.yaml
kubectl apply -f k8s/busquedas-deployment.yaml
kubectl apply -f k8s/busquedas-services.yaml
kubectl apply -f k8s/gateway-ingress.yaml
```

---

## 📁 Estructura del Repositorio

```
TravelHub-ProyectoFinal/
├── busquedas_app/          # Microservicio de Búsquedas (BFF + caché)
│   ├── app/
│   │   ├── api/            # Endpoints REST
│   │   └── utils/          # Helpers: inventario, reservas, caché
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── inventario_app/         # Microservicio de Inventario
│   ├── app/
│   │   ├── api/            # Endpoints REST
│   │   ├── db/             # Modelos de base de datos
│   │   ├── services/       # Lógica de negocio (CRUD)
│   │   └── utils/          # Helpers: seed
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── reserva_app/            # Microservicio de Reservas
│   ├── app/
│   │   ├── api/            # Endpoints REST
│   │   ├── db/             # Modelos de base de datos
│   │   ├── services/       # Lógica de negocio (CRUD)
│   │   └── utils/          # Helpers: seed
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── k8s/                    # Manifiestos de Kubernetes
│   ├── busquedas-deployment.yaml
│   ├── busquedas-services.yaml
│   ├── inventario-deployment.yaml
│   ├── inventario-services.yaml
│   ├── reservas-deployment.yaml
│   ├── reservas-services.yaml
│   └── gateway-ingress.yaml
├── terraform/              # Infraestructura como código
│   ├── stacks/             # ECR, EKS, RDS, ElastiCache
│   ├── modules/
│   └── environments/
├── experimentos/           # Experimentos de rendimiento
├── experimento-II/
└── makefile                # Automatización de despliegue
```

---

## 🌐 Región AWS

El proyecto está configurado para desplegarse en la región **`us-east-1`** (N. Virginia).

---

*Proyecto desarrollado para el curso de Proyecto Final — MISO · Universidad de los Andes*