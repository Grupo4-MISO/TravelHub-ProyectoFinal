from flask_restful import Resource
from flask import request
import requests
import subprocess
import os
import sys

from app.utils.token_helper import token_required, roles_required

INVENTARIO_BASE = "http://127.0.0.1:3000"
BUSQUEDAS_BASE = "http://127.0.0.1:3002"
RESERVA_BASE = "http://127.0.0.1:3001"
AUTH_BASE = "http://127.0.0.1:3004"
CLIENTES_BASE = "http://127.0.0.1:3007"
COMENTARIOS_BASE = "http://127.0.0.1:3003"
TRANSACCIONES_BASE = "http://127.0.0.1:3005"
PROVEEDORES_BASE = "http://127.0.0.1:3006"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Health(Resource):
    def get(self):
        return {'status': 'healthy'}, 200


class InventarioProxy(Resource):
    def _build_url(self, path):
        return f"{INVENTARIO_BASE}/api/v1/inventarios/{path}"

    def get(self, path):
        try:
            url = self._build_url(path)
            params = request.args.to_dict()
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.get(url, params=params, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy get: {str(e)}"}, 500

    def post(self, path):
        try:
            url = self._build_url(path)
            data = request.get_json() or {}
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.post(url, json=data, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy post: {str(e)}"}, 500

    def put(self, path):
        try:
            url = self._build_url(path)
            data = request.get_json() or {}
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.put(url, json=data, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy put: {str(e)}"}, 500

    def delete(self, path):
        try:
            url = self._build_url(path)
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.delete(url, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy delete: {str(e)}"}, 500


class BusquedasProxy(Resource):
    def _build_url(self, path):
        return f"{BUSQUEDAS_BASE}/api/v1/busquedas/{path}"

    def get(self, path):
        try:
            url = self._build_url(path)
            params = request.args.to_dict()
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.get(url, params=params, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy get: {str(e)}"}, 500

    def post(self, path):
        try:
            url = self._build_url(path)
            data = request.get_json() or {}
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.post(url, json=data, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy post: {str(e)}"}, 500

    def put(self, path):
        try:
            url = self._build_url(path)
            data = request.get_json() or {}
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.put(url, json=data, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy put: {str(e)}"}, 500

    def delete(self, path):
        try:
            url = self._build_url(path)
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.delete(url, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy delete: {str(e)}"}, 500


class ReservaProxy(Resource):
    def _build_url(self, path):
        return f"{RESERVA_BASE}/api/v1/reservas/{path}"

    def get(self, path):
        try:
            url = self._build_url(path)
            params = request.args.to_dict()
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.get(url, params=params, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy get: {str(e)}"}, 500

    def post(self, path):
        try:
            url = self._build_url(path)
            data = request.get_json() or {}
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.post(url, json=data, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy post: {str(e)}"}, 500

    def put(self, path):
        try:
            url = self._build_url(path)
            data = request.get_json() or {}
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.put(url, json=data, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy put: {str(e)}"}, 500

    def delete(self, path):
        try:
            url = self._build_url(path)
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.delete(url, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy delete: {str(e)}"}, 500


class AuthProxy(Resource):
    def _build_url(self, path):
        return f"{AUTH_BASE}/api/v1/auth/{path}"

    def get(self, path):
        try:
            url = self._build_url(path)
            params = request.args.to_dict()
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.get(url, params=params, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy get: {str(e)}"}, 500

    def post(self, path):
        try:
            url = self._build_url(path)
            data = request.get_json() or {}
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.post(url, json=data, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy post: {str(e)}"}, 500

    def put(self, path):
        try:
            url = self._build_url(path)
            data = request.get_json() or {}
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.put(url, json=data, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy put: {str(e)}"}, 500

    def delete(self, path):
        try:
            url = self._build_url(path)
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.delete(url, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy delete: {str(e)}"}, 500


class ClientesProxy(Resource):
    def _build_url(self, path):
        return f"{CLIENTES_BASE}/api/v1/Travelers/{path}"

    def get(self, path):
        try:
            url = self._build_url(path)
            params = request.args.to_dict()
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.get(url, params=params, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy get: {str(e)}"}, 500

    def post(self, path):
        try:
            url = self._build_url(path)
            data = request.get_json() or {}
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.post(url, json=data, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy post: {str(e)}"}, 500

    def put(self, path):
        try:
            url = self._build_url(path)
            data = request.get_json() or {}
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.put(url, json=data, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy put: {str(e)}"}, 500

    def delete(self, path):
        try:
            url = self._build_url(path)
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.delete(url, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy delete: {str(e)}"}, 500


class ComentariosProxy(Resource):
    def _build_url(self, path):
        return f"{COMENTARIOS_BASE}/api/v1/reviews/{path}"

    def get(self, path):
        try:
            url = self._build_url(path)
            params = request.args.to_dict()
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.get(url, params=params, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy get: {str(e)}"}, 500

    def post(self, path):
        try:
            url = self._build_url(path)
            data = request.get_json() or {}
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.post(url, json=data, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy post: {str(e)}"}, 500

    def put(self, path):
        try:
            url = self._build_url(path)
            data = request.get_json() or {}
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.put(url, json=data, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy put: {str(e)}"}, 500

    def delete(self, path):
        try:
            url = self._build_url(path)
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.delete(url, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy delete: {str(e)}"}, 500


class TransaccionesProxy(Resource):
    def _build_url(self, path):
        return f"{TRANSACCIONES_BASE}/api/v1/Transactions/{path}"

    def get(self, path):
        try:
            url = self._build_url(path)
            params = request.args.to_dict()
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.get(url, params=params, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy get: {str(e)}"}, 500

    def post(self, path):
        try:
            url = self._build_url(path)
            data = request.get_json() or {}
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.post(url, json=data, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy post: {str(e)}"}, 500

    def put(self, path):
        try:
            url = self._build_url(path)
            data = request.get_json() or {}
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.put(url, json=data, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy put: {str(e)}"}, 500

    def delete(self, path):
        try:
            url = self._build_url(path)
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.delete(url, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy delete: {str(e)}"}, 500


class ProveedoresProxy(Resource):
    def _build_url(self, path):
        return f"{PROVEEDORES_BASE}/api/v1/Managers/{path}"

    def get(self, path):
        try:
            url = self._build_url(path)
            params = request.args.to_dict()
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.get(url, params=params, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy get: {str(e)}"}, 500

    def post(self, path):
        try:
            url = self._build_url(path)
            data = request.get_json() or {}
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.post(url, json=data, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy post: {str(e)}"}, 500

    def put(self, path):
        try:
            url = self._build_url(path)
            data = request.get_json() or {}
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.put(url, json=data, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy put: {str(e)}"}, 500

    def delete(self, path):
        try:
            url = self._build_url(path)
            headers = dict(request.headers)
            headers.pop('Host', None)
            response = requests.delete(url, headers=headers, timeout=30)
            return response.json(), response.status_code
        except Exception as e:
            return {"message": f"Error proxy delete: {str(e)}"}, 500


class StartAllServices(Resource):
    def post(self):
        """
        Inicia todos los microservicios de TravelHub
        ---
        tags:
          - Admin
        responses:
          200:
            description: Microservicios iniciados
        """
        services = [
            ("inventario_app", "inventario_app", 3000),
            ("reserva_app", "reserva_app", 3001),
            ("busquedas_app", "busquedas_app", 3002),
            ("comentariosapp", "comentariosapp", 3003),
            ("autenticadorapp", "autenticadorapp", 3004),
            ("transaccionesapp", "transaccionesapp", 3005),
            ("proveedoresapp", "proveedoresapp", 3006),
            ("clientesapp", "clientesapp", 3007),
        ]
        
        started = []
        errors = []
        
        for service_name, service_folder, port in services:
            try:
                service_path = os.path.join(PROJECT_ROOT, "..", "..", service_folder)
                main_path = os.path.join(service_path, "main.py")
                if not os.path.exists(main_path):
                    errors.append(f"{service_name}: main.py no encontrado")
                    continue
                    
                subprocess.Popen(
                    [sys.executable, main_path],
                    cwd=service_path,
                    creationflags=1 if sys.platform == 'win32' else 0,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                started.append(f"{service_name} (puerto {port})")
            except Exception as e:
                errors.append(f"{service_name}: {str(e)}")
        
        return {
            "message": "Microservicios iniciados" if started else "Error iniciando servicios",
            "started": started,
            "errors": errors
        }, 200 if started else 500