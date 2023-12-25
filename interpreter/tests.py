import unittest

from interpreter import interpreter_file


class TestInterpreter(unittest.TestCase):

    def test_same_program_multiple_executing(self):
        interpreter = interpreter_file.Interpreter()
        result1 = interpreter.execute("programs/program2.txt")
        result2 = interpreter.execute("programs/program2.txt")
        result3 = interpreter.execute("programs/program2.txt")

        self.assertEqual(result1, result2, result3)

    def test_interpreter1(self):
        interpreter = interpreter_file.Interpreter()
        result = interpreter.execute("programs/program1.txt")
        self.assertEqual(result,
                         [(0, 0), (2, 0), (4, 0), (6, 0), (6, 2), (6, 4)])
        self.assertEqual(interpreter.grid.get_coords(), (6, 4))

    # def test_grid_out_of_bounds_error(self):
    #     interpreter = Interpreter()
    #     result = interpreter.execute("programs/out_of_bounds_error.txt")
    #
    #     self.assertEqual(result.get_message(),
    #                      "GridOutOfBounceError --> Invalid direction. "
    #                      "It must be between 0 and 21. "
    #                      "You can't move down 2 times.")

    def test_3_nested_procedure_calls(self):
        interpreter = interpreter_file.Interpreter()
        result = interpreter.execute("programs/3nested_proc.txt")

        self.assertEqual(result, [(0, 0), (0, 4), (3, 4), (3, 6)])

    def test_program2(self):
        interpreter = interpreter_file.Interpreter()
        result = interpreter.execute("programs/program2.txt")

        self.assertEqual(result,
                         [(0, 0), (2, 0), (2, 10), (1, 10), (0, 10), (2, 10),
                          (2, 20), (1, 20), (0, 20), (2, 20)])

    # def test_repeat_not_closed(self):
    #     interpreter = Interpreter()
    #
    #     result = interpreter.execute("programs/repeat_not_closed.txt")
    #     self.assertEqual(result.get_message(),
    #                      "CycleNotClosedError --> "
    #                      "Your repeat cycle is not closed")
    #
    #     result = interpreter.execute("programs/repeat_not_closed1.txt")
    #     self.assertEqual(result.get_message(),
    #                      "CycleNotClosedError --> "
    #                      "Your repeat cycle is not closed")
