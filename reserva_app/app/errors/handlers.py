from app.errors.exceptions import APIError

class ErrorHandler:
    @staticmethod
    def errors(app):
        @app.errorhandler(APIError)
        def handleApiError(error):
            return {'msg': error.message}, error.status_code

        @app.errorhandler(404)
        def handleNotFound(error):
            return {'msg': f'Not Found: {error}'}, 404

        @app.errorhandler(Exception)
        def handleUnhandledError(error):
            return {'msg': f'Error interno del servidor: {str(error)}'}, 500