class APIError(Exception):
    def __init__(
            self,
            message,
            status_code
        ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class ExternalServiceError(APIError):
    def __init__(self, message = 'External service error'):
        super().__init__(message, 502)
    
class DatababaseError(APIError):
    def __init__(self, message = 'Database error'):
        super().__init__(message, 500)
    
class InternalServerError(APIError):
    def __init__(self, message = 'Internal server error'):
        super().__init__(message, 500)