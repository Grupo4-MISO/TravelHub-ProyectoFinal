from datetime import datetime

class ReservaHelper:
    @staticmethod
    def convertirFechasDate(fecha):
        return datetime.strptime(fecha, '%Y-%m-%d').date()