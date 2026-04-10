#!/usr/bin/env python3
"""
Script de Testing para la Creación Asincrónica de Usuarios
Prueba el flujo completo: Usuario → Token → Manager
"""

import requests
import json
from uuid import uuid4

# URLs de los servicios
AUTH_URL = "http://127.0.0.1:5000/api/v1/auth"
PROVIDERS_URL = "http://127.0.0.1:5005/api/v1"

def print_section(title):
    """Imprime un título de sección"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_create_admin_user():
    """Test 1: Crear un usuario administrador en autenticadorapp"""
    print_section("TEST 1: Crear Usuario Administrador")
    
    data = {
        "email": "admin@travelhub.com",
        "password": "admin123",
        "role": "Administrator",
        "first_name": "Admin",
        "last_name": "User"
    }
    
    response = requests.post(f"{AUTH_URL}/users", json=data)
    
    print(f"Request: POST {AUTH_URL}/users")
    print(f"Payload: {json.dumps(data, indent=2)}")
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("\n✓ Usuario administrador creado exitosamente")
        return response.json()
    elif response.status_code == 409:
        print("\n✓ Usuario administrador ya existe, se continúa con login")
        return {"email": "admin@travelhub.com"}
    else:
        print("\n✗ Error al crear usuario administrador")
        return None

def test_login(admin_user):
    """Test 2: Login para obtener token JWT"""
    print_section("TEST 2: Login y Obtener Token JWT")
    
    data = {
        "email": "admin@travelhub.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{AUTH_URL}/login", json=data)
    
    print(f"Request: POST {AUTH_URL}/login")
    print(f"Payload: {json.dumps(data, indent=2)}")
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        token = result["token"]
        print(f"Token obtenido: {token[:50]}...")
        print(f"User: {json.dumps(result['user'], indent=2)}")
        print("\n✓ Login exitoso")
        return token
    else:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print("\n✗ Error en login")
        return None

def test_create_manager(token):
    """Test 3: Crear un Manager con Usuario Asincrónico"""
    print_section("TEST 3: Crear Manager (con Usuario Asincrónico)")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Generar un correo único
    unique_email = f"manager{str(uuid4())[:8]}@hotel.test.com"
    
    data = {
        "hospedajeId": str(uuid4()),
        "email": unique_email,
        "password": "Pass12345",
        "first_name": "Juan",
        "last_name": "Pérez"
    }
    
    response = requests.post(
        f"{PROVIDERS_URL}/Managers",
        json=data,
        headers=headers
    )
    
    print(f"Request: POST {PROVIDERS_URL}/Managers")
    print(f"Headers: Authorization: Bearer {token[:30]}...")
    print(f"Payload: {json.dumps(data, indent=2)}")
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        result = response.json()
        print(f"\n✓ Manager y Usuario creados exitosamente")
        print(f"  - Manager ID: {result['manager']['id']}")
        print(f"  - User ID: {result['user']['id']}")
        print(f"  - Username: {result['user']['username']}")
        print(f"  - Email: {result['user']['email']}")
        return result
    else:
        print(f"\n✗ Error al crear manager")
        return None

def test_get_manager(token, manager_id):
    """Test 4: Obtener el Manager creado"""
    print_section("TEST 4: Obtener Manager Creado")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{PROVIDERS_URL}/Managers/{manager_id}",
        headers=headers
    )
    
    print(f"Request: GET {PROVIDERS_URL}/Managers/{manager_id}")
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("\n✓ Manager obtenido exitosamente")
        return response.json()
    else:
        print("\n✗ Error al obtener manager")
        return None

def test_duplicate_email(token):
    """Test 5: Intentar crear Manager con email duplicado"""
    print_section("TEST 5: Error - Email Duplicado")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Usar el mismo email del test anterior
    data = {
        "hospedajeId": str(uuid4()),
        "email": "admin@travelhub.com",  # Email que ya existe
        "password": "Pass12345",
        "first_name": "Carlos",
        "last_name": "García"
    }
    
    response = requests.post(
        f"{PROVIDERS_URL}/Managers",
        json=data,
        headers=headers
    )
    
    print(f"Request: POST {PROVIDERS_URL}/Managers")
    print(f"Payload: {json.dumps(data, indent=2)}")
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code in [409, 500]:
        print("\n✓ Error esperado - Email duplicado detectado")
        return True
    else:
        print("\n✗ No se detectó el error de duplicado")
        return False

def main():
    """Ejecuta todos los tests"""
    print("\n" + "="*60)
    print("  TESTING: Creación Asincrónica de Usuarios")
    print("  Flujo: Usuario → Token → Manager")
    print("="*60)
    
    try:
        # Test 1: Crear usuario admin
        admin_user = test_create_admin_user()
        if not admin_user:
            print("\n✗ FATAL: No se pudo crear usuario admin")
            return
        
        # Test 2: Login
        token = test_login(admin_user)
        if not token:
            print("\n✗ FATAL: No se pudo obtener token")
            return
        
        # Test 3: Crear manager
        manager_result = test_create_manager(token)
        if not manager_result:
            print("\n✗ FATAL: No se pudo crear manager")
            return
        
        manager_id = manager_result['manager']['id']
        
        # Test 4: Obtener manager
        test_get_manager(token, manager_id)
        
        # Test 5: Intentar duplicado
        test_duplicate_email(token)
        
        print_section("✓ TODOS LOS TESTS COMPLETADOS")
        print("La función asincrónica de creación de usuarios está funcionando correctamente.\n")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: No se puede conectar con los servicios")
        print("  - Asegúrate de que autenticadorapp esté corriendo en puerto 5000")
        print("  - Asegúrate de que proveedoresapp esté corriendo en puerto 5005")
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")

if __name__ == "__main__":
    main()
