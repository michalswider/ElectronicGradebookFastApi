class ApplicationException(Exception):
    def __init__(self, detail: str, status_code: int, user: str = "Anonymous"):
        self.detail = detail
        self.status_code = status_code
        self.user = user

    def to_response(self):
        return {"detail": self.detail}, self.status_code

    def __str__(self):
        return f"{self.__class__.__name__} (status_code={self.status_code}, user={self.user}): {self.detail}"


class ExistException(ApplicationException):
    def __init__(self, detail: str, status_code: int = 400, user: str = "Anonymous"):
        super().__init__(detail, status_code, user)


class NotFoundException(ApplicationException):
    def __init__(self, detail: str, status_code: int = 404, user: str = "Anonymous"):
        super().__init__(detail, status_code, user)


class InvalidException(ApplicationException):
    def __init__(self, detail: str, status_code: int = 400, user: str = "Anonymous"):
        super().__init__(detail, status_code, user)


class ForeignKeyConstraintException(ApplicationException):
    def __init__(self, detail: str, status_code: int = 409, user: str = "Anonymous"):
        super().__init__(detail, status_code, user)
