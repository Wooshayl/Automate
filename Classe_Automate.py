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

        self.is_standard = False
        self.is_deterministic = False
        self.is_complete = False
        self.is_minimized = False

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
        """Displays the automaton as a formatted transition table without using tabulate."""

        # Column headers
        headers = ["", "State"] + self.alphabet

        # Calculate column widths for proper alignment
        col_widths = [max(len(header), 2) for header in headers]  # Start with header lengths

        # Prepare row data
        table_rows = []
        for state in self.states:
            # Determine E, S, or ES
            markers = []
            if state in self.initial_states:
                markers.append("E")
            if state in self.final_states:
                markers.append("S")
            state_label = "".join(markers) or " "  # Ensure non-empty space

            # Fill transitions
            row = [state_label, str(state)]  # First two columns
            for symbol in self.alphabet:
                destinations = self.transitions.get(state, {}).get(symbol, ["-"])
                destination_str = ",".join(map(str, destinations))
                row.append(destination_str)

            # Update column widths dynamically
            for i, value in enumerate(row):
                col_widths[i] = max(col_widths[i], len(value))

            table_rows.append(row)

        # Print header
        header_row = " | ".join(header.ljust(col_widths[i]) for i, header in enumerate(headers))
        print(header_row)
        print("-" * len(header_row))  # Separator line

        # Print table rows
        for row in table_rows:
            print(" | ".join(row[i].ljust(col_widths[i]) for i in range(len(row))))



