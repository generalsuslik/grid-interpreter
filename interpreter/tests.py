import unittest

from interpreter import Interpreter


class TestInterpreter(unittest.TestCase):
    def test_interpreter1(self):
        interpreter = Interpreter("programs/program1.txt")
        interpreter.execute()
        self.assertEqual(interpreter.coordinates, [(0, 0), (2, 0), (4, 0), (6, 0), (6, 2), (6, 4)])
        self.assertEqual(interpreter.grid.get_coords(), (6, 4))
