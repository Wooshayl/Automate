import os

class FileParser:
    """Class responsible for reading and extracting data from a properly formatted file for automaton creation."""

    @staticmethod
    def convert_positive_integer(line_content, line_number, allow_zero=True):
        """Parses a positive integer from a line, raising ValueError on failure.
        :param line_content: (str) The information we want to parse
        :param line_number: (int) The line number for error reporting.
        :param allow_zero: (bool) Whether zero is allowed.
        :return: The parsed positive integer."""
        try:
            value = int(line_content)
            if value < 0:
                raise ValueError(f"Line {line_number}: Value must be non-negative, got {value}")
            if value == 0 and not allow_zero:
                raise ValueError(f"Line {line_number}: Value must be positive, got 0")
            return value
        except ValueError as e:
            raise ValueError(f"Line {line_number}: Cannot parse integer: '{line_content}'") from e

    @staticmethod
    def parse_states(line_content, line_number, num_states):
        """Takes in a line (a string) and returns a list of states.
        :param line_content: (str) The information we want to parse
        :param line_number : (int) The line number for error reporting.
        :param num_states : (int) The total number of states in the automaton.
        :return: list[int] A list of parsed state numbers."""
        parts = line_content.split()
        if not parts:
            raise ValueError(f"Line {line_number}: State line is empty")

        expected_number = FileParser.convert_positive_integer(parts[0], line_number)
        if len(parts) != expected_number + 1:
            raise ValueError(f"Line {line_number}: Expected {expected_number} states, found {len(parts) - 1}")

        states = []
        for i in range(1, expected_number + 1):
            state = FileParser.convert_positive_integer(parts[i], line_number)
            if state < 0 or state >= num_states:
                raise ValueError(f"Line {line_number}: State {state} out of range [0, {num_states - 1}]")
            states.append(state)
        return states

    @staticmethod
    def parse_transitions(lines, start_line, num_transitions, num_states):
        """Parses and validates transitions from a list of lines.
        :param list_transitions : (list[str]) The list of lines containing transition information.
        :param start_line : (int) The starting line number for transitions.
        :param num_transitions : (int) The number of transitions to parse.
        :param num_states : (int) The total number of states in the automaton.
        :return: list[tuple[int, str, int]]: A list of parsed transitions (source, symbol, destination)."""
        transitions = []
        epsilon_transitions = []

        for i in range(num_transitions):
            line_num = start_line + i
            if line_num >= len(lines):
                raise ValueError(f"Line {line_num + 1}: Missing transition")

            line = lines[line_num].strip()
            if len(line) < 3:
                raise ValueError(f"Line {line_num + 1}: Invalid transition format '{line}'")

            try:
                source = int(line[0])
                symbol = line[1:-1]
                destination = int(line[-1])

                if source < 0 or source >= num_states:
                    raise ValueError(f"Line {line_num + 1}: Source state {source} out of range")
                if destination < 0 or destination >= num_states:
                    raise ValueError(f"Line {line_num + 1}: Destination state {destination} out of range")

                if symbol in {"ε", "epsilon", "eps"}:
                    epsilon_transitions.append((source, destination))
                    transitions.append((source, None, destination))
                else:
                    transitions.append((source, symbol, destination))
            except ValueError:
                raise ValueError(f"Line {line_num + 1}: Invalid transition format '{line}'")

        return transitions, epsilon_transitions

    @staticmethod
    def compute_epsilon_closure(states, epsilon_transitions):
        """Computes the epsilon closure for a set of states.
        :param states: (set[int]) The set of states to compute closure for
        :param epsilon_transitions: (list[tuple[int, int]]) List of epsilon transitions (src, dest)
        :return closure: set[int] The epsilon closure"""

        closure = set(states)
        while True:
            new_states_found = False
            for source, destination in epsilon_transitions:
                if source in closure and destination not in closure:
                    closure.add(destination)
                    new_states_found = True
            if not new_states_found:
                break
        return closure

    @staticmethod
    def read_automaton_file(file_number):
        """Reads and parses an automaton from a file, performing validation.
    Supports epsilon transitions (represented by "", "ε", "epsilon", or "eps").
    :param filename : (str) The path to the automaton file.
    :return : (dict) A dictionary containing the parsed automaton information."""
        file_path = f"automates/automaton{file_number}.txt"  # Dynamically create the file path

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                lines = [line.strip() for line in file.readlines()]

            if len(lines) < 5:
                raise ValueError(f"File {file_number} has insufficient lines (min 5 required).")

            num_symbols = FileParser.convert_positive_integer(lines[0], 1)
            num_states = FileParser.convert_positive_integer(lines[1], 2)
            initial_states = FileParser.parse_states(lines[2], 3, num_states)
            terminal_states = FileParser.parse_states(lines[3], 4, num_states)
            num_transitions = FileParser.convert_positive_integer(lines[4], 5)

            if len(lines) < 5 + num_transitions:
                raise ValueError(f"File {file_number} is missing transition lines.")
            if len(lines) > 5 + num_transitions:
                raise ValueError(f"File {file_number} has too many lines.")

            transitions, epsilon_transitions = FileParser.parse_transitions(lines, 5, num_transitions, num_states)

            if epsilon_transitions:
                epsilon_closure = FileParser.compute_epsilon_closure(set(initial_states), epsilon_transitions)
                initial_states = list(epsilon_closure)

            return {
                "num_automate": file_number,  # Store file number for reference
                "alphabet": [chr(97 + i) for i in range(num_symbols)],
                "states": list(range(num_states)),
                "initial_states": initial_states,
                "terminal_states": terminal_states,
                "transitions": transitions,
                "epsilon_transitions": epsilon_transitions,
                "has_epsilon_transitions": len(epsilon_transitions) > 0,
            }

        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: '{file_path}'")
        except Exception as e:
            raise ValueError(f"Error reading file {file_number}: {e}")
    @staticmethod
    def print_automaton_info(automaton):
        """Prints a readable summary of the automaton's properties.
        :param automaton: (dict) A dictionary containing the automaton information."""
        print("\nAutomaton Information:")
        print(f"Number of symbols: {automaton['num_symbols']}")
        print(f"Number of states: {automaton['num_states']}")
        print(f"Initial states: {automaton['initial_states']}")
        print(f"Terminal states: {automaton['terminal_states']}")
        print(f"Number of transitions: {len(automaton['transitions'])}")

        print("Transitions:")
        for source, symbol, destination in automaton['transitions']:
            if symbol is None:
                print(f"  {source}ε{destination} (epsilon transition)")
            else:
                print(f"  {source}{symbol}{destination} (with symbol '{symbol}')")

        if automaton["has_epsilon_transitions"]:
            print("\nThis automaton contains epsilon transitions.")
            print(f"Number of epsilon transitions: {len(automaton['epsilon_transitions'])}")

            print("\nEpsilon closures:")
            for state in range(automaton["num_states"]):
                closure = FileParser.compute_epsilon_closure({state}, automaton["epsilon_transitions"])
                if len(closure) > 1:
                    print(f"  ε-closure(q{state}) = {sorted(closure)}")
