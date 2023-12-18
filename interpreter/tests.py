import unittest

from interpreter import Interpreter


class TestInterpreter(unittest.TestCase):
    def test_interpreter1(self):
        interpreter = Interpreter()
        result = interpreter.execute("programs/program1.txt")
        self.assertEqual(result,
                         [(0, 0), (2, 0), (4, 0), (6, 0), (6, 2), (6, 4)])
        self.assertEqual(interpreter.grid.get_coords(), (6, 4))

    def test_grid_out_of_bounds_error(self):
        interpreter = Interpreter()
        result = interpreter.execute("programs/out_of_bounds_error.txt")

        self.assertEqual(result.get_message(),
                         "GridOutOfBounceError --> Invalid direction. "
                         "It must be between 0 and 21. "
                         "You can't move down 2 times.")
