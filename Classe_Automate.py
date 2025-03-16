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

        # Function to safely sort mixed types (str and int)
        def safe_sort(items):
            # Convert all items to strings for consistent sorting
            return sorted(items, key=str)

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

                # Use safe_sort to handle mixed types
                row.append(",".join(map(str, safe_sort(destinations))) if destinations else "-")

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

        # Function to safely sort mixed types (str and int)
        def safe_sort(items):
            # Convert all items to strings for consistent sorting
            return sorted(items, key=str)

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
        initial_macrostate_tuple = tuple(safe_sort(initial_macrostate))  # Use safe_sort here

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
                    epsilon_closure_next_tuple = tuple(safe_sort(epsilon_closure_next))  # Use safe_sort here

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
                    epsilon_closure_next_tuple = tuple(safe_sort(epsilon_closure_next))  # Use safe_sort here
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
        return Automate(
            num_automate=self.num_automate,
            alphabet=self.alphabet,
            states=new_states,
            initial_states=new_initial_states,
            final_states=new_final_states,
            transitions=new_transitions
        )

    def is_complete(self):
        """
        Checks if the automaton is complete.
        An automaton is complete if for each state and each symbol in the alphabet,
        there exists at least one outgoing transition.

        :return: bool - True if the automaton is complete, False otherwise
        """
        # For each state, check if there's a transition for each symbol in the alphabet
        for state in self.states:
            for symbol in self.alphabet:
                # If the state has no transitions or no transition for this symbol
                if state not in self.transitions or symbol not in self.transitions[state]:
                    return False
                # Or if the destination list for this symbol is empty
                if not self.transitions[state][symbol]:
                    return False

        return True

    # Fix for the complete() method in Classe_Automate.py

    def complete(self):
        """
        Completes the automaton by adding a sink state and missing transitions.
        Unlike the determinize() method, this does not determinize the automaton first.

        :return: A new complete automaton
        """
        # Create a copy of the automaton
        automate = Automate(
            num_automate=self.num_automate,
            alphabet=self.alphabet,
            states=self.states.copy(),
            initial_states=self.initial_states.copy(),
            final_states=self.final_states.copy(),
            transitions=[(s, sym, d) for s in self.transitions for sym in self.transitions[s] for d in
                         self.transitions[s][sym]]
        )

        # Check if the automaton is already complete
        if automate.is_complete():
            return automate

        # Create a sink state "P"
        # Find a unique name for the sink state that is not already used
        sink_state = "P"
        while sink_state in automate.states:
            sink_state = sink_state + "P"

        # Add the sink state to the automaton states
        automate.states.append(sink_state)

        # IMPORTANT FIX: Check for and track added transitions to avoid duplicates
        added_transitions = set()  # Track transitions we've already added

        # Add missing transitions to the sink state
        for state in automate.states:
            for symbol in automate.alphabet:
                # Check if the transition already exists
                has_transition = (state in automate.transitions and
                                  symbol in automate.transitions[state] and
                                  automate.transitions[state][symbol])

                if not has_transition:
                    # Only add if not already added
                    transition_key = (state, symbol, sink_state)
                    if transition_key not in added_transitions:
                        automate.add_transition(state, symbol, sink_state)
                        added_transitions.add(transition_key)

        # Add transitions from the sink state to itself for all symbols
        for symbol in automate.alphabet:
            transition_key = (sink_state, symbol, sink_state)
            if transition_key not in added_transitions:
                automate.add_transition(sink_state, symbol, sink_state)
                added_transitions.add(transition_key)

        return automate

    def minimize(self):
        """
        Minimizes the automaton using Moore's algorithm.
        The automaton must be deterministic and complete.

        Returns:
        - A new minimized automaton
        """
        # Test if the automaton is deterministic and complete
        if not self.is_determinist():
            print("⚠ The automaton must be deterministic")
            print("⚠ Applying determinization...")
            automaton = self.determinize()
        else:
            automaton = self

        if not automaton.is_complete():
            print("⚠ The automaton must be complete")
            print("⚠ Applying completion...")
            automaton = automaton.complete()

        print("Starting minimization process...")

        # First partition: final states and non-final states
        current_teta = {}
        for state in automaton.states:
            if state in automaton.final_states:
                current_teta[state] = 1  # Final states
            else:
                current_teta[state] = 0  # Non-final states

        # Store the history of partitions to detect cycles
        partition_history = []

        # Start the refinement process
        itr = 1
        stable = False

        while not stable:
            print(f"Iteration {itr} - Partitions: {current_teta}")

            # Add current partition to history to detect cycles
            # Convert all keys to strings before sorting to avoid type comparison issues
            partition_str = str(sorted([(str(k), v) for k, v in current_teta.items()]))
            if partition_str in partition_history:
                print("⚠ Cycle detected in partitions. Stopping.")
                break
            partition_history.append(partition_str)

            # Create new partition based on current partition
            new_teta = {}

            # For each state, create a signature based on its current class and transition targets
            keys = {}
            for state in automaton.states:
                # Start with the current class
                key = [current_teta[state]]

                # For each symbol, add the class of the target state
                for letter in automaton.alphabet:
                    if state in automaton.transitions and letter in automaton.transitions[state]:
                        target_states = automaton.transitions[state][letter]
                        if target_states:
                            target_state = target_states[0]  # Since it's deterministic
                            key.append((letter, current_teta[target_state]))
                        else:
                            key.append((letter, -1))  # No transition
                    else:
                        key.append((letter, -1))  # No transition

                # Store the signature as a tuple (hashable)
                key_tuple = tuple(key)
                keys[state] = key_tuple

            # Group states by signature
            key_groups = {}
            for state, sig in keys.items():
                if sig not in key_groups:
                    key_groups[sig] = []
                key_groups[sig].append(state)

            # Assign new partition classes
            new_class = 0
            for sig, states in key_groups.items():
                for state in states:
                    new_teta[state] = new_class
                new_class += 1

            # Check if the partition is stable
            if new_teta == current_teta:
                stable = True
            else:
                current_teta = new_teta

            itr += 1


        print(f"Minimization completed in {itr - 1} iterations.")

        # Build the minimized automaton
        # Group states by their equivalence class
        equivalence_classes = {}
        for state, class_id in current_teta.items():
            if class_id not in equivalence_classes:
                equivalence_classes[class_id] = []
            equivalence_classes[class_id].append(state)

        print("Final equivalence classes:")
        for class_id, states in equivalence_classes.items():
            print(f"Class {class_id}: {states}")

        # Create new states for each equivalence class
        new_states = []
        class_to_state = {}
        for class_id in equivalence_classes:
            state_name = f"q{class_id}"
            new_states.append(state_name)
            class_to_state[class_id] = state_name

        # Determine initial and final states
        new_initial_states = []
        new_final_states = []

        for class_id, states in equivalence_classes.items():
            state_name = class_to_state[class_id]

            # If any state in the class is initial, the class is initial
            if any(state in automaton.initial_states for state in states):
                new_initial_states.append(state_name)

            # If any state in the class is final, the class is final
            if any(state in automaton.final_states for state in states):
                new_final_states.append(state_name)

        # Create transitions for the new automaton
        new_transitions = []
        for class_id, states in equivalence_classes.items():
            source_state = class_to_state[class_id]

            # Take any state from the class (they're equivalent)
            representative = states[0]

            # For each symbol, determine the target class
            for symbol in automaton.alphabet:
                if representative in automaton.transitions and symbol in automaton.transitions[representative]:
                    target_states = automaton.transitions[representative][symbol]
                    if target_states:
                        target_state = target_states[0]
                        target_class = current_teta[target_state]
                        target_state_name = class_to_state[target_class]
                        new_transitions.append((source_state, symbol, target_state_name))

        # Create the new minimized automaton
        minimized_automaton = Automate(
            num_automate=automaton.num_automate,
            alphabet=automaton.alphabet,
            states=new_states,
            initial_states=new_initial_states,
            final_states=new_final_states,
            transitions=new_transitions
        )

        return minimized_automaton

    def recognize_word(self, word):
        """
        Tests if a word is accepted by the automaton.
        This implementation works for both deterministic and non-deterministic automata.

        Args:
            word (str): The word to test

        Returns:
            bool: True if the word is accepted, False otherwise
        """
        # For non-deterministic automata, we need to track all possible current states
        current_states = set(self.initial_states)

        for letter in word:
            if letter not in self.alphabet:
                print(f"Error: Symbol '{letter}' is not in the alphabet!")
                return False

            # Compute next possible states
            next_states = set()
            for state in current_states:
                if state in self.transitions and letter in self.transitions[state]:
                    next_states.update(self.transitions[state][letter])

            # If no valid transitions, the word is rejected
            if not next_states:
                return False

            current_states = next_states

        # Check if any current state is final
        return any(state in self.final_states for state in current_states)

    def complement(self):
        """
        Creates the complement of the automaton.
        The complement automaton accepts all words that are not accepted by the original automaton.

        Returns:
            Automate: The complement automaton
        """

        if not self.is_determinist():
            print("⚠ Warning: The automaton should be deterministic for complement to work correctly.")
            print("⚠ Determinizing the automaton...")
            automaton = self.determinize()
        else:
            automaton = self

        if not automaton.is_complete():
            print("⚠ Warning: The automaton should be complete for complement to work correctly.")
            print("⚠ Completing the automaton...")
            automaton = automaton.complete()


        new_final_states = [state for state in self.states if state not in self.final_states]

        # Extraire les transitions au format attendu par l'initialisation
        transitions_list = []
        for source in automaton.transitions:
            for symbol in automaton.transitions[source]:
                for destination in automaton.transitions[source][symbol]:
                    transitions_list.append((source, symbol, destination))

        # Créer l'automate complémentaire
        complement_automaton = Automate(
            num_automate=automaton.num_automate,
            alphabet=automaton.alphabet,
            states=automaton.states.copy(),
            initial_states=automaton.initial_states.copy(),
            final_states=new_final_states,
            transitions=transitions_list
        )

        return complement_automaton
