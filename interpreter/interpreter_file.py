from collections import defaultdict
from string import ascii_letters

from interpreter import errors, grid


class Interpreter:
    """
    Class represents simple interpreter. When u ran the execute() method,
    the interpreter declares all variables and procedures with get_variables()
    and get_procedures() methods respectively. Then interpreter runs 2
    parse methods,
    to open all loops and procedures calls. After that, it'll have an
    array of all static stuff and if-blocks.
    """

    def __init__(self):
        self.grid = None
        self.commands = []
        self.executable_commands = []
        self.final_executable_commands = []
        self.functions = defaultdict(list)
        self.variables = {}
        self.coordinates = [(0, 0)]

    # Variables declaration
    def get_variables(self):
        index = 0
        while index < len(self.commands):
            command = self.commands[index]
            command_split = command.split()
            if command_split[0] == "SET":
                variable_name = command_split[1]
                variable_value = command.split("=")[-1].strip()

                if variable_value in ascii_letters:

                    if self.variables.get(variable_value) is None:
                        raise errors.NotDeclaredVariableError(
                            f"No such variable: {variable_value}"
                        )

                    else:
                        variable_value = self.variables.get(variable_value)

                else:
                    variable_value = int(variable_value)

                self.variables[variable_name] = variable_value

                self.commands.pop(index)
                continue

            else:
                index += 1

    def get_procedures(self):
        index = 0
        while index < len(self.commands):
            command_split = self.commands[index].split()
            if command_split[0] == "PROCEDURE":
                procedure_name = command_split[1]
                procedure_body = []
                index += 1
                while self.commands[index] != "ENDPROC":
                    procedure_body.append(self.commands[index])
                    index += 1

                self.functions[procedure_name] = procedure_body
                index += 1
                continue

            index += 1

    def first_parse(self, commands_array) -> None | errors.Error:
        index = 0
        # Check if there is a not closed or not opened repeat cycle error
        count_repeat = 0
        count_endrepeat = 0

        for string in commands_array:
            if string.startswith("REPEAT"):
                count_repeat += 1

            if string.startswith("ENDREPEAT"):
                count_endrepeat += 1

        if count_repeat != count_endrepeat:
            raise errors.RepeatNotClosedError(
                "Your repeat cycle is not closed"
            )

        while index < len(commands_array):
            command = commands_array[index]
            split_command = command.split()
            # ########################LOOPS##############################
            # 1st loop
            if split_command[0] == "REPEAT":
                n1 = split_command[1]
                if n1 in ascii_letters:
                    check_n1 = self.variables.get(n1)
                    if check_n1 is None:
                        raise errors.NotDeclaredVariableError(
                            f"No such variable: {n1}"
                        )

                    else:
                        n1 = check_n1

                else:
                    n1 = int(n1)

                if n1 == 0:
                    raise errors.EndlessRepeatError(
                        "You've created an endless repeat"
                    )

                cycle_body1 = []
                index += 1
                while commands_array[index] != "ENDREPEAT":
                    command1 = commands_array[index]
                    split_command1 = command1.split()
                    ################################################
                    # 2 nest loop
                    if split_command1[0] == "REPEAT":
                        n2 = split_command1[1]
                        if n2 in ascii_letters:
                            check_n2 = self.variables.get(n2)
                            if check_n2 is None:
                                raise errors.NotDeclaredVariableError(
                                    f"No such variable: {n2}"
                                )

                            else:
                                n2 = check_n2

                        else:
                            n2 = int(n2)

                        if n2 == 0:
                            raise errors.EndlessRepeatError(
                                "You've created an endless repeat"
                            )

                        cycle_body2 = []
                        index += 1
                        # while we haven't quited 2 loop
                        while commands_array[index] != "ENDREPEAT":
                            command2 = commands_array[index]
                            split_command2 = command2.split()
                            # --------------------------------------------
                            # last 3rd nested loop
                            if split_command2[0] == "REPEAT":
                                # we've found 3rd (last) loop
                                n3 = split_command1[1]
                                if n3 in ascii_letters:
                                    check_n3 = self.variables.get(n3)
                                    if check_n3 is None:
                                        raise errors.NotDeclaredVariableError(
                                            f"No such variable: {n3}"
                                        )

                                    n3 = check_n3

                                else:
                                    n3 = int(n3)

                                if n3 == 0:
                                    raise errors.EndlessRepeatError(
                                        "You've created an endless repeat"
                                    )
                                cycle_body3 = []
                                index += 1
                                while commands_array[index] != "ENDREPEAT":
                                    if (commands_array[index].split()[0]
                                            == "REPEAT" or
                                            commands_array[index].split()[0]
                                            == "CALL"):
                                        raise (errors.
                                        Increasing3NestedCallsError(
                                            "You've increased 3 nested calls "
                                            "rule"
                                        ))

                                    cycle_body3.append(commands_array[index])
                                    try:
                                        index += 1

                                    except IndexError:
                                        raise errors.RepeatNotClosedError(
                                            "Your repeat cycle is not closed"
                                        )

                                # escaping from "ENDREPEAT" in 3rd loop
                                index += 1
                                # Adding elements from 3rd loop
                                # n3 times to 2nd loop's body
                                for _ in range(n3):
                                    for elem in cycle_body3:
                                        cycle_body2.append(elem)
                                # 3 nest done
                            # ---------------------------------------------#
                            # continuing 2 nest
                            ################################################
                            else:  # We quited 3rd loop, and now we're
                                # able to continue working with 2nd loop
                                cycle_body2.append(commands_array[index])
                                try:
                                    index += 1

                                except IndexError:
                                    raise errors.RepeatNotClosedError(
                                        "Your repeat cycle is not closed"
                                    )

                        index += 1  # escaping from "ENDREPEAT" in 2nd loop
                        # Our 2nd loop has ended. Now we have to
                        # add elements from cycle2 n2 times to cycle1
                        for _ in range(n2):
                            for elem in cycle_body2:
                                cycle_body1.append(elem)

                    #####################################################
                    # continuing 1st nest
                    else:  # We quited 2nd loop, and now we're able to
                        # continue working with 1st loop
                        cycle_body1.append(commands_array[index])
                        try:
                            index += 1

                        except IndexError:
                            return errors.RepeatNotClosedError(
                                "Your repeat cycle is not closed"
                            )

                index += 1  # escaping from "ENDREPEAT" in 1st loop
                for _ in range(n1):
                    for elem in cycle_body1:
                        self.executable_commands.append(elem)

                continue

            # ########################LOOPS##############################

            # Skip PROCEDURES declaration
            elif split_command[0] == "PROCEDURE":
                index += 1
                while commands_array[index] != "ENDPROC":
                    index += 1

                index += 1
                continue

            # Working with procedures calling
            elif split_command[0] == "CALL":
                procedure_name1 = split_command[1]
                call_cycle1 = []
                for elem1 in self.functions[procedure_name1]:
                    elem_split1 = elem1.split()
                    # Case we found 2nd func call
                    if elem_split1[0] == "CALL":
                        procedure_name2 = elem_split1[1]
                        call_cycle2 = []
                        for elem2 in self.functions[procedure_name2]:
                            elem_split2 = elem2.split()
                            # Case we found 3rd procedure call
                            if elem_split2[0] == "CALL":
                                procedure_name3 = elem_split2[1]
                                call_cycle3 = []
                                for elem3 in self.functions[procedure_name3]:
                                    if elem3.split()[0] == "CALL" or \
                                            elem3.split()[0] == "REPEAT":
                                        raise (errors.
                                        Increasing3NestedCallsError(
                                            "You've increased 3 nested calls "
                                            "rule"
                                        ))

                                    call_cycle3.append(elem3)

                                for called3 in call_cycle3:
                                    call_cycle2.append(called3)

                            # We're done with 3rd procedure call
                            else:
                                call_cycle2.append(elem2)

                        for called2 in call_cycle2:
                            call_cycle1.append(called2)

                    #  we're done with second func call
                    else:
                        call_cycle1.append(elem1)

                # Now, let's add all commands from cycle1 to the main array
                for c in call_cycle1:
                    self.executable_commands.append(c)

            # End of working with procedures calling

            else:
                self.executable_commands.append(command)

            index += 1

    def second_parse(self):
        index = 0
        # Check if there is a not closed or not opened repeat cycle error
        count_repeat = 0
        count_endrepeat = 0

        for string in self.executable_commands:
            if string.startswith("REPEAT"):
                count_repeat += 1

            if string.startswith("ENDREPEAT"):
                count_endrepeat += 1

        if count_repeat != count_endrepeat:
            raise errors.RepeatNotClosedError(
                "Your repeat cycle is not closed"
            )
        while index < len(self.executable_commands):
            command = self.executable_commands[index]
            split_command = command.split()
            # ########################LOOPS##############################
            # 1st loop
            if split_command[0] == "REPEAT":
                n1 = split_command[1]
                if n1 in ascii_letters:
                    check_n1 = self.variables.get(n1)
                    if check_n1 is None:
                        raise errors.NotDeclaredVariableError(
                            f"No such variable: {n1}"
                        )

                    n1 = check_n1

                else:
                    n1 = int(n1)

                if n1 == 0:
                    raise errors.EndlessRepeatError(
                        "You've created an endless repeat"
                    )

                cycle_body1 = []
                index += 1
                while self.executable_commands[index] != "ENDREPEAT":
                    command1 = self.executable_commands[index]
                    split_command1 = command1.split()
                    ########################################################
                    # 2 nest loop
                    if split_command1[0] == "REPEAT":
                        n2 = split_command1[1]
                        if n2 in ascii_letters:
                            check_n2 = self.variables.get(n2)
                            if check_n2 is None:
                                raise errors.NotDeclaredVariableError(
                                    f"No such variable: {n2}"
                                )

                            else:
                                n2 = check_n2

                        else:
                            n2 = int(n2)

                        if n2 == 0:
                            raise errors.EndlessRepeatError(
                                "You've created an endless repeat"
                            )

                        cycle_body2 = []
                        index += 1
                        while self.executable_commands[index] != "ENDREPEAT":
                            # while we haven't quited 2 loop
                            command2 = self.executable_commands[index]
                            split_command2 = command2.split()
                            # ----------------------------------------------#
                            # last 3rd nested loop
                            if split_command2[0] == "REPEAT":
                                # we've found 3rd (last) loop
                                n3 = split_command2[1]
                                if n3 in ascii_letters:
                                    check_n3 = self.variables.get(n3)
                                    if check_n3 is None:
                                        raise errors.NotDeclaredVariableError(
                                            f"No such variable: {n3}"
                                        )

                                    else:
                                        n3 = check_n3

                                else:
                                    n3 = int(n3)

                                if n3 == 0:
                                    raise errors.EndlessRepeatError(
                                        "You've created an endless repeat"
                                    )

                                cycle_body3 = []
                                index += 1
                                this_comm = self.executable_commands[index]
                                while this_comm != "ENDREPEAT":

                                    if (self.executable_commands[index].
                                            split()[0]
                                            == "REPEAT" or
                                            self.executable_commands[index].
                                                    split()[0]
                                            == "CALL"):
                                        raise (errors.
                                        Increasing3NestedCallsError(
                                            "You've increased 3 nested calls "
                                            "rule"
                                        ))

                                    cycle_body3.append(
                                        self.executable_commands[index]
                                    )
                                    try:
                                        index += 1

                                    except IndexError:
                                        raise errors.RepeatNotClosedError(
                                            "Your repeat cycle is not closed"
                                        )
                                    this_comm = self.executable_commands[index]
                                # escaping from "ENDREPEAT" in 3rd loop
                                index += 1
                                # Adding elements from 3rd loop n3 times
                                # to 2nd loop's body
                                for _ in range(n3):
                                    for elem in cycle_body3:
                                        cycle_body2.append(elem)
                                # 3 nest done
                            # ---------------------------------------------#
                            # continuing 2 nest
                            ################################################
                            else:  # We quited 3rd loop, and now we're able to
                                # continue working with 2nd loop
                                cycle_body2.append(
                                    self.executable_commands[index]
                                )
                                try:
                                    index += 1

                                except IndexError:
                                    raise errors.RepeatNotClosedError(
                                        "Your repeat cycle is not closed"
                                    )

                        index += 1  # escaping from "ENDREPEAT" in 2nd loop
                        # Our 2nd loop has ended. Now we have to
                        # add elements from cycle2 n2 times to cycle1
                        for _ in range(n2):
                            for elem in cycle_body2:
                                cycle_body1.append(elem)

                    #####################################################
                    # continuing 1st nest
                    else:  # We quited 2nd loop, and now we're able to
                        # continue working with 1st loop
                        cycle_body1.append(self.executable_commands[index])
                        try:
                            index += 1

                        except IndexError:
                            raise errors.RepeatNotClosedError(
                                "Your repeat cycle is not closed"
                            )

                index += 1  # escaping from "ENDREPEAT" in 1st loop
                for _ in range(n1):
                    for elem in cycle_body1:
                        self.final_executable_commands.append(elem)

                continue

            # ########################LOOPS#############################
            else:
                self.final_executable_commands.append(command)

            index += 1

    def execute(self, program_file: str) -> (
            None | errors.Error | list[tuple[int, int]]
    ):
        self.commands = []
        self.executable_commands = []
        self.final_executable_commands = []
        self.functions = defaultdict(list)
        self.variables = {}
        self.coordinates = [(0, 0)]

        self.grid = grid.Grid(start_x=0, start_y=0)
        self.load_file(program_file)
        self.get_variables()
        self.get_procedures()
        first_parse_error = self.first_parse(self.commands)
        second_parse_error = self.second_parse()

        if first_parse_error is not None:
            return first_parse_error

        if second_parse_error is not None:
            return second_parse_error

        i = 0
        while i < len(self.final_executable_commands):
            command = self.final_executable_commands[i]
            command_split = command.split()
            if command_split[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                if command_split[1] in self.variables.keys():
                    value_to_move = self.variables[command_split[1]]
                else:
                    value_to_move = int(command_split[1])

                self.grid.move(command_split[0], value_to_move)

                self.coordinates.append((self.grid.x, self.grid.y))

            if command_split[0] == "IFBLOCK":
                block_direction = command_split[1]
                try:
                    endif_index = (self.final_executable_commands[i:]
                                   .index("ENDIF") + i)

                except ValueError:
                    raise errors.IFBlockNotClosedError(
                        "IFBlock was never closed"
                    )

                match block_direction:
                    case "UP":
                        if self.grid.y < 20:
                            self.final_executable_commands.pop(endif_index)
                            i += 1
                            continue

                        else:
                            i = endif_index + 1
                            continue

                    case "DOWN":
                        if self.grid.y > 0:
                            self.final_executable_commands.pop(endif_index)
                            i += 1
                            continue

                        else:
                            i = endif_index + 1
                            continue

                    case "RIGHT":
                        if self.grid.x < 20:
                            self.final_executable_commands.pop(endif_index)
                            i += 1
                            continue

                        else:
                            i = endif_index + 1
                            continue

                    case "LEFT":
                        if self.grid.x > 0:
                            self.final_executable_commands.pop(endif_index)
                            i += 1
                            continue

                        else:
                            i = endif_index + 1
                            continue

            i += 1

        return self.coordinates

    def load_file(self, program_file: str) -> None:
        check_file = open(program_file).readline()
        if not check_file.endswith("\n"):
            with open(program_file, "a") as file:
                file.write("\n")

        with open(program_file, "r") as file:
            for line in file:
                if len(line) > 2:
                    self.commands.append(line[:-1].strip())

    def get_cords(self):
        if self.grid:
            return self.grid.get_coords()
        raise errors.ExecuteAtLeastOnce()

    def __str__(self):
        return f"{self.coordinates}"


if __name__ == "__main__":
    program = Interpreter()
    res = program.execute("../test_programs/1.txt")
    print(res)
