
class BusquedasHelper:
    @staticmethod
    def filtrarHabitacionesDisponibles(hospedajes_habitaciones, disponibles):
        #Diccionario de habitaciones disponibles
        hospedajes_habitaciones_disponibles = list()

        #Pasamos disponibles a set
        disponibles = set(disponibles)

        for hospedaje_habitacion in hospedajes_habitaciones:
            if hospedaje_habitacion.get('habitacion_id') in disponibles:
                hospedajes_habitaciones_disponibles.append(hospedaje_habitacion)
        
        return hospedajes_habitaciones_disponibles