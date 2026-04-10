import requests
import secrets
from typing import Optional, Dict, Tuple

# URL base del servicio de autenticación
AUTH_SERVICE_URL = "http://127.0.0.1:5000/api/v1/auth"

class AsyncUserService:
    """
    Servicio asincrónico para crear usuarios en autenticadorapp
    desde proveedoresapp
    """

    @staticmethod
    def create_user_in_auth_service(
        email: str,
        first_name: str,
        last_name: str,
        role: str = "Manager"
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Crea un usuario en el servicio de autenticación (autenticadorapp)
        
        Args:
            email (str): Email del usuario
            first_name (str): Nombre del usuario
            last_name (str): Apellido del usuario
            role (str): Rol del usuario (default: Manager)
        
        Returns:
            Tuple[Optional[Dict], Optional[str]]: 
                - Tuple (user_data, None) si es exitoso
                - Tuple (None, error_message) si hay error
        
        Ejemplo:
            user_data, error = AsyncUserService.create_user_in_auth_service(
                email="manager@example.com",
                first_name="Juan",
                last_name="Pérez"
            )
            if error:
                print(f"Error: {error}")
            else:
                user_id = user_data["id"]
        """
        try:
            # Generar una contraseña temporal segura
            temporary_password = secrets.token_urlsafe(16)
            
            # Preparar el payload
            payload = {
                "email": email,
                "password": temporary_password,
                "role": role,
                "first_name": first_name,
                "last_name": last_name
            }
            
            # Hacer la petición POST a autenticadorapp
            response = requests.post(
                f"{AUTH_SERVICE_URL}/users",
                json=payload,
                timeout=10
            )
            
            # Verificar el status code
            if response.status_code == 201:
                # Usuario creado exitosamente
                user_data = response.json()
                return user_data, None
            
            elif response.status_code == 409:
                # Usuario duplicado
                error_msg = "El email ya está registrado en el servicio de autenticación"
                return None, error_msg
            
            elif response.status_code == 400:
                # Datos inválidos
                error_data = response.json()
                error_msg = error_data.get("message", "Datos inválidos enviados a autenticación")
                return None, error_msg
            
            else:
                # Otro error
                error_msg = f"Error en autenticadorapp: {response.status_code} - {response.text}"
                return None, error_msg
        
        except requests.exceptions.Timeout:
            error_msg = "Timeout: El servicio de autenticación no respondió a tiempo"
            return None, error_msg
        
        except requests.exceptions.ConnectionError:
            error_msg = "Error de conexión: No se pudo conectar con el servicio de autenticación. Verifica que autenticadorapp esté corriendo en puerto 5000"
            return None, error_msg
        
        except Exception as e:
            error_msg = f"Error inesperado al crear usuario: {str(e)}"
            return None, error_msg

    @staticmethod
    def validate_user_creation_data(
        email: str,
        first_name: str,
        last_name: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Valida los datos antes de crear un usuario
        
        Args:
            email (str): Email del usuario
            first_name (str): Nombre del usuario
            last_name (str): Apellido del usuario
        
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if not email or "@" not in email:
            return False, "Email inválido"
        
        if not first_name or len(first_name.strip()) == 0:
            return False, "El nombre es requerido"
        
        if not last_name or len(last_name.strip()) == 0:
            return False, "El apellido es requerido"
        
        return True, None
