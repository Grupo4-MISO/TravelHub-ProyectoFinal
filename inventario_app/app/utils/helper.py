from app.errors.exceptions import BadRequestError

RATES = {
    'USD': 1,
    'COP': 4000,
    'MXN': 17,
    'PEN': 3.7,
    'CLP': 900,
    'ARS': 900,
    'USD': 1,
    'EUR': 0.92
}

class InventarioHelper:
    @staticmethod
    def validacionCampoCiudad(ciudad):
        if not ciudad:
            raise BadRequestError('El campo ciudad no debe ser vacío')

        try:
            ciudad = int(ciudad)

            if isinstance(ciudad, int):
                raise BadRequestError('El campo ciudad debe ser un texto')
        
        except ValueError:
            return ciudad
    
    @staticmethod
    def validacionCampoCapacidad(capacidad):
        try:
            capacidad = int(capacidad)

        except ValueError:
            raise BadRequestError('El campo capacidad debe ser un número entero')
        
        except TypeError:
            raise BadRequestError('El campo capacidad no debe ser vacío')
        
        if capacidad <= 0:
            raise BadRequestError('El campo capacidad debe ser un número entero positivo')

        return capacidad

    @staticmethod
    def convertirMoneda(precio, currency_code_origen, currency_code_destino):
        # Si no se especifica moneda destino, no hacemos conversión.
        if not currency_code_destino:
            return precio

        if currency_code_origen == currency_code_destino:
            return precio

        #Tasas de conversion
        tasa_origen = RATES.get(currency_code_origen)
        tasa_destino = RATES.get(currency_code_destino)

        # Distinción explícita entre ausencia de tasa (None) y tasa 0.
        if tasa_origen is None or tasa_destino is None:
            raise ValueError("Currency no soportada")

        #Convertimos a USD como base
        precio_usd = precio / tasa_origen

        #Convertimos a moneda destino
        precio_convertido = precio_usd * tasa_destino

        return round(precio_convertido, 0)

    @staticmethod
    def convertirPrecios(habitaciones, currency_code_destino):
        for habitacion in habitaciones:
            precio_origen = habitacion.get('precio')
            moneda_origen = habitacion.get('currency_code')

            precio_convertido = InventarioHelper.convertirMoneda(
                precio_origen,
                moneda_origen,
                currency_code_destino
            )

            habitacion['precio'] = precio_convertido

        return habitaciones