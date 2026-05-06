from app.db.models import db, Tarifa


class TarifaCrud:
    """Clase para manejar operaciones CRUD de Tarifas"""

    def create_tarifa(self, nombre, valor_noche, moneda, categoria_habitacion, vigencia_inicio, vigencia_fin, identificador=None, descripcion=None):
        """Crear una nueva tarifa"""
        try:
            nueva_tarifa = Tarifa(
                nombre=nombre,
                identificador=identificador,
                descripcion=descripcion,
                valor_noche=valor_noche,
                moneda=moneda,
                categoria_habitacion=categoria_habitacion,
                vigencia_inicio=vigencia_inicio,
                vigencia_fin=vigencia_fin,
            )
            db.session.add(nueva_tarifa)
            db.session.commit()
            return nueva_tarifa
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error al crear tarifa: {str(e)}")

    def get_all_tarifas(self):
        """Obtener todas las tarifas"""
        return Tarifa.query.all()

    def get_tarifa_by_id(self, tarifa_id):
        """Obtener tarifa por ID"""
        return Tarifa.query.filter_by(id=tarifa_id).first()

    def update_tarifa(self, tarifa_id, **kwargs):
        """Actualizar tarifa"""
        try:
            tarifa = self.get_tarifa_by_id(tarifa_id)
            if not tarifa:
                raise Exception("Tarifa no encontrada")
            
            for key, value in kwargs.items():
                if hasattr(tarifa, key):
                    setattr(tarifa, key, value)
            
            db.session.commit()
            return tarifa
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error al actualizar tarifa: {str(e)}")

    def delete_tarifa(self, tarifa_id):
        """Eliminar tarifa"""
        try:
            tarifa = self.get_tarifa_by_id(tarifa_id)
            if not tarifa:
                raise Exception("Tarifa no encontrada")
            
            db.session.delete(tarifa)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error al eliminar tarifa: {str(e)}")

    def get_tarifas_by_tipo(self, tipo_servicio):
        """Compatibilidad: retorna tarifas por categoria_habitacion"""
        return Tarifa.query.filter_by(categoria_habitacion=tipo_servicio).all()
