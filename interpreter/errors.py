class Error(Exception):
    def __init__(self, message: str) -> None:
        self.message = message

    def get_message(self) -> str:
        return self.message

    def __str__(self) -> str:
        return self.message


class GridOutOfBounceError(Error):               # done
    def __init__(self, message: str) -> None:
        super().__init__(f"{self.__class__.__name__} --> {message}")


class VariableNotDeclared(Error):                  # done
    def __init__(self, message: str) -> None:
        super().__init__(f"{self.__class__.__name__} --> {message}")


class ProcedureNotDeclaredError(Error):                # done
    def __init__(self, message: str) -> None:
        super().__init__(f"{self.__class__.__name__} --> {message}")


class ProcedureNotClosedError(Error):                # done
    def __init__(self, message: str) -> None:
        super().__init__(f"{self.__class__.__name__} --> {message}")


class RepeatNotClosedError(Error):                   # done
    def __init__(self, message: str) -> None:
        super().__init__(f"{self.__class__.__name__} --> {message}")


class IFBlockNotClosedError(Error):                  # done
    def __init__(self, message: str) -> None:
        super().__init__(f"{self.__class__.__name__} --> {message}")


class ExecuteAtLeastOnce(Error):
    def __init__(
            self,
            message="You must execute any program at least once"
    ) -> None:
        super().__init__(f"{self.__class__.__name__} --> {message}")


class NotDeclaredVariableError(Error):                # done
    def __init__(self, message: str) -> None:
        super().__init__(f"{self.__class__.__name__} --> {message}")


class EndlessRepeatError(Error):                       # done
    def __init__(self, message: str) -> None:
        super().__init__(f"{self.__class__.__name__} --> {message}")


class ProcedureAlreadyDeclaredError(Error):              # done
    def __init__(self, message: str) -> None:
        super().__init__(f"{self.__class__.__name__} --> {message}")


class Increasing3NestedCallsError(Error):                 # done
    def __init__(self, message: str) -> None:
        super().__init__(f"{self.__class__.__name__} --> {message}")


class IncorrectRepeatDeclarationError(Error):             # done
    def __init__(self, message: str) -> None:
        super().__init__(f"{self.__class__.__name__} --> {message}")



