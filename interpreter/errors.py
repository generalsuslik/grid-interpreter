class Error(Exception):
    def __init__(self, message: str) -> None:
        self.message = message

    def get_message(self) -> str:
        return self.message

    def __str__(self) -> str:
        return self.message


class GridOutOfBounceError(Error):
    def __init__(self, message: str) -> None:
        super().__init__(f"{self.__class__.__name__} --> {message}")


class VariableNotDeclared(Error):
    def __init__(self, message: str) -> None:
        super().__init__(f"{self.__class__.__name__} --> {message}")


class ProcedureNotDeclaredError(Error):
    def __init__(self, message: str) -> None:
        super().__init__(f"{self.__class__.__name__} --> {message}")


class ProcedureNotClosedError(Error):
    def __init__(self, message: str) -> None:
        super().__init__(f"{self.__class__.__name__} --> {message}")


class RepeatNotClosedError(Error):
    def __init__(self, message: str) -> None:
        super().__init__(f"{self.__class__.__name__} --> {message}")


class IFBlockNotClosedError(Error):
    def __init__(self, message: str) -> None:
        super().__init__(f"{self.__class__.__name__} --> {message}")

