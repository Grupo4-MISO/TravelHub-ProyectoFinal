from app.errors.exceptions import APIError

class ErrorHandler:
    @staticmethod
    def errors(app):
        @app.errorhandler(APIError)
        def handleApiError(error):
            return {'msg': error.message}, error.status_code