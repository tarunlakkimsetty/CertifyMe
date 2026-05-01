class AppError(Exception):
    pass


class ValidationError(AppError):
    pass


class AuthenticationError(AppError):
    pass


class DuplicateEmailError(AppError):
    pass


class NotFoundError(AppError):
    pass


class ForbiddenError(AppError):
    pass
