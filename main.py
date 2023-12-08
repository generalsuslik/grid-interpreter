from collections import defaultdict

from grid import Grid


class Interpreter:
    """
    Class represents simple interpreter. First, u have to declare all procedures with get_procedures method
    then u have to run parse method, to remove all loops and procedures calls. After that, you'll have an
    array of all static stuff and if-blocks.

    TODO: loops in procedures
    TODO: variables declaration(for example: SET X 12)
    """
    def __init__(self, program_file):
        self.grid = Grid()
        self.commands = [i[:-1].strip() for i in open(program_file).readlines() if len(i) > 2]
        self.executable_commands = []
        self.final_executable_commands = []
        self.functions = defaultdict(list)
        self.variables = {}

    def get_procedures(self):
        index = 0
        while index < len(self.commands):
            command_split = self.commands[index].split()
            if command_split[0] == "PROCEDURE":
                procedure_name = command_split[1]
                procedure_body = []
                index += 1
                while self.commands[index] != "ENDPROCEDURE":
                    procedure_body.append(self.commands[index])
                    index += 1

                self.functions[procedure_name] = procedure_body
                index += 1
                continue

            index += 1

    def first_parse(self, commands_array):
        index = 0
        while index < len(commands_array):
            command = commands_array[index]
            split_command = command.split()
            # ########################LOOPS##############################
            # 1st loop
            if split_command[0] == "REPEAT":
                n1 = split_command[1]
                if n1 in self.variables.keys():
                    n1 = self.variables[n1]

                else:
                    n1 = int(n1)
                cycle_body1 = []
                index += 1
                while commands_array[index] != "ENDREPEAT":
                    command1 = commands_array[index]
                    split_command1 = command1.split()
                    ####################################################################
                    # 2 nest loop
                    if split_command1[0] == "REPEAT":
                        n2 = split_command1[1]
                        if n2 in self.variables.keys():
                            n2 = self.variables[n2]

                        else:
                            n2 = int(n2)
                        cycle_body2 = []
                        index += 1
                        while commands_array[index] != "ENDREPEAT":  # while we haven't quited 2 loop
                            command2 = commands_array[index]
                            split_command2 = command2.split()
                            # -----------------------------------------------------------------------#
                            # last 3rd nested loop
                            if split_command2[0] == "REPEAT":  # we've found 3rd (last) loop
                                n3 = int(split_command2[1])
                                cycle_body3 = []
                                index += 1
                                while commands_array[index] != "ENDREPEAT":
                                    cycle_body3.append(commands_array[index])
                                    index += 1

                                index += 1  # escaping from "ENDREPEAT" in 3rd loop

                                for _ in range(n3):  # Adding elements from 3rd loop n3 times to 2nd loop's body
                                    for elem in cycle_body3:
                                        cycle_body2.append(elem)
                                # 3 nest done
                            # -----------------------------------------------------------------------#
                            # continuing 2 nest
                            ##########################################################################
                            else:  # We quited 3rd loop, and now we're able to continue working with 2nd loop
                                cycle_body2.append(commands_array[index])
                                index += 1

                        index += 1  # escaping from "ENDREPEAT" in 2nd loop
                        # Our 2nd loop has ended. Now we have to add elements from cycle2 n2 times to cycle1
                        for _ in range(n2):
                            for elem in cycle_body2:
                                cycle_body1.append(elem)

                    #####################################################
                    # continuing 1st nest
                    else:  # We quited 2nd loop, and now we're able to continue working with 1st loop
                        cycle_body1.append(commands_array[index])
                        index += 1

                index += 1  # escaping from "ENDREPEAT" in 1st loop
                for _ in range(n1):
                    for elem in cycle_body1:
                        self.executable_commands.append(elem)

                continue

            # ########################LOOPS##############################

            # Variables declaration
            if split_command[0] == "SET":
                variable_name = split_command[1]
                variable_value = int(command.split("=")[-1])
                self.variables[variable_name] = variable_value

            # Skip PROCEDURES declaration
            elif split_command[0] == "PROCEDURE":
                index += 1
                while commands_array[index] != "ENDPROCEDURE":
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
        while index < len(self.executable_commands):
            command = self.executable_commands[index]
            split_command = command.split()
            # ########################LOOPS##############################
            # 1st loop
            if split_command[0] == "REPEAT":
                n1 = split_command[1]
                if n1 in self.variables.keys():
                    n1 = self.variables[n1]

                else:
                    n1 = int(n1)

                cycle_body1 = []
                index += 1
                while self.executable_commands[index] != "ENDREPEAT":
                    command1 = self.executable_commands[index]
                    split_command1 = command1.split()
                    ####################################################################
                    # 2 nest loop
                    if split_command1[0] == "REPEAT":
                        n2 = split_command1[1]
                        if n2 in self.variables.keys():
                            n2 = self.variables[n2]

                        else:
                            n2 = int(n2)

                        cycle_body2 = []
                        index += 1
                        while self.executable_commands[index] != "ENDREPEAT":  # while we haven't quited 2 loop
                            command2 = self.executable_commands[index]
                            split_command2 = command2.split()
                            # -----------------------------------------------------------------------#
                            # last 3rd nested loop
                            if split_command2[0] == "REPEAT":  # we've found 3rd (last) loop
                                n3 = split_command2[1]
                                if n3 in self.variables.keys():
                                    n3 = self.variables[n3]

                                else:
                                    n3 = int(n3)
                                cycle_body3 = []
                                index += 1
                                while self.executable_commands[index] != "ENDREPEAT":
                                    cycle_body3.append(self.executable_commands[index])
                                    index += 1

                                index += 1  # escaping from "ENDREPEAT" in 3rd loop

                                for _ in range(n3):  # Adding elements from 3rd loop n3 times to 2nd loop's body
                                    for elem in cycle_body3:
                                        cycle_body2.append(elem)
                                # 3 nest done
                            # -----------------------------------------------------------------------#
                            # continuing 2 nest
                            ##########################################################################
                            else:  # We quited 3rd loop, and now we're able to continue working with 2nd loop
                                cycle_body2.append(self.executable_commands[index])
                                index += 1

                        index += 1  # escaping from "ENDREPEAT" in 2nd loop
                        # Our 2nd loop has ended. Now we have to add elements from cycle2 n2 times to cycle1
                        for _ in range(n2):
                            for elem in cycle_body2:
                                cycle_body1.append(elem)

                    #####################################################
                    # continuing 1st nest
                    else:  # We quited 2nd loop, and now we're able to continue working with 1st loop
                        cycle_body1.append(self.executable_commands[index])
                        index += 1

                index += 1  # escaping from "ENDREPEAT" in 1st loop
                for _ in range(n1):
                    for elem in cycle_body1:
                        self.final_executable_commands.append(elem)

                continue

            # ########################LOOPS#############################
            else:
                self.final_executable_commands.append(command)

            index += 1

    def __str__(self):
        return f"{self.final_executable_commands}"


program = Interpreter("program.txt")
program.get_procedures()
program.first_parse(program.commands)
program.second_parse()
print(program)

