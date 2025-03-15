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
        if symbol not in self.alphabet:
            print(f"⚠ Error: The symbol '{symbol}' is not in the alphabet!")
            return
        if source not in self.transitions:
            print(f"⚠ Error: State '{source}' does not exist!")
            return

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
                print(f"{state:<10}{symbol:<10}{destinations}")

    def display_table(self):
        """Displays the automaton as a formatted transition table, with states ordered by traversal."""

        # Step 1: Extract epsilon transitions from self.transitions
        epsilon_transitions = []
        for state in self.states:
            if state in self.transitions:
                for symbol in self.transitions[state]:
                    if symbol in {"eps", "ε", "epsilon", None}:
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
        col_widths = [max(len(header), 2) for header in headers]

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


