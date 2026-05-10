import requests
import os
from datetime import datetime, timezone
from app.errors.exceptions import ExternalServiceError, BadRequestError

TARIFAS_URL = os.getenv('TARIFAS_URL', 'http://127.0.0.1:3005')


class TarifasHelper:
    """Helper para consultar el microservicio de tarifas y obtener tarifa/descuentos aplicables"""

    @staticmethod
    def obtener_tarifa_para_reserva(hotel_id: str, categoria_habitacion: str, check_in_str: str, check_out_str: str, currency_code: str = None, auth_headers=None):
        """
        Consulta la tarifa vigente para una combinación de hotel, categoría y fechas.
        
        Args:
            hotel_id: UUID del hotel
            categoria_habitacion: Categoría (SENCILLA, DOBLE, SUITE, etc)
            check_in_str: Fecha en formato YYYY-MM-DD
            check_out_str: Fecha en formato YYYY-MM-DD
            currency_code: Código de moneda (COP, USD, etc) [opcional]
            
        Returns:
            dict con tarifa_id, valor_final, descuentos_aplicados
            None si no existe tarifa vigente
        """
        try:
            # Parseamos las fechas para validar que sean vigentes
            check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
            check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
            now_utc = datetime.now(timezone.utc)

            headers = dict(auth_headers) if auth_headers else None
            if headers:
                headers.pop('Host', None)
            
            # Consultamos todas las tarifas vigentes del hotel
            response = requests.get(
                f"{TARIFAS_URL}/tarifas",
                params={"vigentes": "true"},
                headers=headers,
                timeout=5
            )
            response.raise_for_status()
            
            tarifas = response.json()
            
            # Filtramos por hotel_id y categoria_habitacion
            tarifa_encontrada = None
            for tarifa in tarifas:
                if (tarifa.get('hotel_id') == hotel_id and 
                    tarifa.get('categoria_habitacion') == categoria_habitacion.upper()):
                    
                    # Validamos que esté vigente para las fechas de la reserva
                    vigencia_inicio = datetime.fromisoformat(tarifa.get('vigencia_inicio')).replace(tzinfo=None)
                    vigencia_fin = datetime.fromisoformat(tarifa.get('vigencia_fin')).replace(tzinfo=None)
                    
                    check_in_dt = datetime.combine(check_in, datetime.min.time())
                    check_out_dt = datetime.combine(check_out, datetime.min.time())
                    
                    # La tarifa es válida si cubre al menos parte del período
                    if not (check_out_dt < vigencia_inicio or check_in_dt > vigencia_fin):
                        tarifa_encontrada = tarifa
                        break
            
            if not tarifa_encontrada:
                return None
            
            # Armar respuesta con información de tarifa
            return {
                'tarifa_id': tarifa_encontrada.get('id'),
                'precio_tarifa_aplicada': tarifa_encontrada.get('valor_final'),
                'descuentos_aplicados': tarifa_encontrada.get('descuentos_activos'),
                'valor_base': tarifa_encontrada.get('valor_base'),
                'moneda': tarifa_encontrada.get('moneda'),
            }
            
        except requests.exceptions.RequestException as e:
            # Log pero no fallar - continuar sin tarifa
            print(f"Advertencia: Error al consultar tarifas: {str(e)}")
            return None
        except Exception as e:
            print(f"Advertencia: Error procesando tarifa: {str(e)}")
            return None

    @staticmethod
    def calcular_descuentos_totales(descuentos_activos: list) -> float:
        """
        Calcula el porcentaje total de descuentos aplicados.
        
        Args:
            descuentos_activos: Lista de descuentos desde la tarifa
            
        Returns:
            float: descuento total aplicado (entre 0 y 1)
        """
        if not descuentos_activos:
            return 0.0
        
        descuento_total = 0.0
        for desc in descuentos_activos:
            descuento_total += float(desc.get('porcentaje', 0)) / 100.0
        
        # Limitar a máximo 1.0
        return min(descuento_total, 1.0)
