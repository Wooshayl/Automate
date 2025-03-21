# File that deals with the initial steps. Receive a normalised .txt and extract all information into a DICT

class FileParser:
    """Class responsible for reading and extracting data from a properly formatted file for automaton creation."""

    @staticmethod
    def convert_positive_integer(line_content, line_number, allow_zero=True):
        """Convert a string into a positive integer.

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

        parts = line_content.split()  # Convert a string into a list of strings, each element seperated by a space
        if not parts:
            raise ValueError(f"Line {line_number}: State line is empty")

        expected_number = FileParser.convert_positive_integer(parts[0], line_number)
        if len(parts) != expected_number + 1:  # The first element is meant to represent the total amount of element
            raise ValueError(f"Line {line_number}: Expected {expected_number} states, found {len(parts) - 1}")

        states = []  # Make a List of INTs thanks to the List of Strings 'parts'
        for i in range(1, expected_number + 1):
            state = FileParser.convert_positive_integer(parts[i], line_number)
            if state < 0 or state >= num_states:
                raise ValueError(f"Line {line_number}: State {state} out of range [0, {num_states - 1}]")
            states.append(state)
        return states

    @staticmethod
    def parse_transitions(list_transitions, num_transitions, num_states):
        """Parses and validates transitions from a list of lines.

        :param list_transitions : (list[str]) The list of lines containing transition information.
        :param num_transitions : (int) The number of transitions to parse.
        :param num_states : (int) The total number of states in the automaton.

        :return: list[tuple[int, str, int]]: A list of parsed transitions (source, symbol, destination)."""

        transitions = []  # Store every transition, epsilon transitions are stored as well as symbol None
        epsilon_transitions = []  # Store only the epsilon transitions

        for i in range(num_transitions):
            line_num = 5 + i
            if line_num >= len(list_transitions):
                raise ValueError(f"Line {line_num + 1}: Missing transition")

            line = list_transitions[line_num].strip()
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
        """ Computes the epsilon closure of a state, meaning : all the states that can be reached following 0 or more epsilon transitions

        :param states: (set[int]) The set of states to compute closure for
        :param epsilon_transitions: (list[tuple[int, int]]) List of epsilon transitions (src, dest)

        :return closure: set[int] The epsilon closure, in other words all the states that can be reached from the
        initial state without transitioning through letters of the alphabet"""

        closure = states    # Duplicate the set of states to compute, the automatically have themselves in the closure
                            # Use of sets instead of lists to easily avoid duplicates

        while True:
            new_states_found = False

            for source, destination in epsilon_transitions:
                if source in closure and destination not in closure:
                    closure.add(destination)  # The source state was in the closure but destination wasn't
                    # Since we're using sets we don't have to worry about duplicates anyway
                    new_states_found = True  # Meaning that we just found a new state for our closure

            if not new_states_found:  # The epsilon-closure is complete
                break

        return closure

    @staticmethod
    def read_automaton_file(file_number):
        """Reads and parses an automaton from a file, performing validation.

        :param file_number: (int) Number of the concerned file

        :return automaton: (dict) all the relevant information of our automaton"""

        file_path = f"automates/automaton{file_number}.txt"  # Dynamically create the file path

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                lines = [line.strip() for line in file.readlines()]  # Remove any existing disturbing whitespace

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

            # Parsing the transitions is more delicate than the previous steps, therefore we work on it here.
            transitions = []  # List of triples containing all the neighbouring transitions, including epsilons replaced by 'None'
            epsilon_transitions = []  # Store only the neighbouring epsilon transitions, only source and destination are stored

            for i in range(num_transitions):
                line_num = 5 + i  # Account for the initial 5 lines that aren't transitions
                line = lines[line_num].strip()  # Remove any whitespace before or after the text

                line = line.replace(" ", "")  # Account for any weird spaces in the transition lines

                source_digits = ""  # Store the source digits in a string incase it's a number over 9
                pos = 0
                while pos < len(line) and line[pos].isdigit():  # While we don't come across a symbol or exceed the line
                    source_digits += line[pos]
                    pos += 1

                if not source_digits:
                    raise ValueError(f"Line {line_num + 1}: Cannot parse source state in '{line}'")

                symbol_start = pos  # pos is incremented in the while loop so if we don't satisfy the condition :

                dest_digits = ""  # Same logic as source_digits, but we work out way backwards
                pos = len(line) - 1
                while pos >= symbol_start and line[pos].isdigit():
                    dest_digits = line[pos] + dest_digits
                    pos -= 1

                if not dest_digits:
                    raise ValueError(f"Line {line_num + 1}: Cannot parse destination state in '{line}'")

                symbol = line[symbol_start:pos + 1]  # Incase the symbol isn't just a simple letter, take an interval

                try:
                    source = int(source_digits)  # Convert the strings into INTs
                    destination = int(dest_digits)  # Convert the strings into INTs
                except ValueError:
                    raise ValueError(f"Line {line_num + 1}: Invalid state format in '{line}'")

                if source < 0 or source >= num_states:
                    raise ValueError(f"Line {line_num + 1}: Source state {source} out of range")
                if destination < 0 or destination >= num_states:
                    raise ValueError(f"Line {line_num + 1}: Destination state {destination} out of range")

                if symbol in {"ε", "eps", ""}:
                    epsilon_transitions.append((source, destination))
                    transitions.append((source, None, destination))
                else:
                    transitions.append((source, symbol, destination))

            epsilon_closures = {}  # Create a DICT to keep track of all epsilon-closures
            for state in range(num_states):  # For every state in the automaton
                epsilon_closures[state] = FileParser.compute_epsilon_closure({state}, epsilon_transitions)
                # Each state is a key, and each value is the complete set of states reachable from that state via epsilon transitions

            expanded_terminal_states = set()
            # Update the terminal states (if an epsilon closure has at least 1 terminal state then it is also terminal)
            for state in range(num_states):  # Check through every possible state
                closure = epsilon_closures[state]  # Get the epsilon closure for said state

                has_terminal_state = False  # Consider that it doesn't have a single final state in the closure
                for terminal_state in terminal_states:  # Filter through every terminal state in the automaton
                    if terminal_state in closure:  # If a single terminal state is found in our state's closure, break
                        has_terminal_state = True
                        break

                if has_terminal_state:
                    expanded_terminal_states.add(
                        state)  # Terminal state detected so add it to the set of new terminal states

            enhanced_transitions = []
            # 'Transitions' only has each direct neighbour, enhanced allows to jump past the epsilons
            for source in range(num_states):
                alphabet_symbols = [chr(97 + i) for i in range(num_symbols)]  # Obtain every letter in our alphabet

                for symbol_char in alphabet_symbols:  # For each letter in our automaton's alphabet
                    states_reachable_by_epsilon = epsilon_closures[
                        source]  # Get all states reachable from source via epsilon transitions

                    for epsilon_reachable_state in states_reachable_by_epsilon:  # For each state reachable by epsilon transitions

                        for transition_source, transition_symbol, transition_dest in transitions:  # Check all transitions in the automaton

                            # If we find a transition from an epsilon-reachable state with the current symbol
                            if transition_source == epsilon_reachable_state and transition_symbol == symbol_char:
                                # Add a new enhanced transition from our original source state
                                enhanced_transitions.append((source, symbol_char, transition_dest))

            return {
                "num_automate": file_number,
                "alphabet": [chr(97 + i) for i in range(num_symbols)],
                "states": list(range(num_states)),
                "initial_states": initial_states,
                "terminal_states": list(expanded_terminal_states),
                "transitions": enhanced_transitions + [(source, None, destination) for source, destination in epsilon_transitions],
                "epsilon_transitions": epsilon_transitions,
                "has_epsilon_transitions": len(epsilon_transitions) > 0,
                "epsilon_closures": epsilon_closures
            }

        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: '{file_path}'")
        except Exception as e:
            raise ValueError(f"Error reading file {file_number}: {e}")
