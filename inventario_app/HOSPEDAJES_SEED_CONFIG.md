# Configuración de HOSPEDAJES_SEED

## Descripción

Los datos de hospedajes (hoteles) se gestionan mediante un archivo JSON externo que es cargado dinámicamente por el módulo `seedHelper`.

## Estructura de Archivos

```
inventario_app/
├── app/
│   ├── data/
│   │   └── hospedajes_seed.json          ← Datos de hospedajes en formato JSON
│   ├── utils/
│   │   └── seedHelper.py                 ← Cargador de datos (inicialización)
│   └── ...
└── ...
```

## Archivo JSON: hospedajes_seed.json

**Ubicación**: `inventario_app/app/data/hospedajes_seed.json`

El archivo contiene un array JSON con todos los hospedajes representativos de Colombia, distribuidos en 9 ciudades:
- Bogota (7 hoteles)
- Medellin (7 hoteles)
- Cartagena (7 hoteles)
- Cali (7 hoteles)
- Santa Marta (7 hoteles)
- Barranquilla (7 hoteles)
- San Andres (7 hoteles)
- Manizales (7 hoteles)
- Villa de Leyva (7 hoteles)

**Total**: 63 hospedajes

### Estructura de cada hospedaje

```json
{
    "id": "UUID-string",
    "nombre": "Nombre del hotel",
    "pais": "Colombia",
    "countryCode": "CO",
    "ciudad": "Nombre ciudad",
    "direccion": "Dirección completa",
    "rating": 4.5,
    "reviews": 1000,
    "habitaciones": [
        {
            "id": "UUID-string",
            "code": "101",
            "descripcion": "Tipo de habitación",
            "capacidad": 2,
            "precio": 380000.0
        }
    ]
}
```

## Integración con seedHelper

El archivo `seedHelper.py` contiene la función `_load_hospedajes_seed()` que:

1. **Localiza el archivo JSON** usando rutas relativas
2. **Carga el contenido** con UTF-8 encoding
3. **Parsea el JSON** en una lista de diccionarios
4. **Maneja errores** con excepciones informativas

### Uso

```python
from app.utils.seedHelper import HOSPEDAJES_SEED

# HOSPEDAJES_SEED está disponible globalmente después de importar
for hospedaje in HOSPEDAJES_SEED:
    print(hospedaje['nombre'], hospedaje['ciudad'])
```

## Proceso de Seed

Cuando se ejecuta `SeedHelper.reset_and_seed()`:

1. Se cargan los datos de `HOSPEDAJES_SEED` (desde el JSON)
2. Se itera sobre cada hospedaje
3. Se crea un registro `HospedajeORM` en la BD
4. Se crean registros de `HabitacionORM` para cada habitación
5. Se asignan amenidades aleatorias (3-7 por hospedaje)

## Ventajas de esta Arquitectura

✅ **Separación de responsabilidades**: Datos en JSON, lógica en Python
✅ **Mantenibilidad**: Editar datos sin tocar código
✅ **Versionado**: Cambios fáciles de trackear en Git
✅ **Escalabilidad**: Fácil agregar nuevos hospedajes
✅ **Reutilizable**: El JSON puede usarse en otros contextos (APIs, etc)

## Cómo Modificar los Datos

### Para agregar un nuevo hospedaje:

1. Abra `hospedajes_seed.json`
2. Agregue un nuevo objeto al array con estructura válida
3. Asegúrese de UUIDs únicos
4. Guarde el archivo
5. Ejecute `SeedHelper.reset_and_seed()` en la aplicación

### Validar JSON:

```python
import json

# Validar sintaxis del JSON
with open('app/data/hospedajes_seed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    print(f"Total hospedajes cargados: {len(data)}")
```

## Manejo de Errores

Si hay errores al cargar el JSON, se lanzarán excepciones informativas:

- **FileNotFoundError**: El archivo JSON no existe en la ruta esperada
- **JSONDecodeError**: El archivo JSON tiene sintaxis inválida

```python
try:
    hospedajes = HOSPEDAJES_SEED
except FileNotFoundError as e:
    print(f"Error: {e}")
except ValueError as e:
    print(f"Error en JSON: {e}")
```

## Símbolo de Referencia

En el código, busque: **`#sym:HOSPEDAJES_SEED`**

Este símbolo marca el punto donde se carga la variable global HOSPEDAJES_SEED.
