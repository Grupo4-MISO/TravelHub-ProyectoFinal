from app.errors.exceptions import BadRequestError
from datetime import datetime

class ReservaHelper:
    @staticmethod
    def convertirFechasDate(fecha):
        return datetime.strptime(fecha, '%Y-%m-%d').date()
    
    @staticmethod
    def validacionCampoFechas(check_in, check_out):
        try:
            check_in = ReservaHelper.convertirFechasDate(check_in)

        except ValueError:
            raise BadRequestError('La fecha de check-in debe estar en formato YYYY-MM-DD')
        
        except TypeError:
            raise BadRequestError('La fecha de check-in no debe ser vacía')
        
        try:
            check_out = ReservaHelper.convertirFechasDate(check_out)

        except ValueError:
            raise BadRequestError('La fecha de check-out debe estar en formato YYYY-MM-DD')
    
        except TypeError:
            raise BadRequestError('La fecha de check-out no debe ser vacía')
    
        if check_in >= check_out:
            raise BadRequestError('La fecha de check-out debe ser posterior a la fecha de check-in')
        
        if check_in < datetime.now().date():
            raise BadRequestError('La fecha de check-in debe ser una fecha futura')

        if check_out < datetime.now().date():
            raise BadRequestError('La fecha de check-out debe ser una fecha futura')

        return check_in, check_out