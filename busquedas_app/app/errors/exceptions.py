class APIError(Exception):
    def __init__(
            self,
            message,
            status_code
        ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class BadRequestError(APIError):
    def __init__(self, message = 'Bad request'):
        super().__init__(message, 400)


class NotFoundError(APIError):
    def __init__(self, message = 'Resource not found'):
        super().__init__(message, 404)


class ExternalServiceError(APIError):
    def __init__(self, message = 'External service error'):
        super().__init__(message, 502)