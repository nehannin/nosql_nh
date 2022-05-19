class NotFound(Exception):
    def __init__(self, message='Not Found Error'):
        self.args = (message,)
