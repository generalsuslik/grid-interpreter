class Error:
    def __init__(self) -> None:
        pass


class OutOfGridBounceError(Error):
    def __init__(self) -> None:
        super().__init__()


class VariableNotDeclared(Error):
    def __init__(self) -> None:
        super().__init__()
