import unittest

from interpreter import errors, interpreter_file


class TestInterpreter(unittest.TestCase):

    def test_same_program_multiple_executing(self):
        interpreter = interpreter_file.Interpreter()
        result1 = interpreter.execute("test_programs/program2.txt")
        result2 = interpreter.execute("test_programs/program2.txt")
        result3 = interpreter.execute("test_programs/program2.txt")

        self.assertEqual(result1, result2, result3)

    def test_same_program_multiple_executing_2(self):
        interpreter = interpreter_file.Interpreter()
        result = set()
        for i in range(40):
            ans = interpreter.execute("test_programs/program1.txt")
            s = ""
            for t in ans:
                s += f"[{t[0]}, {t[1]}]"
            result.add(s)

        self.assertEqual(len(result), 1)

    def test_3_nested_procedure_calls(self):
        interpreter = interpreter_file.Interpreter()
        try:
            interpreter.execute("test_programs/3nested_proc.txt")

        except errors.Increasing3NestedCallsError as error:
            self.assertEqual(error.message,
                             "Increasing3NestedCallsError: "
                             "You've increased 3 nested calls rule")

    def test_program2(self):
        interpreter = interpreter_file.Interpreter()
        result = interpreter.execute("test_programs/program2.txt")

        self.assertEqual(result,
                         [(0, 0), (2, 0), (2, 10), (1, 10), (0, 10), (2, 10),
                          (2, 20), (1, 20), (0, 20), (2, 20)])
        self.assertEqual(interpreter.interpreter_get_coords(), (2, 20))

    def test_run_at_least_once(self):
        interpreter = interpreter_file.Interpreter()
        with self.assertRaises(errors.ExecuteAtLeastOnce):
            interpreter.interpreter_get_coords()

    def test_ifblocks1(self):
        interpreter = interpreter_file.Interpreter()
        result = interpreter.execute("test_programs/test_ifblocks1.txt")

        self.assertEqual(result, [(0, 0), (2, 0), (2, 2), (2, 6)])

    def test_ifblocks2(self):
        interpreter = interpreter_file.Interpreter()
        result = interpreter.execute("test_programs/test_ifblocks2.txt")

        self.assertEqual(result, [(0, 0), (0, 4), (2, 4), (2, 20), (6, 20), (20, 20)])

    def test_for_reglament_1(self):
        interpreter = interpreter_file.Interpreter()
        result = interpreter.execute("programs_4_reglament/1.txt")

        self.assertEqual(result, [(0, 0), (5, 0), (10, 0), (15, 0), (15, 10), (13, 10), (13, 12)])

    def test_for_reglament_2(self):
        interpreter = interpreter_file.Interpreter()

        try:
            interpreter.execute("programs_4_reglament/2.txt")

        except errors.GridOutOfBounceError as error:
            self.assertEqual(error.get_message(), "GridOutOfBounceError: "
                                                  "Invalid direction. It must be between 0 and 20. "
                                                  "You can't move right 2 times. Your previous position: (20, 0)")

    def test_for_reglament_2_correct(self):
        interpreter = interpreter_file.Interpreter()
        result = interpreter.execute("programs_4_reglament/2_correct.txt")

        self.assertEqual(result,
                         [(0, 0), (2, 0), (4, 0), (6, 0), (8, 0), (10, 0),
                          (12, 0), (14, 0), (16, 0), (18, 0), (20, 0)])

    def test_for_reglament_5_a(self):
        interpreter = interpreter_file.Interpreter()

        try:
            interpreter.execute("programs_4_reglament/5_a_out_of_bounce.txt")

        except errors.GridOutOfBounceError as error:
            self.assertEqual(error.get_message(), "GridOutOfBounceError: Invalid direction. "
                                                  "It must be between 0 and 20. You can't move right 22 times. "
                                                  "Your previous position: (0, 0)")

    def test_for_reglament_5_b_1(self):
        interpreter = interpreter_file.Interpreter()

        try:
            interpreter.execute("programs_4_reglament/5_b_1_wrong_command_format.txt")

        except errors.NoSuchCommandError as error:
            self.assertEqual(error.get_message(), "NoSuchCommandError: No such command: RIGH. "
                                                  "Maybe you ment RIGHT")

    def test_for_reglament_5_b_2(self):
        interpreter = interpreter_file.Interpreter()

        try:
            interpreter.execute("programs_4_reglament/5_b_2_wrong_command_format.txt")

        except errors.NoSuchCommandError as error:
            self.assertEqual(error.get_message(), "NoSuchCommandError: No such command: JUMP")

    def test_for_reglament_5_c(self):
        interpreter = interpreter_file.Interpreter()

        try:
            interpreter.execute("programs_4_reglament/5_c_forbidden_parametres.txt")

        except errors.WrongSyntaxCommandError as error:
            self.assertEqual(error.get_message(), "WrongSyntaxCommandError: You can't move LEFT -5 times")
