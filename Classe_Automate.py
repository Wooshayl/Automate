from Class_FileParser import FileParser  # Import the class that reads files


class Automate:
    def __init__(self, num_automate, alphabet, states, initial_states, final_states, transitions):
        self.num_automate = num_automate  # Store the file number
        self.alphabet = alphabet
        self.states = states
        self.initial_states = initial_states
        self.final_states = final_states
        self.transitions = {state: {} for state in states}

        for (source, symbol, destination) in transitions:
            self.add_transition(source, symbol, destination)

    def add_transition(self, source, symbol, destination):
        """Adds a transition to the automaton."""
        if symbol not in self.alphabet and symbol is not None:
            print(f"⚠ Error: The symbol '{symbol}' is not in the alphabet!")
            return
        if source not in self.transitions:
            self.transitions[source] = {}  # Initialize transitions for this state if needed

        if symbol in self.transitions[source]:
            self.transitions[source][symbol].append(destination)
        else:
            self.transitions[source][symbol] = [destination]

    @classmethod
    def from_file(cls, file_number):
        """Creates an Automate instance from a numbered file."""
        data = FileParser.read_automaton_file(file_number)
        if data:
            return cls(
                num_automate=data["num_automate"],
                alphabet=data["alphabet"],
                states=data["states"],
                initial_states=data["initial_states"],
                final_states=data["terminal_states"],
                transitions=data["transitions"]
            )

    def display_value(self):
        """Displays the automaton as a table."""
        print(f"\n🔹 Automaton {self.num_automate}")
        print(f"Alphabet: {self.alphabet}")
        print(f"States: {self.states}")
        print(f"Initial states: {self.initial_states}")
        print(f"Final states: {self.final_states}")
        print("\nTransitions:")

        # Create a table format
        print(f"{'State':<10}{'Symbol':<10}{'Next States'}")
        print("-" * 30)
        for state, transitions in self.transitions.items():
            for symbol, destinations in transitions.items():
                print(f"{state:<10}{symbol if symbol is not None else 'ε':<10}{destinations}")

    def display_table(self):
        """Displays the automaton as a formatted transition table, with states ordered by traversal."""

        # Step 1: Extract epsilon transitions from self.transitions
        epsilon_transitions = []
        for state in self.states:
            if state in self.transitions:
                for symbol in self.transitions[state]:
                    if symbol in {None, "eps", "ε", "epsilon"}:
                        for dest in self.transitions[state][symbol]:
                            epsilon_transitions.append((state, dest))

        # Step 2: Compute epsilon closure for each state
        epsilon_closure_map = {
            state: FileParser.compute_epsilon_closure({state}, epsilon_transitions) for state in self.states
        }

        # New: Determine state traversal order starting from initial states
        ordered_states = []
        visited = set()
        queue = list(self.initial_states)  # Start with initial states

        while queue:
            current_state = queue.pop(0)
            if current_state in visited:
                continue

            ordered_states.append(current_state)
            visited.add(current_state)

            # Add all destination states to the queue
            for symbol in self.alphabet:
                destinations = set()
                for substate in epsilon_closure_map[current_state]:
                    if substate in self.transitions and symbol in self.transitions[substate]:
                        destinations.update(self.transitions[substate][symbol])

                # Add unvisited destinations to the queue
                for dest in destinations:
                    if dest not in visited and dest not in queue:
                        queue.append(dest)

        # Add any remaining states that weren't reachable
        for state in self.states:
            if state not in visited:
                ordered_states.append(state)

        # Step 3: Prepare headers
        headers = ["", "State"] + self.alphabet
        col_widths = [max(len(str(header)), 2) for header in headers]

        # Step 4: Prepare table rows
        table_rows = []
        for state in ordered_states:  # Use the ordered states instead of self.states
            # Determine E, S, or ES
            markers = []
            if state in self.initial_states:
                markers.append("E")
            if state in self.final_states:
                markers.append("S")
            state_label = "".join(markers) or " "

            # Step 5: Fill transitions, considering epsilon closure
            row = [state_label, str(state)]  # First two columns
            for symbol in self.alphabet:
                destinations = set()

                # Explore epsilon closure and fetch reachable states
                for substate in epsilon_closure_map[state]:
                    if substate in self.transitions and symbol in self.transitions[substate]:
                        destinations.update(self.transitions[substate][symbol])

                row.append(",".join(map(str, sorted(destinations))) if destinations else "-")

            # Step 6: Adjust column width
            for i, value in enumerate(row):
                col_widths[i] = max(col_widths[i], len(value))

            table_rows.append(row)

        # Step 7: Print the formatted table
        header_row = " | ".join(header.ljust(col_widths[i]) for i, header in enumerate(headers))
        print(header_row)
        print("-" * len(header_row))  # Separator line
        for row in table_rows:
            print(" | ".join(row[i].ljust(col_widths[i]) for i in range(len(row))))

    def is_determinist(self):
        """
        Checks if the automaton is deterministic.
        An automaton is deterministic if:
        1. It has only one initial state
        2. For each state and each symbol, there is at most one transition
        3. There are no epsilon transitions

        :return: bool - True if the automaton is deterministic, False otherwise
        """
        # Check if there is more than one initial state
        if len(self.initial_states) != 1:
            return False

        # Check if there are epsilon transitions
        for state in self.states:
            if state in self.transitions:
                if None in self.transitions[state]:
                    return False  # Epsilon transition found

        # Check if for each state and each symbol, there is at most one transition
        for state in self.states:
            if state in self.transitions:
                for symbol in self.alphabet:
                    if symbol in self.transitions[state] and len(self.transitions[state][symbol]) > 1:
                        return False  # More than one transition for the same symbol

        return True

    def determinize(self):
        """
        Transforms the automaton into an equivalent deterministic automaton.
        This method builds a new automaton from the current one while preserving state names.
        Composite states like {9,19} will be named '919'.

        :return: A new deterministic automaton
        """
        if self.is_determinist():
            # If the automaton is already deterministic, return a copy
            return self

        # Handle epsilon transitions first
        # Collect all epsilon transitions
        epsilon_transitions = []
        for state in self.states:
            if state in self.transitions and None in self.transitions[state]:
                for dest in self.transitions[state][None]:
                    epsilon_transitions.append((state, dest))

        # Create a map of epsilon closures for each state
        epsilon_closures = {}
        for state in self.states:
            epsilon_closures[state] = FileParser.compute_epsilon_closure({state}, epsilon_transitions)

        # Build the new automaton
        # Initial states: set of epsilon closures of initial states
        initial_macrostate = set()
        for initial_state in self.initial_states:
            initial_macrostate.update(epsilon_closures[initial_state])
        initial_macrostate_tuple = tuple(sorted(initial_macrostate))

        # Initialize structures for the new automaton
        # We'll use tuples of states as keys and combined state names as values
        new_states_map = {}  # Maps macrostates to their combined names
        states_to_process = [initial_macrostate_tuple]
        processed_states = set()
        new_transitions = []

        # Function to generate combined state name from a set of states
        def generate_state_name(states_tuple):
            return ''.join(str(state) for state in states_tuple)

        # First pass: Generate all the new state names
        while states_to_process:
            current_macrostate = states_to_process.pop(0)
            if current_macrostate in processed_states:
                continue

            processed_states.add(current_macrostate)

            # Generate the combined state name for this macrostate
            new_state_name = generate_state_name(current_macrostate)
            new_states_map[current_macrostate] = new_state_name

            # For each symbol in the alphabet
            for symbol in self.alphabet:
                # Calculate the set of states reachable with this symbol
                next_states = set()
                for state in current_macrostate:
                    if state in self.transitions and symbol in self.transitions[state]:
                        next_states.update(self.transitions[state][symbol])

                # Apply epsilon closures to the reached states
                epsilon_closure_next = set()
                for state in next_states:
                    epsilon_closure_next.update(epsilon_closures[state])

                if epsilon_closure_next:
                    # Convert to tuple to use as a key
                    epsilon_closure_next_tuple = tuple(sorted(epsilon_closure_next))

                    # Add new state to process if not seen before
                    if epsilon_closure_next_tuple not in new_states_map and epsilon_closure_next_tuple not in states_to_process:
                        states_to_process.append(epsilon_closure_next_tuple)

        # Second pass: Create all transitions using the new state names
        for macrostate in processed_states:
            current_state_name = new_states_map[macrostate]

            # For each symbol in the alphabet
            for symbol in self.alphabet:
                # Calculate the set of states reachable with this symbol
                next_states = set()
                for state in macrostate:
                    if state in self.transitions and symbol in self.transitions[state]:
                        next_states.update(self.transitions[state][symbol])

                # Apply epsilon closures
                epsilon_closure_next = set()
                for state in next_states:
                    epsilon_closure_next.update(epsilon_closures[state])

                if epsilon_closure_next:
                    epsilon_closure_next_tuple = tuple(sorted(epsilon_closure_next))
                    next_state_name = new_states_map[epsilon_closure_next_tuple]

                    # Add the transition using state names
                    new_transitions.append((current_state_name, symbol, next_state_name))

        # Generate the list of all new states
        new_states = list(new_states_map.values())

        # Determine the initial and final states of the new automaton
        new_initial_states = [new_states_map[initial_macrostate_tuple]]

        new_final_states = []
        for macrostate, state_name in new_states_map.items():
            # A macrostate is final if at least one of its states is final
            if any(state in self.final_states for state in macrostate):
                new_final_states.append(state_name)

        # Create the new deterministic automaton with string-based state names
        from Classe_Automate import Automate  # Import here to avoid circular imports
        return Automate(
            num_automate=self.num_automate,
            alphabet=self.alphabet,
            states=new_states,
            initial_states=new_initial_states,
            final_states=new_final_states,
            transitions=new_transitions
        )
