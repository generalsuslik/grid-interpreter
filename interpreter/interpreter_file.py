from collections import defaultdict

from interpreter import errors, grid


class Interpreter:
    """
    Class represents simple interpreter. When u run the execute() method,
    the interpreter declares all variables and procedures with get_variables()
    and get_procedures() methods respectively. Then interpreter runs 2
    parse methods,
    to open all loops and procedures calls. After that, it'll have an
    array of all static stuff and if-blocks.
    """

    def __init__(self):
        self.grid = None
        self.force_stop = False
        self.commands = []
        self.executable_commands = []
        self.final_executable_commands = []
        self.functions = defaultdict(list)
        self.variables = {}
        self.coordinates = [(0, 0)]
        self.allowed_commands = ["RIGHT", "LEFT", "UP", "DOWN", "REPEAT", "ENDREPEAT", "IFBLOCK", "ENDIF",
                                 "PROCEDURE", "ENDPROC", "SET"]

    # Variables declaration
    def get_variables(self):
        index = 0
        while index < len(self.commands):
            if self.force_stop:
                return 0
            command = self.commands[index]
            command_split = command.split()
            if command_split[0] == "SET":
                variable_name = command_split[1]
                variable_value = command.split("=")[-1].strip()

                try:

                    variable_value = int(variable_value)
                    self.variables[variable_name] = variable_value

                except ValueError:
                    if isinstance(variable_value, str):

                        if self.variables.get(variable_value) is None:
                            raise errors.NotDeclaredVariableError(
                                f"No such variable: {variable_value}"
                            )

                        else:
                            variable_value = self.variables.get(variable_value)

                        self.variables[variable_name] = variable_value

                self.commands.pop(index)
                continue

            else:
                index += 1

    def get_procedures(self):
        index = 0
        while index < len(self.commands):
            if self.force_stop:
                return 0
            command_split = self.commands[index].split()
            if command_split[0] == "PROCEDURE":
                procedure_name = command_split[1]
                if procedure_name in self.functions.keys():
                    raise errors.ProcedureAlreadyDeclaredError(
                        f"Procedure with name {procedure_name} is already "
                        f"declared"
                    )
                procedure_body = []
                index += 1

                try:
                    while self.commands[index] != "ENDPROC":
                        if not self.commands[index].startswith("CALL"):
                            procedure_body.append(self.commands[index])

                        else:
                            called_procedure = self.functions.get(self.commands[index].split()[1])
                            if called_procedure is None:
                                raise errors.ProcedureNotDeclaredError(
                                    f"Procedure {self.commands[index].split()[1]} was not declared"
                                )

                            for procedure_command in called_procedure:
                                procedure_body.append(procedure_command)

                        index += 1

                except IndexError:
                    raise errors.ProcedureNotClosedError(
                        f"Procedure {procedure_name} was never closed"
                    )

                self.functions[procedure_name] = procedure_body
                index += 1
                continue

            index += 1

    def similar_command(self, command: str) -> str | None:
        for allowed_command in self.allowed_commands:
            if command in allowed_command and command != allowed_command:
                return allowed_command

        return None

    def check_line(self, line: str) -> bool:
        for command in self.allowed_commands:
            if line in command and line != command:
                return True

        return False

    def check_command(self, command):
        command_split = command.split()
        command_title = command_split[0]

        match command_title:
            case "RIGHT" | "LEFT" | "UP" | "DOWN" | "REPEAT" | "PROCEDURE" | "IFBLOCK" | "CALL":
                return len(command_split) == 2

            case "ENDPROC" | "PROCEDURE" | "ENDIF" | "ENDREPEAT":
                return len(command_split) == 1

            case "SET":
                return len(command_split) == 4

        if self.check_line(command_title):
            possible_command = self.similar_command(command_title)
            if possible_command is not None:
                raise errors.NoSuchCommandError(f"No such command: "
                                                f"{command_title}. "
                                                f"Maybe you ment "
                                                f"{possible_command}")

        else:
            raise errors.NoSuchCommandError(f"No such command: "
                                            f"{command_title}")

    def check_commands(self):
        for command_line in self.commands:
            self.check_command(command_line)

    @staticmethod
    def check_repeat_loop_declaration(split_command):
        if len(split_command) != 2:
            raise errors.IncorrectRepeatDeclarationError(
                "Your loop is declared incorrectly. "
                "It must be like: REPEAT <X>"
            )

    @staticmethod
    def check_repeat_loops(commands_array):
        # Check if there is a not closed or not opened repeat cycle error
        count_repeat = 0
        count_endrepeat = 0

        for string in commands_array:
            if string.startswith("REPEAT"):
                count_repeat += 1

            if string.startswith("ENDREPEAT"):
                count_endrepeat += 1

        if count_repeat > count_endrepeat:
            raise errors.RepeatNotClosedError(
                "Your repeat cycle is not closed"
            )

    def first_parse(self, commands_array) -> None | errors.Error:
        index = 0
        self.check_repeat_loops(commands_array)

        while index < len(commands_array):
            if self.force_stop:
                return 0
            command = commands_array[index]
            split_command = command.split()
            # ########################LOOPS##############################
            # 1st loop
            if split_command[0] == "REPEAT":
                self.check_repeat_loop_declaration(split_command)
                n1 = split_command[1]

                check_n1 = None

                try:
                    check_n1 = int(n1)

                except ValueError:
                    if isinstance(n1, str):
                        check_n1 = self.variables.get(n1)
                        if check_n1 is None:
                            raise errors.NotDeclaredVariableError(
                                f"No such variable: {n1}"
                            )

                finally:
                    if check_n1 is None:
                        raise errors.SomethingWentWrongError(
                            "Something went wrong"
                        )

                    n1 = check_n1

                if n1 == 0:
                    raise errors.EndlessRepeatError(
                        "You can't create an endless repeat. "
                        "Change your repeat times number to a "
                        "number more then 0"
                    )

                if n1 < 0:
                    raise errors.IncorrectRepeatDeclarationError(
                        "You can't create a repeat cycle with "
                        "with negative repeat times number"
                    )

                cycle_body1 = []
                index += 1
                while commands_array[index] != "ENDREPEAT":
                    command1 = commands_array[index]
                    split_command1 = command1.split()
                    ################################################
                    # 2 nest loop
                    if split_command1[0] == "REPEAT":
                        self.check_repeat_loop_declaration(split_command1)
                        n2 = split_command1[1]

                        check_n2 = None

                        try:
                            check_n2 = int(n2)

                        except ValueError:
                            if isinstance(n2, str):
                                check_n2 = self.variables.get(n2)
                                if check_n2 is None:
                                    raise errors.NotDeclaredVariableError(
                                        f"No such variable: {n2}"
                                    )

                        finally:
                            if check_n2 is None:
                                raise errors.SomethingWentWrongError(
                                    "Something went wrong"
                                )

                            n2 = check_n2

                        if n2 == 0:
                            raise errors.EndlessRepeatError(
                                "You can't create an endless repeat "
                                "Change your repeat times number to a "
                                "number more then 0"
                            )

                        if n2 < 0:
                            raise errors.IncorrectRepeatDeclarationError(
                                "You can't create a repeat cycle with "
                                "with negative repeat times number"
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
                                self.check_repeat_loop_declaration(split_command2)
                                n3 = split_command[1]

                                check_n3 = None

                                try:
                                    check_n3 = int(n3)

                                except ValueError:
                                    if isinstance(n3, str):
                                        check_n3 = self.variables.get(n3)
                                        if check_n3 is None:
                                            raise errors.NotDeclaredVariableError(
                                                f"No such variable: {n3}"
                                            )

                                finally:
                                    if check_n3 is None:
                                        raise errors.SomethingWentWrongError(
                                            "Something went wrong"
                                        )

                                    n3 = check_n3

                                if n3 == 0:
                                    raise errors.EndlessRepeatError(
                                        "You can't create an endless repeat "
                                        "Change your repeat times number to a "
                                        "number more then 0"
                                    )

                                if n3 < 0:
                                    raise (
                                        errors.
                                        IncorrectRepeatDeclarationError(
                                            "You can't create a repeat cycle "
                                            "with "
                                            "with negative repeat times "
                                            "number"
                                        ))

                                cycle_body3 = []
                                index += 1
                                while commands_array[index] != "ENDREPEAT":
                                    if (
                                            commands_array[index].split()[0] in
                                            ["REPEAT", "CALL", "IFBLOCK"]
                                    ):
                                        raise (
                                            errors.Increasing3NestedCallsError(
                                                "You've increased 3 nested "
                                                "calls rule"
                                            )
                                        )

                                    cycle_body3.append(commands_array[index])
                                    index += 1

                                    if index >= len(commands_array):
                                        raise errors.RepeatNotClosedError(
                                            "Your repeat cycle is not closed"
                                        )

                                # escaping from "ENDREPEAT" in 3rd loop
                                index += 1
                                # Adding elements from 3rd loop
                                # n3 times to 2nd loop's body
                                for _ in range(n3):
                                    for elem in cycle_body3:
                                        if not elem.startswith("CALL"):
                                            cycle_body2.append(elem)

                                        else:
                                            procedure3 = self.functions.get(elem.split()[1])
                                            if procedure3 is None:
                                                raise errors.ProcedureNotDeclaredError(
                                                    f"No such procedure {elem.split()[1]}"
                                                )

                                            for procedure_command3 in procedure3:
                                                cycle_body2.append(procedure_command3)
                                # 3 nest done
                            # ---------------------------------------------#
                            # continuing 2 nest
                            ################################################
                            else:  # We quited 3rd loop, and now we're
                                # able to continue working with 2nd loop
                                cycle_body2.append(commands_array[index])
                                index += 1

                            if index >= len(commands_array):
                                raise errors.RepeatNotClosedError(
                                    "Your repeat cycle is not closed"
                                )

                        index += 1  # escaping from "ENDREPEAT" in 2nd loop
                        # Our 2nd loop has ended. Now we have to
                        # add elements from cycle2 n2 times to cycle1
                        for _ in range(n2):
                            for elem in cycle_body2:
                                if not elem.startswith("CALL"):
                                    cycle_body1.append(elem)

                                else:
                                    procedure2 = self.functions.get(elem.split()[1])
                                    if procedure2 is None:
                                        raise errors.ProcedureNotDeclaredError(
                                            f"No such procedure {elem.split()[1]}"
                                        )

                                    for procedure_command2 in procedure2:
                                        cycle_body1.append(procedure_command2)

                    #####################################################
                    # continuing 1st nest
                    else:  # We quited 2nd loop, and now we're able to
                        # continue working with 1st loop
                        cycle_body1.append(commands_array[index])
                        index += 1

                    if index >= len(commands_array):
                        return errors.RepeatNotClosedError(
                            "Your repeat cycle is not closed"
                        )

                index += 1  # escaping from "ENDREPEAT" in 1st loop
                for _ in range(n1):
                    for elem in cycle_body1:
                        if not elem.startswith("CALL"):
                            self.executable_commands.append(elem)

                        else:
                            procedure = self.functions.get(elem.split()[1])
                            if procedure is None:
                                raise errors.ProcedureNotDeclaredError(
                                    f"No procedure {elem.split()[1]}"
                                )

                            for procedure_command in procedure:
                                self.executable_commands.append(procedure_command)

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

                if procedure_name1 not in self.functions.keys():
                    raise errors.ProcedureNotDeclaredError(
                        f"No procedure with name {procedure_name1}"
                    )

                call_cycle1 = []
                for elem1 in self.functions[procedure_name1]:
                    elem_split1 = elem1.split()
                    # Case we found 2nd func call
                    if elem_split1[0] == "CALL":
                        procedure_name2 = elem_split1[1]

                        if procedure_name2 not in self.functions.keys():
                            raise errors.ProcedureNotDeclaredError(
                                f"No procedure with name {procedure_name2}"
                            )

                        call_cycle2 = []
                        for elem2 in self.functions[procedure_name2]:
                            elem_split2 = elem2.split()
                            # Case we found 3rd procedure call
                            if elem_split2[0] == "CALL":
                                procedure_name3 = elem_split2[1]

                                if (procedure_name3 not in
                                        self.functions.keys()):
                                    raise errors.ProcedureNotDeclaredError(
                                        f"No procedure with name "
                                        f"{procedure_name3}"
                                    )

                                call_cycle3 = []
                                for elem3 in self.functions[procedure_name3]:
                                    if elem3.split()[0] in ["CALL", "REPEAT", "IFBLOCK"]:
                                        raise (
                                            errors.Increasing3NestedCallsError(
                                                "You've increased 3 nested "
                                                "calls rule"
                                            )
                                        )

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
                if self.check_command(command):
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
            if self.force_stop:
                return 0
            command = self.executable_commands[index]
            split_command = command.split()
            # ########################LOOPS##############################
            # 1st loop
            if split_command[0] == "REPEAT":
                self.check_repeat_loop_declaration(split_command)
                n1 = split_command[1]

                check_n1 = None

                try:
                    check_n1 = int(n1)

                except ValueError:
                    if isinstance(n1, str):
                        check_n1 = self.variables.get(n1)
                        if check_n1 is None:
                            raise errors.NotDeclaredVariableError(
                                f"No such variable: {n1}"
                            )

                finally:
                    if check_n1 is None:
                        raise errors.SomethingWentWrongError(
                            "Something went wrong"
                        )

                    n1 = check_n1

                if n1 == 0:
                    raise errors.EndlessRepeatError(
                        "You can't create an endless repeat"
                        "Change your repeat times number to a "
                        "number more then 0"
                    )

                if n1 < 0:
                    raise errors.EndlessRepeatError(
                        "You can't create an endless repeat"
                        "Change your repeat times number to a "
                        "number more then 0"
                    )

                cycle_body1 = []
                index += 1
                while self.executable_commands[index] != "ENDREPEAT":
                    command1 = self.executable_commands[index]
                    split_command1 = command1.split()
                    ########################################################
                    # 2 nest loop
                    if split_command1[0] == "REPEAT":
                        self.check_repeat_loop_declaration(split_command1)
                        n2 = split_command1[1]

                        check_n2 = None

                        try:
                            check_n2 = int(n2)

                        except ValueError:
                            if isinstance(n2, str):
                                check_n2 = self.variables.get(n2)
                                if check_n2 is None:
                                    raise errors.NotDeclaredVariableError(
                                        f"No such variable: {n2}"
                                    )

                        finally:
                            if check_n2 is None:
                                raise errors.SomethingWentWrongError(
                                    "Something went wrong"
                                )

                            n2 = check_n2

                        if n2 == 0:
                            raise errors.EndlessRepeatError(
                                "You can't create an endless repeat"
                                "Change your repeat times number to a "
                                "number more then 0"
                            )

                        if n2 < 0:
                            raise errors.EndlessRepeatError(
                                "You can't create an endless repeat"
                                "Change your repeat times number to a "
                                "number more then 0"
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
                                self.check_repeat_loop_declaration(split_command2)
                                n3 = split_command2[1]

                                check_n3 = None

                                try:
                                    check_n3 = int(n3)

                                except ValueError:
                                    if isinstance(n3, str):
                                        check_n3 = self.variables.get(n3)
                                        if check_n3 is None:
                                            raise errors.NotDeclaredVariableError(
                                                f"No such variable: {n3}"
                                            )

                                finally:
                                    if check_n3 is None:
                                        raise errors.SomethingWentWrongError(
                                            "Something went wrong"
                                        )

                                    n3 = check_n3

                                if n3 == 0:
                                    raise errors.EndlessRepeatError(
                                        "You can't create an endless repeat"
                                        "Change your repeat times number to a "
                                        "number more then 0"
                                    )

                                if n3 < 0:
                                    raise errors.EndlessRepeatError(
                                        "You can't create an endless repeat"
                                        "Change your repeat times number to a "
                                        "number more then 0"
                                    )

                                cycle_body3 = []
                                index += 1
                                this_comm = self.executable_commands[index]
                                while this_comm != "ENDREPEAT":
                                    if (
                                        self.executable_commands[index]. split()[0] in
                                            ["REPEAT", "CALL", "IFBLOCK"]
                                    ):
                                        raise (
                                            errors.
                                            Increasing3NestedCallsError(
                                                "You've increased 3 nested "
                                                "calls rule"
                                            )
                                        )

                                    cycle_body3.append(
                                        self.executable_commands[index]
                                    )

                                    index += 1

                                    if index >= len(self.executable_commands):
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

                                index += 1

                                if index >= len(self.executable_commands):
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

                        index += 1

                        if index >= len(self.executable_commands):
                            raise errors.RepeatNotClosedError(
                                "Your repeat cycle was never closed"
                            )

                index += 1  # escaping from "ENDREPEAT" in 1st loop
                for _ in range(n1):
                    for elem in cycle_body1:
                        self.final_executable_commands.append(elem)

                continue

            # ########################LOOPS#############################
            else:
                if self.check_command(command):
                    self.final_executable_commands.append(command)

            index += 1

    def check_ifblocks(self):
        count_if_blocks = 0
        count_endif_blocks = 0

        for command in self.final_executable_commands:
            if command.startswith("IFBLOCK"):
                count_if_blocks += 1

            if command == "ENDIF":
                count_endif_blocks += 1

        if count_if_blocks > count_endif_blocks:
            raise errors.IFBlockNotClosedError(
                f"{count_if_blocks - count_endif_blocks} of your ifblocks are not closed"
            )

        if count_if_blocks < count_endif_blocks:
            raise errors.WrongSyntaxCommandError(
                "You have wrong syntax with endif"
            )

    def run_commands(self) -> None:
        index = 0
        self.check_ifblocks()
        while index < len(self.final_executable_commands):
            if self.force_stop:
                return 0
            command = self.final_executable_commands[index]
            command_split = command.split()
            if command_split[0] in ["UP", "DOWN", "RIGHT", "LEFT"]:
                times_to_move = command_split[1]

                check_time_to_move = None

                try:
                    check_time_to_move = int(times_to_move)

                except ValueError:
                    check_time_to_move = self.variables.get(times_to_move)
                    if check_time_to_move is None:
                        raise errors.NotDeclaredVariableError(
                            f"Variable {times_to_move} is not declared"
                        )

                finally:
                    if check_time_to_move is None:
                        raise errors.SomethingWentWrongError(
                            "Something went wrong"
                        )

                    times_to_move = int(check_time_to_move)

                    if times_to_move <= 0:
                        raise errors.WrongSyntaxCommandError(
                            f"You can't move {command_split[0]} {times_to_move} times"
                        )

                    self.grid.move(command_split[0], times_to_move)
                    self.coordinates.append(self.grid.get_coords())
                    index += 1
                    continue

            # first ifblock
            # ###################################################################################1
            if command_split[0] == "IFBLOCK":
                block_direction = command_split[1]
                if block_direction is None:
                    raise errors.WrongSyntaxCommandError(
                        "You can't check ifblock without provided direction"
                    )

                index += 1
                if block_direction == "UP":
                    if self.grid.y < 20:
                        while self.final_executable_commands[index] != "ENDIF":
                            index += 1
                        index += 1
                        continue

                    else:
                        command1 = self.final_executable_commands[index]
                        command1_split = command1.split()
                        if command1_split[0] in ["UP", "DOWN", "RIGHT", "LEFT"]:
                            times_to_move1 = command1_split[1]
                            check_times_to_move1 = None

                            try:
                                check_times_to_move1 = int(times_to_move1)

                            except ValueError:
                                check_times_to_move1 = self.variables.get(times_to_move1)
                                if check_times_to_move1 is None:
                                    raise errors.NotDeclaredVariableError(
                                        f"No such variable: {times_to_move1}"
                                    )

                            finally:
                                if check_times_to_move1 is None:
                                    raise errors.SomethingWentWrongError(
                                        "Something went wrong"
                                    )

                                times_to_move1 = check_times_to_move1

                                if times_to_move1 <= 0:
                                    raise errors.WrongSyntaxCommandError(
                                        f"You can't move {command1_split[0]} {times_to_move1} "
                                        f"times"
                                    )

                                self.grid.move(command1_split[0], times_to_move1)
                                self.coordinates.append(self.grid.get_coords())
                                index += 1
                                continue

                        # first ifblock up -> second ifblock
                        # #######################################################################2
                        elif command1_split[0] == "IFBLOCK":
                            block_direction1 = command1_split[1]
                            if block_direction1 is None:
                                raise errors.WrongSyntaxCommandError(
                                    "You can't check ifblock without provided direction"
                                )

                            index += 1
                            # first ifblock up -> second ifblock up
                            if block_direction1 == "UP":
                                if self.grid.y < 20:
                                    while self.final_executable_commands[index] != "ENDIF":
                                        index += 1
                                    index += 1
                                    continue

                                else:
                                    command2 = self.final_executable_commands[index]
                                    command2_split = command2.split()
                                    if command2_split[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                        times_to_move2 = command2_split[1]
                                        check_times_to_move2 = None

                                        try:
                                            check_times_to_move2 = int(times_to_move2)

                                        except ValueError:
                                            check_times_to_move2 = (
                                                self.variables.get(times_to_move2))

                                            if check_times_to_move2 is None:
                                                raise errors.NotDeclaredVariableError(
                                                    f"No such variable: {times_to_move2}"
                                                )

                                        finally:
                                            if check_times_to_move2 is None:
                                                raise errors.SomethingWentWrongError(
                                                    "Something went wrong"
                                                )

                                            times_to_move2 = check_times_to_move2

                                            if times_to_move2 <= 0:
                                                raise errors.WrongSyntaxCommandError(
                                                    f"You can't move {command2_split[0]} "
                                                    f"{times_to_move2} "
                                                    f"times"
                                                )

                                            self.grid.move(command2_split[0], times_to_move2)
                                            self.coordinates.append(self.grid.get_coords())
                                            index += 1
                                            continue

                                    # first ifblock up -> second ifblock up -> third ifblock
                                    # ###########################################################3
                                    elif command2_split[0] == "IFBLOCK":
                                        block_direction2 = command2_split[2]
                                        if block_direction2 is None:
                                            raise errors.WrongSyntaxCommandError(
                                                "You can't check ifblock without provided "
                                                "direction"
                                            )

                                        index += 1
                                        # first ifblock up -> second ifblock up ->
                                        # third ifblock up
                                        if block_direction2 == "UP":
                                            if self.grid.y < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: "
                                                                f"{times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0],
                                                                       times_to_move3)
                                                        self.coordinates.append(
                                                            self.grid.get_coords()
                                                        )
                                                        index += 1
                                                        continue

                                                elif command3_split[0] == ["IFBLOCK",
                                                                           "CALL", "REPEAT"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock up -> second ifblock up ->
                                        # third ifblock down
                                        if block_direction2 == "DOWN":
                                            if self.grid.y > 0:
                                                while (self.final_executable_commands[index]
                                                       != "ENDIF"):
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: "
                                                                f"{times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock up -> second ifblock up ->
                                        # third ifblock right
                                        if block_direction2 == "RIGHT":
                                            if self.grid.x < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: "
                                                                f"{times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["IFBLOCK", "CALL",
                                                                           "REPEAT"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock up -> second ifblock up ->
                                        # third ifblock left
                                        if block_direction2 == "LEFT":
                                            if self.grid.x > 0:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["IFBLOCK", "REPEAT",
                                                                           "CALL"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                            # first ifblock up -> second ifblock down
                            if block_direction1 == "DOWN":
                                if self.grid.y > 0:
                                    while self.final_executable_commands[index] != "ENDIF":
                                        index += 1
                                    index += 1
                                    continue

                                else:
                                    command2 = self.final_executable_commands[index]
                                    command2_split = command2.split()
                                    if command2_split[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                        times_to_move2 = command2_split[1]
                                        check_times_to_move2 = None

                                        try:
                                            check_times_to_move2 = int(times_to_move2)

                                        except ValueError:
                                            check_times_to_move2 = (
                                                self.variables.get(times_to_move2))

                                            if check_times_to_move2 is None:
                                                raise errors.NotDeclaredVariableError(
                                                    f"No such variable: {times_to_move2}"
                                                )

                                        finally:
                                            if check_times_to_move2 is None:
                                                raise errors.SomethingWentWrongError(
                                                    "Something went wrong"
                                                )

                                            times_to_move2 = check_times_to_move2

                                            if times_to_move2 <= 0:
                                                raise errors.WrongSyntaxCommandError(
                                                    f"You can't move {command2_split[0]} "
                                                    f"{times_to_move2} "
                                                    f"times"
                                                )

                                            self.grid.move(command2_split[0], times_to_move2)
                                            self.coordinates.append(self.grid.get_coords())
                                            index += 1
                                            continue

                                    # first ifblock up -> second ifblock up -> third ifblock
                                    # ###########################################################3
                                    elif command2_split[0] == "IFBLOCK":
                                        block_direction2 = command2_split[2]
                                        if block_direction2 is None:
                                            raise errors.WrongSyntaxCommandError(
                                                "You can't check ifblock without provided "
                                                "direction"
                                            )

                                        index += 1
                                        # first ifblock up -> second ifblock up ->
                                        # third ifblock up
                                        if block_direction2 == "UP":
                                            if self.grid.y < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: "
                                                                f"{times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0],
                                                                       times_to_move3)
                                                        self.coordinates.append(
                                                            self.grid.get_coords()
                                                        )
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["IFBLOCK", "CALL", "REPEAT"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock up -> second ifblock up ->
                                        # third ifblock down
                                        if block_direction2 == "DOWN":
                                            if self.grid.y > 0:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: "
                                                                f"{times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0],
                                                                       times_to_move3)
                                                        self.coordinates.append(
                                                            self.grid.get_coords()
                                                        )
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["IFBLOCK", "CALL", "REPEAT"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock up -> second ifblock up ->
                                        # third ifblock right
                                        if block_direction2 == "RIGHT":
                                            if self.grid.x < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: "
                                                                f"{times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0],
                                                                       times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["IFBLOCK", "CALL", "REPEAT"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock up -> second ifblock up ->
                                        # third ifblock left
                                        if block_direction2 == "LEFT":
                                            if self.grid.x > 0:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: "
                                                                f"{times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["IFBLOCK", "CALL",
                                                                           "REPEAT"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                            # first ifblock up -> second ifblock right
                            if block_direction1 == "RIGHT":
                                if self.grid.x < 20:
                                    while self.final_executable_commands[index] != "ENDIF":
                                        index += 1
                                    index += 1
                                    continue

                                else:
                                    command2 = self.final_executable_commands[index]
                                    command2_split = command2.split()
                                    if command2_split[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                        times_to_move2 = command2_split[1]
                                        check_times_to_move2 = None

                                        try:
                                            check_times_to_move2 = int(times_to_move2)

                                        except ValueError:
                                            check_times_to_move2 = (
                                                self.variables.get(times_to_move2))

                                            if check_times_to_move2 is None:
                                                raise errors.NotDeclaredVariableError(
                                                    f"No such variable: {times_to_move2}"
                                                )

                                        finally:
                                            if check_times_to_move2 is None:
                                                raise errors.SomethingWentWrongError(
                                                    "Something went wrong"
                                                )

                                            times_to_move2 = check_times_to_move2

                                            if times_to_move2 <= 0:
                                                raise errors.WrongSyntaxCommandError(
                                                    f"You can't move {command2_split[0]} "
                                                    f"{times_to_move2} "
                                                    f"times"
                                                )

                                            self.grid.move(command2_split[0], times_to_move2)
                                            self.coordinates.append(self.grid.get_coords())
                                            index += 1
                                            continue

                                    # first ifblock up -> second ifblock right -> third ifblock
                                    # ###########################################################3
                                    elif command2_split[0] == "IFBLOCK":
                                        block_direction2 = command2_split[2]
                                        if block_direction2 is None:
                                            raise errors.WrongSyntaxCommandError(
                                                "You can't check ifblock without provided "
                                                "direction"
                                            )

                                        index += 1
                                        # first ifblock up -> second ifblock right ->
                                        # third ifblock up
                                        if block_direction2 == "UP":
                                            if self.grid.y < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["IFBLOCK", "CALL", "REPEAT"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock up -> second ifblock right ->
                                        # third ifblock down
                                        if block_direction2 == "DOWN":
                                            if self.grid.y > 0:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: "
                                                                f"{times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0],
                                                                       times_to_move3)
                                                        self.coordinates.append(
                                                            self.grid.get_coords()
                                                        )
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL", "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock up -> second ifblock right ->
                                        # third ifblock right
                                        if block_direction2 == "RIGHT":
                                            if self.grid.x < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL", "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock up -> second ifblock right ->
                                        # third ifblock left
                                        if block_direction2 == "LEFT":
                                            if self.grid.x > 0:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL", "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                            # first ifblock up -> second ifblock left
                            if block_direction1 == "LEFT":
                                if self.grid.x > 0:
                                    while self.final_executable_commands[index] != "ENDIF":
                                        index += 1
                                    index += 1
                                    continue

                                else:
                                    command2 = self.final_executable_commands[index]
                                    command2_split = command2.split()
                                    if command2_split[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                        times_to_move2 = command2_split[1]
                                        check_times_to_move2 = None

                                        try:
                                            check_times_to_move2 = int(times_to_move2)

                                        except ValueError:
                                            check_times_to_move2 = (
                                                self.variables.get(times_to_move2))

                                            if check_times_to_move2 is None:
                                                raise errors.NotDeclaredVariableError(
                                                    f"No such variable: {times_to_move2}"
                                                )

                                        finally:
                                            if check_times_to_move2 is None:
                                                raise errors.SomethingWentWrongError(
                                                    "Something went wrong"
                                                )

                                            times_to_move2 = check_times_to_move2

                                            if times_to_move2 <= 0:
                                                raise errors.WrongSyntaxCommandError(
                                                    f"You can't move {command2_split[0]} "
                                                    f"{times_to_move2} "
                                                    f"times"
                                                )

                                            self.grid.move(command2_split[0], times_to_move2)
                                            self.coordinates.append(self.grid.get_coords())
                                            index += 1
                                            continue

                                    # first ifblock up -> second ifblock left ->
                                    # third ifblock
                                    # ###########################################################3
                                    elif command2_split[0] == "IFBLOCK":
                                        block_direction2 = command2_split[2]
                                        if block_direction2 is None:
                                            raise errors.WrongSyntaxCommandError(
                                                "You can't check ifblock without provided "
                                                "direction"
                                            )

                                        index += 1
                                        # first ifblock up -> second ifblock left ->
                                        # third ifblock up
                                        if block_direction2 == "UP":
                                            if self.grid.y < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock up -> second ifblock left ->
                                        # third ifblock down
                                        if block_direction2 == "DOWN":
                                            if self.grid.y > 0:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: "
                                                                f"{times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0],
                                                                       times_to_move3)
                                                        self.coordinates.append(
                                                            self.grid.get_coords()
                                                        )
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL", "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock up -> second ifblock left ->
                                        # third ifblock right
                                        if block_direction2 == "RIGHT":
                                            if self.grid.x < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock up -> second ifblock left ->
                                        # third ifblock left
                                        if block_direction2 == "LEFT":
                                            if self.grid.x > 0:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                #  continuing first ifblock down
                # ###############################################################################1
                if block_direction == "DOWN":
                    if self.grid.y > 0:
                        while self.final_executable_commands[index] != "ENDIF":
                            index += 1
                        index += 1
                        continue

                    else:
                        command1 = self.final_executable_commands[index]
                        command1_split = command1.split()
                        if command1_split[0] in ["UP", "DOWN", "RIGHT", "LEFT"]:
                            times_to_move1 = command1_split[1]
                            check_times_to_move1 = None

                            try:
                                check_times_to_move1 = int(times_to_move1)

                            except ValueError:
                                check_times_to_move1 = self.variables.get(times_to_move1)
                                if check_times_to_move1 is None:
                                    raise errors.NotDeclaredVariableError(
                                        f"No such variable: {times_to_move1}"
                                    )

                            finally:
                                if check_times_to_move1 is None:
                                    raise errors.SomethingWentWrongError(
                                        "Something went wrong"
                                    )

                                times_to_move1 = check_times_to_move1

                                if times_to_move1 <= 0:
                                    raise errors.WrongSyntaxCommandError(
                                        f"You can't move {command1_split[0]} {times_to_move1} "
                                        f"times"
                                    )

                                self.grid.move(command1_split[0], times_to_move1)
                                self.coordinates.append(self.grid.get_coords())
                                index += 1
                                continue

                        # first ifblock down -> second ifblock
                        # #######################################################################2
                        elif command1_split[0] == "IFBLOCK":
                            block_direction1 = command1_split[1]
                            if block_direction1 is None:
                                raise errors.WrongSyntaxCommandError(
                                    "You can't check ifblock without provided direction"
                                )

                            index += 1
                            # first ifblock down -> second ifblock up
                            if block_direction1 == "UP":
                                if self.grid.y < 20:
                                    while self.final_executable_commands[index] != "ENDIF":
                                        index += 1
                                    index += 1
                                    continue

                                else:
                                    command2 = self.final_executable_commands[index]
                                    command2_split = command2.split()
                                    if command2_split[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                        times_to_move2 = command2_split[1]
                                        check_times_to_move2 = None

                                        try:
                                            check_times_to_move2 = int(times_to_move2)

                                        except ValueError:
                                            check_times_to_move2 = (
                                                self.variables.get(times_to_move2))

                                            if check_times_to_move2 is None:
                                                raise errors.NotDeclaredVariableError(
                                                    f"No such variable: {times_to_move2}"
                                                )

                                        finally:
                                            if check_times_to_move2 is None:
                                                raise errors.SomethingWentWrongError(
                                                    "Something went wrong"
                                                )

                                            times_to_move2 = check_times_to_move2

                                            if times_to_move2 <= 0:
                                                raise errors.WrongSyntaxCommandError(
                                                    f"You can't move {command2_split[0]} "
                                                    f"{times_to_move2} "
                                                    f"times"
                                                )

                                            self.grid.move(command2_split[0], times_to_move2)
                                            self.coordinates.append(self.grid.get_coords())
                                            index += 1
                                            continue

                                    # first ifblock down -> second ifblock up ->
                                    # third ifblock
                                    # ###########################################################3
                                    elif command2_split[0] == "IFBLOCK":
                                        block_direction2 = command2_split[2]
                                        if block_direction2 is None:
                                            raise errors.WrongSyntaxCommandError(
                                                "You can't check ifblock without provided "
                                                "direction"
                                            )

                                        index += 1
                                        # first ifblock down -> second ifblock up ->
                                        # third ifblock up
                                        if block_direction2 == "UP":
                                            if self.grid.y < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL", "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock down -> second ifblock up ->
                                        # third ifblock down
                                        if block_direction2 == "DOWN":
                                            if self.grid.y > 0:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: "
                                                                f"{times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0],
                                                                       times_to_move3)
                                                        self.coordinates.append(
                                                            self.grid.get_coords()
                                                        )
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock down -> second ifblock up ->
                                        # third ifblock right
                                        if block_direction2 == "RIGHT":
                                            if self.grid.x < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL", "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock down -> second ifblock up ->
                                        # third ifblock left
                                        if block_direction2 == "LEFT":
                                            if self.grid.x > 0:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL", "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                            # first ifblock down -> second ifblock down
                            if block_direction1 == "DOWN":
                                if self.grid.y > 0:
                                    while self.final_executable_commands[index] != "ENDIF":
                                        index += 1
                                    index += 1
                                    continue

                                else:
                                    command2 = self.final_executable_commands[index]
                                    command2_split = command2.split()
                                    if command2_split[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                        times_to_move2 = command2_split[1]
                                        check_times_to_move2 = None

                                        try:
                                            check_times_to_move2 = int(times_to_move2)

                                        except ValueError:
                                            check_times_to_move2 = (
                                                self.variables.get(times_to_move2))

                                            if check_times_to_move2 is None:
                                                raise errors.NotDeclaredVariableError(
                                                    f"No such variable: {times_to_move2}"
                                                )

                                        finally:
                                            if check_times_to_move2 is None:
                                                raise errors.SomethingWentWrongError(
                                                    "Something went wrong"
                                                )

                                            times_to_move2 = check_times_to_move2

                                            if times_to_move2 <= 0:
                                                raise errors.WrongSyntaxCommandError(
                                                    f"You can't move {command2_split[0]} "
                                                    f"{times_to_move2} "
                                                    f"times"
                                                )

                                            self.grid.move(command2_split[0], times_to_move2)
                                            self.coordinates.append(self.grid.get_coords())
                                            index += 1
                                            continue

                                    # first ifblock down -> second ifblock down ->
                                    # third ifblock
                                    # ###########################################################3
                                    elif command2_split[0] == "IFBLOCK":
                                        block_direction2 = command2_split[2]
                                        if block_direction2 is None:
                                            raise errors.WrongSyntaxCommandError(
                                                "You can't check ifblock without provided "
                                                "direction"
                                            )

                                        index += 1
                                        # first ifblock down -> second ifblock down ->
                                        # third ifblock up
                                        if block_direction2 == "UP":
                                            if self.grid.y < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL", "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock down -> second ifblock down ->
                                        # third ifblock down
                                        if block_direction2 == "DOWN":
                                            if self.grid.y > 0:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: "
                                                                f"{times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0],
                                                                       times_to_move3)
                                                        self.coordinates.append(
                                                            self.grid.get_coords()
                                                        )
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL", "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock down -> second ifblock down ->
                                        # third ifblock right
                                        if block_direction2 == "RIGHT":
                                            if self.grid.x < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock down -> second ifblock down ->
                                        # third ifblock left
                                        if block_direction2 == "LEFT":
                                            if self.grid.x > 0:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: "
                                                                f"{times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0],
                                                                       times_to_move3)
                                                        self.coordinates.append(
                                                            self.grid.get_coords()
                                                        )
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                            # first ifblock down -> second ifblock right
                            if block_direction1 == "RIGHT":
                                if self.grid.x < 20:
                                    while self.final_executable_commands[index] != "ENDIF":
                                        index += 1
                                    index += 1
                                    continue

                                else:
                                    command2 = self.final_executable_commands[index]
                                    command2_split = command2.split()
                                    if command2_split[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                        times_to_move2 = command2_split[1]
                                        check_times_to_move2 = None

                                        try:
                                            check_times_to_move2 = int(times_to_move2)

                                        except ValueError:
                                            check_times_to_move2 = (
                                                self.variables.get(times_to_move2))

                                            if check_times_to_move2 is None:
                                                raise errors.NotDeclaredVariableError(
                                                    f"No such variable: {times_to_move2}"
                                                )

                                        finally:
                                            if check_times_to_move2 is None:
                                                raise errors.SomethingWentWrongError(
                                                    "Something went wrong"
                                                )

                                            times_to_move2 = check_times_to_move2

                                            if times_to_move2 <= 0:
                                                raise errors.WrongSyntaxCommandError(
                                                    f"You can't move {command2_split[0]} "
                                                    f"{times_to_move2} "
                                                    f"times"
                                                )

                                            self.grid.move(command2_split[0], times_to_move2)
                                            self.coordinates.append(self.grid.get_coords())
                                            index += 1
                                            continue

                                    # first ifblock down -> second ifblock right ->
                                    # third ifblock
                                    # ###########################################################3
                                    elif command2_split[0] == "IFBLOCK":
                                        block_direction2 = command2_split[2]
                                        if block_direction2 is None:
                                            raise errors.WrongSyntaxCommandError(
                                                "You can't check ifblock without provided "
                                                "direction"
                                            )

                                        index += 1
                                        # first ifblock down -> second ifblock right ->
                                        # third ifblock up
                                        if block_direction2 == "UP":
                                            if self.grid.y < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0],
                                                                       times_to_move3)
                                                        self.coordinates.append(
                                                            self.grid.get_coords()
                                                        )
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock down -> second ifblock right ->
                                        # third ifblock down
                                        if block_direction2 == "DOWN":
                                            if self.grid.y > 0:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: "
                                                                f"{times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0],
                                                                       times_to_move3)
                                                        self.coordinates.append(
                                                            self.grid.get_coords()
                                                        )
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # ffirst ifblock down -> second ifblock right ->
                                        # third ifblock right
                                        if block_direction2 == "RIGHT":
                                            if self.grid.x < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock down -> second ifblock right ->
                                        # third ifblock left
                                        if block_direction2 == "LEFT":
                                            if self.grid.x > 0:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                            # first ifblock down -> second ifblock left
                            if block_direction1 == "LEFT":
                                if self.grid.x > 0:
                                    while self.final_executable_commands[index] != "ENDIF":
                                        index += 1
                                    index += 1
                                    continue

                                else:
                                    command2 = self.final_executable_commands[index]
                                    command2_split = command2.split()
                                    if command2_split[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                        times_to_move2 = command2_split[1]
                                        check_times_to_move2 = None

                                        try:
                                            check_times_to_move2 = int(times_to_move2)

                                        except ValueError:
                                            check_times_to_move2 = (
                                                self.variables.get(times_to_move2))

                                            if check_times_to_move2 is None:
                                                raise errors.NotDeclaredVariableError(
                                                    f"No such variable: {times_to_move2}"
                                                )

                                        finally:
                                            if check_times_to_move2 is None:
                                                raise errors.SomethingWentWrongError(
                                                    "Something went wrong"
                                                )

                                            times_to_move2 = check_times_to_move2

                                            if times_to_move2 <= 0:
                                                raise errors.WrongSyntaxCommandError(
                                                    f"You can't move {command2_split[0]} "
                                                    f"{times_to_move2} "
                                                    f"times"
                                                )

                                            self.grid.move(command2_split[0], times_to_move2)
                                            self.coordinates.append(self.grid.get_coords())
                                            index += 1
                                            continue

                                    # first ifblock down -> second ifblock left ->
                                    # third ifblock
                                    # ###########################################################3
                                    elif command2_split[0] == "IFBLOCK":
                                        block_direction2 = command2_split[2]
                                        if block_direction2 is None:
                                            raise errors.WrongSyntaxCommandError(
                                                "You can't check ifblock without provided "
                                                "direction"
                                            )

                                        index += 1
                                        # first ifblock down -> second ifblock left ->
                                        # third ifblock up
                                        if block_direction2 == "UP":
                                            if self.grid.y < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: "
                                                                f"{times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0],
                                                                       times_to_move3)
                                                        self.coordinates.append(
                                                            self.grid.get_coords()
                                                        )
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock down -> second ifblock left ->
                                        # third ifblock down
                                        if block_direction2 == "DOWN":
                                            if self.grid.y > 0:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: "
                                                                f"{times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0],
                                                                       times_to_move3)
                                                        self.coordinates.append(
                                                            self.grid.get_coords()
                                                        )
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # ffirst ifblock down -> second ifblock left ->
                                        # third ifblock right
                                        if block_direction2 == "RIGHT":
                                            if self.grid.x < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: "
                                                                f"{times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock down -> second ifblock left ->
                                        # third ifblock left
                                        if block_direction2 == "LEFT":
                                            if self.grid.x > 0:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                # continuing first ifblock right
                if block_direction == "RIGHT":
                    if self.grid.x < 20:
                        while self.final_executable_commands[index] != "ENDIF":
                            index += 1
                        index += 1
                        continue

                    else:
                        command1 = self.final_executable_commands[index]
                        command1_split = command1.split()
                        if command1_split[0] in ["UP", "DOWN", "RIGHT", "LEFT"]:
                            times_to_move1 = command1_split[1]
                            check_times_to_move1 = None

                            try:
                                check_times_to_move1 = int(times_to_move1)

                            except ValueError:
                                check_times_to_move1 = self.variables.get(times_to_move1)
                                if check_times_to_move1 is None:
                                    raise errors.NotDeclaredVariableError(
                                        f"No such variable: {times_to_move1}"
                                    )

                            finally:
                                if check_times_to_move1 is None:
                                    raise errors.SomethingWentWrongError(
                                        "Something went wrong"
                                    )

                                times_to_move1 = check_times_to_move1

                                if times_to_move1 <= 0:
                                    raise errors.WrongSyntaxCommandError(
                                        f"You can't move {command1_split[0]} {times_to_move1} "
                                        f"times"
                                    )

                                self.grid.move(command1_split[0], times_to_move1)
                                self.coordinates.append(self.grid.get_coords())
                                index += 1
                                continue

                        # first ifblock right -> second ifblock
                        # ########################################################################
                        elif command1_split[0] == "IFBLOCK":
                            block_direction1 = command1_split[1]
                            if block_direction1 is None:
                                raise errors.WrongSyntaxCommandError(
                                    "You can't check ifblock without provided direction"
                                )

                            index += 1

                            # first ifblock right -> second ifblock up
                            if block_direction1 == "UP":
                                if self.grid.y < 20:
                                    while self.final_executable_commands[index] != "ENDIF":
                                        index += 1
                                    index += 1
                                    continue

                                else:
                                    command2 = self.final_executable_commands[index]
                                    command2_split = command2.split()
                                    if command2_split[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                        times_to_move2 = command2_split[1]
                                        check_times_to_move2 = None

                                        try:
                                            check_times_to_move2 = int(times_to_move2)

                                        except ValueError:
                                            check_times_to_move2 = (
                                                self.variables.get(times_to_move2))

                                            if check_times_to_move2 is None:
                                                raise errors.NotDeclaredVariableError(
                                                    f"No such variable: {times_to_move2}"
                                                )

                                        finally:
                                            if check_times_to_move2 is None:
                                                raise errors.SomethingWentWrongError(
                                                    "Something went wrong"
                                                )

                                            times_to_move2 = check_times_to_move2

                                            if times_to_move2 <= 0:
                                                raise errors.WrongSyntaxCommandError(
                                                    f"You can't move {command2_split[0]} "
                                                    f"{times_to_move2} "
                                                    f"times"
                                                )

                                            self.grid.move(command2_split[0], times_to_move2)
                                            self.coordinates.append(self.grid.get_coords())
                                            index += 1
                                            continue

                                    # first ifblock right -> second ifblock up ->
                                    # third ifblock
                                    # ###########################################################3
                                    elif command2_split[0] == "IFBLOCK":
                                        block_direction2 = command2_split[2]
                                        if block_direction2 is None:
                                            raise errors.WrongSyntaxCommandError(
                                                "You can't check ifblock without provided "
                                                "direction"
                                            )

                                        index += 1
                                        # first ifblock right -> second ifblock up ->
                                        # third ifblock up
                                        if block_direction2 == "UP":
                                            if self.grid.y < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock right -> second ifblock up ->
                                        # third ifblock down
                                        if block_direction2 == "DOWN":
                                            if self.grid.y > 0:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: "
                                                                f"{times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0],
                                                                       times_to_move3)
                                                        self.coordinates.append(
                                                            self.grid.get_coords()
                                                        )
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock right -> second ifblock up ->
                                        # third ifblock right
                                        if block_direction2 == "RIGHT":
                                            if self.grid.x < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: "
                                                                f"{times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock right -> second ifblock up ->
                                        # third ifblock left
                                        if block_direction2 == "LEFT":
                                            if self.grid.x > 0:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                            # first ifblock right -> second ifblock down
                            if block_direction1 == "DOWN":
                                if self.grid.y > 0:
                                    while self.final_executable_commands[index] != "ENDIF":
                                        index += 1
                                    index += 1
                                    continue

                                else:
                                    command2 = self.final_executable_commands[index]
                                    command2_split = command2.split()
                                    if command2_split[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                        times_to_move2 = command2_split[1]
                                        check_times_to_move2 = None

                                        try:
                                            check_times_to_move2 = int(times_to_move2)

                                        except ValueError:
                                            check_times_to_move2 = (
                                                self.variables.get(times_to_move2))

                                            if check_times_to_move2 is None:
                                                raise errors.NotDeclaredVariableError(
                                                    f"No such variable: {times_to_move2}"
                                                )

                                        finally:
                                            if check_times_to_move2 is None:
                                                raise errors.SomethingWentWrongError(
                                                    "Something went wrong"
                                                )

                                            times_to_move2 = check_times_to_move2

                                            if times_to_move2 <= 0:
                                                raise errors.WrongSyntaxCommandError(
                                                    f"You can't move {command2_split[0]} "
                                                    f"{times_to_move2} "
                                                    f"times"
                                                )

                                            self.grid.move(command2_split[0], times_to_move2)
                                            self.coordinates.append(self.grid.get_coords())
                                            index += 1
                                            continue

                                    # first ifblock right -> second ifblock down ->
                                    # third ifblock
                                    # ###########################################################3
                                    elif command2_split[0] == "IFBLOCK":
                                        block_direction2 = command2_split[2]
                                        if block_direction2 is None:
                                            raise errors.WrongSyntaxCommandError(
                                                "You can't check ifblock without provided "
                                                "direction"
                                            )

                                        index += 1
                                        # first ifblock right -> second ifblock down ->
                                        # third ifblock up
                                        if block_direction2 == "UP":
                                            if self.grid.y < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock right -> second ifblock down ->
                                        # third ifblock down
                                        if block_direction2 == "DOWN":
                                            if self.grid.y > 0:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: "
                                                                f"{times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0],
                                                                       times_to_move3)
                                                        self.coordinates.append(
                                                            self.grid.get_coords()
                                                        )
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock right -> second ifblock down ->
                                        # third ifblock right
                                        if block_direction2 == "RIGHT":
                                            if self.grid.x < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock right -> second ifblock down ->
                                        # third ifblock left
                                        if block_direction2 == "LEFT":
                                            if self.grid.x > 0:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: "
                                                                f"{times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                            # first ifblock right -> second ifblock right
                            if not block_direction1 == "RIGHT":
                                if self.grid.x < 20:
                                    while self.final_executable_commands[index] != "ENDIF":
                                        index += 1
                                    index += 1
                                    continue

                                else:
                                    command2 = self.final_executable_commands[index]
                                    command2_split = command2.split()
                                    if command2_split[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                        times_to_move2 = command2_split[1]
                                        check_times_to_move2 = None

                                        try:
                                            check_times_to_move2 = int(times_to_move2)

                                        except ValueError:
                                            check_times_to_move2 = (
                                                self.variables.get(times_to_move2))

                                            if check_times_to_move2 is None:
                                                raise errors.NotDeclaredVariableError(
                                                    f"No such variable: {times_to_move2}"
                                                )

                                        finally:
                                            if check_times_to_move2 is None:
                                                raise errors.SomethingWentWrongError(
                                                    "Something went wrong"
                                                )

                                            times_to_move2 = check_times_to_move2

                                            if times_to_move2 <= 0:
                                                raise errors.WrongSyntaxCommandError(
                                                    f"You can't move {command2_split[0]} "
                                                    f"{times_to_move2} "
                                                    f"times"
                                                )

                                            self.grid.move(command2_split[0], times_to_move2)
                                            self.coordinates.append(self.grid.get_coords())
                                            index += 1
                                            continue

                                    # first ifblock right -> second ifblock right ->
                                    # third ifblock
                                    # ###########################################################3
                                    elif command2_split[0] == "IFBLOCK":
                                        block_direction2 = command2_split[2]
                                        if block_direction2 is None:
                                            raise errors.WrongSyntaxCommandError(
                                                "You can't check ifblock without provided "
                                                "direction"
                                            )

                                        index += 1
                                        # first ifblock right -> second ifblock right ->
                                        # third ifblock up
                                        if block_direction2 == "UP":
                                            if self.grid.y < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock right -> second ifblock right ->
                                        # third ifblock down
                                        if block_direction2 == "DOWN":
                                            if self.grid.y > 0:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: "
                                                                f"{times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0],
                                                                       times_to_move3)
                                                        self.coordinates.append(
                                                            self.grid.get_coords()
                                                        )
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock right -> second ifblock right ->
                                        # third ifblock right
                                        if block_direction2 == "RIGHT":
                                            if self.grid.x < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock right -> second ifblock right ->
                                        # third ifblock left
                                        if block_direction2 == "LEFT":
                                            if self.grid.x > 0:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                            # first ifblock right -> second ifblock left
                            if not block_direction1 == "LEFT":
                                if self.grid.x > 0:
                                    while self.final_executable_commands[index] != "ENDIF":
                                        index += 1
                                    index += 1
                                    continue

                                else:
                                    command2 = self.final_executable_commands[index]
                                    command2_split = command2.split()
                                    if command2_split[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                        times_to_move2 = command2_split[1]
                                        check_times_to_move2 = None

                                        try:
                                            check_times_to_move2 = int(times_to_move2)

                                        except ValueError:
                                            check_times_to_move2 = (
                                                self.variables.get(times_to_move2))

                                            if check_times_to_move2 is None:
                                                raise errors.NotDeclaredVariableError(
                                                    f"No such variable: {times_to_move2}"
                                                )

                                        finally:
                                            if check_times_to_move2 is None:
                                                raise errors.SomethingWentWrongError(
                                                    "Something went wrong"
                                                )

                                            times_to_move2 = check_times_to_move2

                                            if times_to_move2 <= 0:
                                                raise errors.WrongSyntaxCommandError(
                                                    f"You can't move {command2_split[0]} "
                                                    f"{times_to_move2} "
                                                    f"times"
                                                )

                                            self.grid.move(command2_split[0], times_to_move2)
                                            self.coordinates.append(self.grid.get_coords())
                                            index += 1
                                            continue

                                    # first ifblock right -> second ifblock left ->
                                    # third ifblock
                                    # ###########################################################3
                                    elif command2_split[0] == "IFBLOCK":
                                        block_direction2 = command2_split[2]
                                        if block_direction2 is None:
                                            raise errors.WrongSyntaxCommandError(
                                                "You can't check ifblock without provided "
                                                "direction"
                                            )

                                        index += 1
                                        # first ifblock right -> second ifblock left ->
                                        # third ifblock up
                                        if block_direction2 == "UP":
                                            if self.grid.y < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: "
                                                                f"{times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock right -> second ifblock left ->
                                        # third ifblock down
                                        if block_direction2 == "DOWN":
                                            if self.grid.y > 0:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: "
                                                                f"{times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0],
                                                                       times_to_move3)
                                                        self.coordinates.append(
                                                            self.grid.get_coords()
                                                        )
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock right -> second ifblock left ->
                                        # third ifblock right
                                        if block_direction2 == "RIGHT":
                                            if self.grid.x < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock right -> second ifblock left ->
                                        # third ifblock left
                                        if block_direction2 == "LEFT":
                                            if self.grid.x > 0:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                # continuing first ifblock left
                if block_direction == "LEFT":
                    if self.grid.x > 0:
                        while self.final_executable_commands[index] != "ENDIF":
                            index += 1
                        index += 1
                        continue

                    else:
                        command1 = self.final_executable_commands[index]
                        command1_split = command1.split()
                        if command1_split[0] in ["UP", "DOWN", "RIGHT", "LEFT"]:
                            times_to_move1 = command1_split[1]
                            check_times_to_move1 = None

                            try:
                                check_times_to_move1 = int(times_to_move1)

                            except ValueError:
                                check_times_to_move1 = self.variables.get(times_to_move1)
                                if check_times_to_move1 is None:
                                    raise errors.NotDeclaredVariableError(
                                        f"No such variable: {times_to_move1}"
                                    )

                            finally:
                                if check_times_to_move1 is None:
                                    raise errors.SomethingWentWrongError(
                                        "Something went wrong"
                                    )

                                times_to_move1 = check_times_to_move1

                                if times_to_move1 <= 0:
                                    raise errors.WrongSyntaxCommandError(
                                        f"You can't move {command1_split[0]} {times_to_move1} "
                                        f"times"
                                    )

                                self.grid.move(command1_split[0], times_to_move1)
                                self.coordinates.append(self.grid.get_coords())
                                index += 1
                                continue

                        # first ifblock left -> second ifblock
                        # ########################################################################
                        elif command1_split[0] == "IFBLOCK":
                            block_direction1 = command1_split[1]
                            if block_direction1 is None:
                                raise errors.WrongSyntaxCommandError(
                                    "You can't check ifblock without provided direction"
                                )

                            index += 1
                            # first ifblock left -> second ifblock ->
                            # second ifblock up
                            if block_direction1 == "UP":
                                if self.grid.y < 20:
                                    while self.final_executable_commands[index] != "ENDIF":
                                        index += 1
                                    index += 1
                                    continue

                                else:
                                    command2 = self.final_executable_commands[index]
                                    command2_split = command2.split()
                                    if command2_split[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                        times_to_move2 = command2_split[1]
                                        check_times_to_move2 = None

                                        try:
                                            check_times_to_move2 = int(times_to_move2)

                                        except ValueError:
                                            check_times_to_move2 = (
                                                self.variables.get(times_to_move2))

                                            if check_times_to_move2 is None:
                                                raise errors.NotDeclaredVariableError(
                                                    f"No such variable: {times_to_move2}"
                                                )

                                        finally:
                                            if check_times_to_move2 is None:
                                                raise errors.SomethingWentWrongError(
                                                    "Something went wrong"
                                                )

                                            times_to_move2 = check_times_to_move2

                                            if times_to_move2 <= 0:
                                                raise errors.WrongSyntaxCommandError(
                                                    f"You can't move {command2_split[0]} "
                                                    f"{times_to_move2} "
                                                    f"times"
                                                )

                                            self.grid.move(command2_split[0], times_to_move2)
                                            self.coordinates.append(self.grid.get_coords())
                                            index += 1
                                            continue

                                    # first ifblock left -> second ifblock up ->
                                    # third ifblock
                                    # ###########################################################3
                                    elif command2_split[0] == "IFBLOCK":
                                        block_direction2 = command2_split[2]
                                        if block_direction2 is None:
                                            raise errors.WrongSyntaxCommandError(
                                                "You can't check ifblock without provided "
                                                "direction"
                                            )

                                        index += 1
                                        # first ifblock left -> second ifblock up ->
                                        # third ifblock up
                                        if block_direction2 == "UP":
                                            if self.grid.y < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock left -> second ifblock up ->
                                        # third ifblock down
                                        if block_direction2 == "DOWN":
                                            if self.grid.y > 0:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: "
                                                                f"{times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0],
                                                                       times_to_move3)
                                                        self.coordinates.append(
                                                            self.grid.get_coords()
                                                        )
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock left -> second ifblock up ->
                                        # third ifblock right
                                        if block_direction2 == "RIGHT":
                                            if self.grid.x < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock left -> second ifblock up ->
                                        # third ifblock left
                                        if block_direction2 == "LEFT":
                                            if self.grid.x > 0:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                            # first ifblock left -> second ifblock ->
                            # second ifblock down
                            if not block_direction1 == "DOWN":
                                if self.grid.y > 0:
                                    while self.final_executable_commands[index] != "ENDIF":
                                        index += 1
                                    index += 1
                                    continue

                                else:
                                    command2 = self.final_executable_commands[index]
                                    command2_split = command2.split()
                                    if command2_split[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                        times_to_move2 = command2_split[1]
                                        check_times_to_move2 = None

                                        try:
                                            check_times_to_move2 = int(times_to_move2)

                                        except ValueError:
                                            check_times_to_move2 = (
                                                self.variables.get(times_to_move2))

                                            if check_times_to_move2 is None:
                                                raise errors.NotDeclaredVariableError(
                                                    f"No such variable: {times_to_move2}"
                                                )

                                        finally:
                                            if check_times_to_move2 is None:
                                                raise errors.SomethingWentWrongError(
                                                    "Something went wrong"
                                                )

                                            times_to_move2 = check_times_to_move2

                                            if times_to_move2 <= 0:
                                                raise errors.WrongSyntaxCommandError(
                                                    f"You can't move {command2_split[0]} "
                                                    f"{times_to_move2} "
                                                    f"times"
                                                )

                                            self.grid.move(command2_split[0], times_to_move2)
                                            self.coordinates.append(self.grid.get_coords())
                                            index += 1
                                            continue

                                    # first ifblock left -> second ifblock down ->
                                    # third ifblock
                                    # ###########################################################3
                                    elif command2_split[0] == "IFBLOCK":
                                        block_direction2 = command2_split[2]
                                        if block_direction2 is None:
                                            raise errors.WrongSyntaxCommandError(
                                                "You can't check ifblock without provided "
                                                "direction"
                                            )

                                        index += 1
                                        # first ifblock left -> second ifblock down ->
                                        # third ifblock up
                                        if block_direction2 == "UP":
                                            if self.grid.y < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock left -> second ifblock down ->
                                        # third ifblock down
                                        if block_direction2 == "DOWN":
                                            if self.grid.y > 0:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: "
                                                                f"{times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0],
                                                                       times_to_move3)
                                                        self.coordinates.append(
                                                            self.grid.get_coords()
                                                        )
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock left -> second ifblock down ->
                                        # third ifblock right
                                        if block_direction2 == "RIGHT":
                                            if self.grid.x < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: "
                                                                f"{times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0],
                                                                       times_to_move3)
                                                        self.coordinates.append(
                                                            self.grid.get_coords()
                                                        )
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock left -> second ifblock down ->
                                        # third ifblock left
                                        if block_direction2 == "LEFT":
                                            if self.grid.x > 0:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                            # first ifblock left -> second ifblock ->
                            # second ifblock right
                            if not block_direction1 == "RIGHT":
                                if self.grid.x < 20:
                                    while self.final_executable_commands[index] != "ENDIF":
                                        index += 1
                                    index += 1
                                    continue

                                else:
                                    command2 = self.final_executable_commands[index]
                                    command2_split = command2.split()
                                    if command2_split[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                        times_to_move2 = command2_split[1]
                                        check_times_to_move2 = None

                                        try:
                                            check_times_to_move2 = int(times_to_move2)

                                        except ValueError:
                                            check_times_to_move2 = (
                                                self.variables.get(times_to_move2))

                                            if check_times_to_move2 is None:
                                                raise errors.NotDeclaredVariableError(
                                                    f"No such variable: {times_to_move2}"
                                                )

                                        finally:
                                            if check_times_to_move2 is None:
                                                raise errors.SomethingWentWrongError(
                                                    "Something went wrong"
                                                )

                                            times_to_move2 = check_times_to_move2

                                            if times_to_move2 <= 0:
                                                raise errors.WrongSyntaxCommandError(
                                                    f"You can't move {command2_split[0]} "
                                                    f"{times_to_move2} "
                                                    f"times"
                                                )

                                            self.grid.move(command2_split[0], times_to_move2)
                                            self.coordinates.append(self.grid.get_coords())
                                            index += 1
                                            continue

                                    # first ifblock left -> second ifblock right ->
                                    # third ifblock
                                    # ###########################################################3
                                    elif command2_split[0] == "IFBLOCK":
                                        block_direction2 = command2_split[2]
                                        if block_direction2 is None:
                                            raise errors.WrongSyntaxCommandError(
                                                "You can't check ifblock without provided "
                                                "direction"
                                            )

                                        index += 1
                                        # first ifblock left -> second ifblock right ->
                                        # third ifblock up
                                        if block_direction2 == "UP":
                                            if self.grid.y < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock left -> second ifblock right ->
                                        # third ifblock down
                                        if block_direction2 == "DOWN":
                                            if self.grid.y > 0:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: "
                                                                f"{times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0],
                                                                       times_to_move3)
                                                        self.coordinates.append(
                                                            self.grid.get_coords()
                                                        )
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock left -> second ifblock right ->
                                        # third ifblock right
                                        if block_direction2 == "RIGHT":
                                            if self.grid.x < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock left -> second ifblock right ->
                                        # third ifblock left
                                        if block_direction2 == "LEFT":
                                            if self.grid.x > 0:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: "
                                                                f"{times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                            # first ifblock left -> second ifblock ->
                            # second ifblock left
                            if not block_direction1 == "LEFT":
                                if self.grid.x > 0:
                                    while self.final_executable_commands[index] != "ENDIF":
                                        index += 1
                                    index += 1
                                    continue

                                else:
                                    command2 = self.final_executable_commands[index]
                                    command2_split = command2.split()
                                    if command2_split[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                        times_to_move2 = command2_split[1]
                                        check_times_to_move2 = None

                                        try:
                                            check_times_to_move2 = int(times_to_move2)

                                        except ValueError:
                                            check_times_to_move2 = (
                                                self.variables.get(times_to_move2))

                                            if check_times_to_move2 is None:
                                                raise errors.NotDeclaredVariableError(
                                                    f"No such variable: {times_to_move2}"
                                                )

                                        finally:
                                            if check_times_to_move2 is None:
                                                raise errors.SomethingWentWrongError(
                                                    "Something went wrong"
                                                )

                                            times_to_move2 = check_times_to_move2

                                            if times_to_move2 <= 0:
                                                raise errors.WrongSyntaxCommandError(
                                                    f"You can't move {command2_split[0]} "
                                                    f"{times_to_move2} "
                                                    f"times"
                                                )

                                            self.grid.move(command2_split[0], times_to_move2)
                                            self.coordinates.append(self.grid.get_coords())
                                            index += 1
                                            continue

                                    # first ifblock left -> second ifblock left ->
                                    # third ifblock
                                    # ###########################################################3
                                    elif command2_split[0] == "IFBLOCK":
                                        block_direction2 = command2_split[2]
                                        if block_direction2 is None:
                                            raise errors.WrongSyntaxCommandError(
                                                "You can't check ifblock without provided "
                                                "direction"
                                            )

                                        index += 1
                                        # first ifblock left -> second ifblock left ->
                                        # third ifblock up
                                        if block_direction2 == "UP":
                                            if self.grid.y < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0],
                                                                       times_to_move3)
                                                        self.coordinates.append(
                                                            self.grid.get_coords()
                                                        )
                                                        index += 1
                                                        continue

                                                elif (command3_split[0] in
                                                      ["REPEAT", "CALL", "IFBLOCK"]):
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock left -> second ifblock left ->
                                        # third ifblock down
                                        if block_direction2 == "DOWN":
                                            if self.grid.y > 0:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: "
                                                                f"{times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0],
                                                                       times_to_move3)
                                                        self.coordinates.append(
                                                            self.grid.get_coords()
                                                        )
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock left -> second ifblock left ->
                                        # third ifblock right
                                        if block_direction2 == "RIGHT":
                                            if self.grid.x < 20:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

                                        # first ifblock left -> second ifblock left ->
                                        # third ifblock left
                                        if block_direction2 == "LEFT":
                                            if self.grid.x > 0:
                                                while self.final_executable_commands[index] != "ENDIF":
                                                    index += 1
                                                index += 1
                                                continue

                                            else:
                                                command3 = self.final_executable_commands[index]
                                                command3_split = command3.split()

                                                if command3_split[0] in ["UP", "DOWN",
                                                                         "LEFT", "RIGHT"]:
                                                    times_to_move3 = command3_split[1]
                                                    check_times_to_move3 = None

                                                    try:
                                                        check_times_to_move3 = int(times_to_move3)

                                                    except ValueError:
                                                        check_times_to_move3 = self.variables.get(
                                                            times_to_move3
                                                        )

                                                        if check_times_to_move3 is None:
                                                            raise errors.NotDeclaredVariableError(
                                                                f"No such variable: {times_to_move3}"
                                                            )

                                                    finally:
                                                        if check_times_to_move3 is None:
                                                            raise errors.SomethingWentWrongError(
                                                                "Something went wrong"
                                                            )

                                                        times_to_move3 = check_times_to_move3
                                                        if times_to_move3 <= 0:
                                                            raise errors.WrongSyntaxCommandError(
                                                                f"You can't move "
                                                                f"{command3_split[0]} "
                                                                f"{times_to_move3} "
                                                                f"times"
                                                            )

                                                        self.grid.move(command3_split[0], times_to_move3)
                                                        self.coordinates.append(self.grid.get_coords())
                                                        index += 1
                                                        continue

                                                elif command3_split[0] in ["REPEAT", "CALL",
                                                                           "IFBLOCK"]:
                                                    raise errors.Increasing3NestedCallsError(
                                                        "You've increased 3 nested "
                                                        "calls rule"
                                                    )

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
        self.check_commands()
        if not self.force_stop:
            self.get_variables()
        if not self.force_stop:
            self.get_procedures()
        if not self.force_stop:
            self.first_parse(self.commands)
        if not self.force_stop:
            self.second_parse()
        if not self.force_stop:
            self.run_commands()
        return self.coordinates

    def load_file(self, program_file: str) -> None:

        suffix = program_file.split(".")[-1]
        if suffix != "txt":
            raise errors.FileReadingError(
                f"You can't open .{suffix} file. The only acceptable format is .txt"
            )

        try:
            with open(program_file, "r") as check_file:
                lines = check_file.read()
                if not lines[-1].endswith("\n"):
                    with open(program_file, "a") as file:
                        file.write("\n")

            with open(program_file, "r") as file:
                for line in file:
                    if len(line) > 2:
                        self.commands.append(line[:-1].strip())

        except Exception:
            raise errors.FileReadingError("Error during reading your file")

    def interpreter_get_coords(self):
        if self.grid:
            return self.grid.get_coords()
        raise errors.ExecuteAtLeastOnce("You have to execute your program at least once")

    def __str__(self):
        return f"{self.coordinates}"


if __name__ == "__main__":
    program = Interpreter()
    res = program.execute("../test_programs/program2.txt")
    print(res)
