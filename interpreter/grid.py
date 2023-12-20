import errors


class Grid:
    def __init__(self):
        self.x = 0
        self.y = 0

    def move(self, _direction: int, val: int) -> None:
        match _direction:
            case "RIGHT":
                if 0 <= (self.x + val) <= 21:
                    self.x += val

                else:
                    raise errors.GridOutOfBounceError(
                        f"Invalid direction. It must be between 0 and 21. "
                        f"You can't "
                        f"move right {val} times.")

            case "LEFT":
                if 0 <= (self.x - val) <= 21:
                    self.x -= val

                else:
                    raise errors.GridOutOfBounceError(
                        f"Invalid direction. "
                        f"It must be between 0 and 21. "
                        f"You can't "
                        f"move left {val} times.")

            case "UP":
                if 0 <= (self.y + val) <= 21:
                    self.y += val

                else:
                    raise errors.GridOutOfBounceError(
                        f"Invalid direction. It must be between 0 and 21. "
                        f"You can't "
                        f"move up {val} times.")

            case "DOWN":
                if 0 <= (self.y - val) <= 21:
                    self.y -= val

                else:
                    raise errors.GridOutOfBounceError(
                        f"Invalid direction. It must be between 0 and 21. "
                        f"You can't "
                        f"move down {val} times.")

    def get_coords(self):
        return self.x, self.y

    def __str__(self):
        return f"{self.x} {self.y}"
