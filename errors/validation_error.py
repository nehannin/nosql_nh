class ValidationError(Exception):
    def __init__(self, message='Validation Error'):
        self.args = (message,)
        