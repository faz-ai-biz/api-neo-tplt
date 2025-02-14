class CustomAppException(Exception):
    """Base exception class for application-specific exceptions."""

    pass


class InvalidTokenError(CustomAppException):
    def __init__(self, message="Invalid or expired token"):
        self.message = message
        super().__init__(self.message)


class PasswordTooWeakException(CustomAppException):
    def __init__(self, message="Password does not meet security requirements"):
        self.message = message
        super().__init__(self.message)


class UserNotFoundError(CustomAppException):
    def __init__(self, message="User not found"):
        self.message = message
        super().__init__(self.message)


class FileNotFoundError(Exception):
    """Raised when a requested file is not found"""

    def __init__(self, message: str = "File not found"):
        self.message = message
        super().__init__(self.message)
