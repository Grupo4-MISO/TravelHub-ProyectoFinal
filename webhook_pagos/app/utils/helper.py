class Helper:
    @staticmethod
    def response(status_code, message):
        return {
            "status_code": status_code,
            "message": message,
        }