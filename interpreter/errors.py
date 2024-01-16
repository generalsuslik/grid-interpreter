class Error(Exception):
    def __init__(self, message: str) -> None:
        self.message = f"{self.__class__.__name__}: {message}"

    def get_message(self) -> str:
        return self.message

    def __str__(self) -> str:
        return self.message


class GridOutOfBounceError(Error):               # done
    pass


class VariableNotDeclared(Error):                  # done
    pass


class ProcedureNotDeclaredError(Error):                # done
    pass


class ProcedureNotClosedError(Error):                # done
    pass


class RepeatNotClosedError(Error):                   # done
    pass


class IFBlockNotClosedError(Error):                  # done
    pass


class ExecuteAtLeastOnce(Error):
    pass


class NotDeclaredVariableError(Error):                # done
    pass


class EndlessRepeatError(Error):                       # done
    pass


class ProcedureAlreadyDeclaredError(Error):              # done
    pass


class Increasing3NestedCallsError(Error):                 # done
    pass


class IncorrectRepeatDeclarationError(Error):             # done
    pass


class NoSuchCommandError(Error):
    pass


class WrongSyntaxCommandError(Error):
    pass


class FileReadingError(Error):
    pass


class SomethingWentWrongError(Error):
    pass


class ForbiddenParametersError(Error):
    pass
