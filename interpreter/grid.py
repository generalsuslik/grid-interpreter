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
                    raise ValueError

            case "LEFT":
                if 0 <= (self.x - val) <= 21:
                    self.x -= val

                else:
                    raise ValueError

            case "UP":
                if 0 <= (self.y + val) <= 21:
                    self.y += val

                else:
                    raise ValueError

            case "DOWN":
                if 0 <= (self.y - val) <= 21:
                    self.y -= val

                else:
                    raise ValueError

    def get_coords(self):
        return self.x, self.y

    def __str__(self):
        return f"{self.x} {self.y}"
