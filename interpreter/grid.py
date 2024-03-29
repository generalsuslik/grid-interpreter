from interpreter import errors


class Grid:
    def __init__(self, start_x=0, start_y=0):
        self.x = start_x
        self.y = start_y

    def move(self, _direction: int, val: int) -> None:
        match _direction:
            case "RIGHT":
                if 0 <= (self.x + val) <= 20:
                    self.x += val

                else:
                    raise errors.GridOutOfBounceError(
                        f"Invalid direction. It must be between 0 and 20. "
                        f"You can't "
                        f"move right {val} times. "
                        f"Your previous position: {self.get_coords()}")

            case "LEFT":
                if 0 <= (self.x - val) <= 20:
                    self.x -= val

                else:
                    raise errors.GridOutOfBounceError(
                        f"Invalid direction. "
                        f"It must be between 0 and 20. "
                        f"You can't "
                        f"move left {val} times. "
                        f"Your previous position: {self.get_coords()}")

            case "UP":
                if 0 <= (self.y + val) <= 20:
                    self.y += val

                else:
                    raise errors.GridOutOfBounceError(
                        f"Invalid direction. It must be between 0 and 20. "
                        f"You can't "
                        f"move up {val} times. "
                        f"Your previous position: {self.get_coords()}")

            case "DOWN":
                if 0 <= (self.y - val) <= 20:
                    self.y -= val

                else:
                    raise errors.GridOutOfBounceError(
                        f"Invalid direction. It must be between 0 and 20. "
                        f"You can't "
                        f"move down {val} times. "
                        f"Your previous position: {self.get_coords()}")

    def get_coords(self):
        return self.x, self.y

    def __str__(self):
        return f"{self.x} {self.y}"
