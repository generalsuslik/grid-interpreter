import unittest

from interpreter import interpreter_file


class TestInterpreter(unittest.TestCase):

    def test_same_program_multiple_executing(self):
        interpreter = interpreter_file.Interpreter()
        result1 = interpreter.execute("programs/program2.txt")
        result2 = interpreter.execute("programs/program2.txt")
        result3 = interpreter.execute("programs/program2.txt")

        self.assertEqual(result1, result2, result3)

    def test_same_program_multiple_executing_2(self):
        interpreter = interpreter_file.Interpreter()
        result = set()
        for i in range(40):
            ans = interpreter.execute("programs/program1.txt")
            s = ""
            for t in ans:
                s += f"[{t[0]}, {t[1]}]"
            result.add(s)

        self.assertEqual(len(result), 1)

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

