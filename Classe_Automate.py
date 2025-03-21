from Class_FileParser import FileParser  # Import the class that reads files


class Automate:

    def __init__(self, num_automate, alphabet, states, initial_states, final_states, transitions):

        #Define most important attributes of the automata object
        self.num_automate = num_automate
        self.alphabet = alphabet
        self.states = states
        self.initial_states = initial_states
        self.final_states = final_states
        for state in states:
            self.transitions = {state: {}}  # Create a DICT and define every state as a key

        for (entry, symbol, destination) in transitions:
            self.add_transition(entry, symbol, destination)

    def add_transition(self, source, symbol, destination):
        """Adds a transition to the automaton."""

        if symbol not in self.alphabet and symbol is not None:
            raise ValueError(f" Error: The symbol '{symbol}' is not in the alphabet!")

        if source not in self.transitions:
            self.transitions[source] = {}  # We've detected a new state not in our list, so we initialise it as a key.

        if symbol in self.transitions[source]:
            self.transitions[source][symbol].append(destination)
        else:
            self.transitions[source][symbol] = [destination]

########################################################################################################################
    # The following methods were used multiple times in other methods, therefore we just put them here as a bracket
########################################################################################################################

    @classmethod
    def from_file(cls, file_number):
        """Creates an Automate instance from a numbered file.

        :param cls: Here we use cls instead of self because we are calling upon the class's constructor __init__ to make a new instance
        :param file_number: Number at the end of the file name.

        :return: Return a new instance of the class. This new instance contains all the automaton's information gathered """

        data = FileParser.read_automaton_file(file_number)
        if data:
            return cls(
                num_automate=data["num_automate"],
                alphabet=data["alphabet"],
                states=data["states"],
                initial_states=data["initial_states"],
                final_states=data["terminal_states"],
                transitions=data["transitions"])

    @staticmethod
    def function_to_sort(items):
        """ Create a new sorted list that can deal with types INT and Str.
        We used sorted since we had issues dealing with our sink state P

        :param items:
        :return:   """

        return sorted(items, key=str)

    @staticmethod
    def generate_state_name(states_tuple):
        """ ????

        :param states_tuple: Tuple(INT, INT)
        :return: """

        combined_name = ""  # Start with an empty text string
        for state in states_tuple:  # Go through each state in the tuple
            combined_name = combined_name + str(state)  # Add the item (as text) to the combined name
        return combined_name

########################################################################################################################
    # Fonctions d'affichages
########################################################################################################################

    def display_value(self):
        """Displays the automaton as a table."""

        print(f"\nAutomaton {self.num_automate}")
        print(f"Alphabet: {self.alphabet}")
        print(f"States: {self.states}")
        print(f"Initial states: {self.initial_states}")
        print(f"Final states: {self.final_states}")
        print("\nTransitions:")

        # Create a table format
        print(f"{'State':<10}{'Symbol':<10}{'Next States'}")
        print("-" * 31)
        for state, transitions in self.transitions.items():
            for symbol, destinations in transitions.items():
                print(f"{state:<10}{symbol if symbol is not None else 'ε':<10}{destinations}")

    def display_table(self):
        """Displays the automaton as a formatted transition table, with states ordered by traversal."""

    #-------------------- Step 1: Extract epsilon transitions from self.transitions --------------------#
        epsilon_transitions = []
        for state in self.states:
            if state in self.transitions:
                for symbol in self.transitions[state]:
                    if symbol in {None, "eps"}:
                        for finish_state in self.transitions[state][symbol]:
                            epsilon_transitions.append((state, finish_state))

    #### Step 2: Compute epsilon closure for each state
        list_epsilon_cloture = {}
        for state in self.states :
            list_epsilon_cloture[state] = FileParser.compute_epsilon_closure({state}, epsilon_transitions)

    #### New: Determine state traversal order starting from initial states
        table_ordered_states = []
        visited = set()
        queue = list(self.initial_states)  # Start with initial states

        while queue:
            current_state = queue.pop(0)
            if current_state in visited:
                continue

            table_ordered_states.append(current_state)
            visited.add(current_state)

            # Add all destination states to the queue
            for symbol in self.alphabet:
                destinations = set()
                for secondaryy_state in list_epsilon_cloture[current_state]:
                    if secondaryy_state in self.transitions and symbol in self.transitions[secondaryy_state]:
                        destinations.update(self.transitions[secondaryy_state][symbol])

                # Add unvisited destinations to the queue
                for finish_state in destinations:
                    if finish_state not in visited and finish_state not in queue:
                        queue.append(finish_state)

        # Add any remaining states that weren't reachable
        for state in self.states:
            if state not in visited:
                table_ordered_states.append(state)

    #### Step 3: Prepare headers
        headers = ["", "State"] + self.alphabet
        col_widths = [len(str(header)) for header in headers]

    #### Step 4: Prepare table rows
        table_rows = []
        for state in table_ordered_states:  # Use the ordered states instead of self.states
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
                for secondaryy_state in list_epsilon_cloture[state]:
                    if secondaryy_state in self.transitions and symbol in self.transitions[secondaryy_state]:
                        destinations.update(self.transitions[secondaryy_state][symbol])

                # Use function_to_sort to handle mixed types
                row.append(",".join(map(str, Automate.function_to_sort(destinations))) if destinations else "-")

    ######### Step 6: Adjust column width
            for i, value in enumerate(row):
                col_widths[i] = max(col_widths[i], len(value))

            table_rows.append(row)

    ##### Step 7: Print the formatted table
        header_row = " | ".join(header.ljust(col_widths[i]) for i, header in enumerate(headers))
        print(header_row)
        print("-" * len(header_row))  # Separator line
        for row in table_rows:
            print(" | ".join(row[i].ljust(col_widths[i]) for i in range(len(row))))

    ################################################################################################################
    # Fonction qui vérifient si l'automate valide une condition (standard, complet, déterministe)
    ################################################################################################################

    def is_standard(self):
        """
        Checks if the automaton is standardised.
        An automaton is standardised if:
        1. It has only one initial state
        2. No transitions lead to the initial state

        :return: bool - True if the automaton is standardised, False otherwise
        """
        # Check if there is exactly one initial state
        if len(self.initial_states) != 1:
            return False

        initial_state = self.initial_states[0]

        # Check if any transition leads to the initial state
        for state in self.states:
            if state in self.transitions:
                for symbol in self.transitions[state]:
                    if initial_state in self.transitions[state][symbol]:
                        return False

        return True

    def is_determinist(self):
        """
        Checks if the automaton is deterministic.
        An automaton is deterministic if:
        1. It has only one initial state
        2. For each state and each symbol, there is at most one transition
        3. There are no epsilon transitions

        :return: bool - True if the automaton is deterministic, False otherwise """
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


####################################################################################################################
    # Fonctions qui modifient l'automate
####################################################################################################################


    def standardise(self):
        """
        Standardises the automaton by creating a new initial state with epsilon transitions
        to all original initial states, and ensuring no transitions lead to the initial state.

        :return: A new standardised automaton
        """
        # If the automaton is already standardised, return a copy
        if self.is_standard():
            return self

        # Create a new state name that doesn't exist in the current automaton
        new_initial = "i"
        while new_initial in self.states:
            new_initial = new_initial + "i"

        # Create a copy of the current states and add the new initial state
        new_states = self.states.copy()
        new_states.append(new_initial)

        # Create new transitions list
        new_transitions = []

        # Add all existing transitions
        for state in self.transitions:
            for symbol in self.transitions[state]:
                for destination in self.transitions[state][symbol]:
                    new_transitions.append((state, symbol, destination))

        # Add epsilon transitions from the new initial state to all original initial states
        for initial_state in self.initial_states:
            new_transitions.append((new_initial, None, initial_state))

        # Create the new standardised automaton
        standardised = Automate(
            num_automate=self.num_automate,
            alphabet=self.alphabet,
            states=new_states,
            initial_states=[new_initial],
            final_states=self.final_states.copy(),
            transitions=new_transitions
        )

        return standardised



    def determinise(self):
        """
        Transforms the automaton into an equivalent deterministic automaton.
        This method builds a new automaton from the current one while preserving state names.
        Composite states like {9,19} will be named '919'.

        :return: A new deterministic automaton
        """


        if self.is_determinist():
            # If the automaton is already deterministic, return a copy
            return self


        ################################################################################################################
        #First Step : Andle epsilon transition, and make structure that list epsilon cloture state to link them after
        ################################################################################################################

        # Handle epsilon transitions first
        # Collect all epsilon transitions
        epsilon_transitions = []
        for state in self.states:
            if state in self.transitions and None in self.transitions[state]:
                for destination in self.transitions[state][None]:
                    epsilon_transitions.append((state, destination))

        # Create a list of epsilon closures for each state
        epsilon_closures = {}
        for state in self.states:
            epsilon_closures[state] = FileParser.compute_epsilon_closure({state}, epsilon_transitions)

        # Build the new automaton
        # Initial states: set of epsilon closures of initial states
        initial_epsilon_state = set()
        for initial_state in self.initial_states:
            initial_epsilon_state.update(epsilon_closures[initial_state])
        initial_epsilon_state_tuple = tuple(Automate.function_to_sort(initial_epsilon_state))

        ################################################################################################################
        # Second Step : create new state who combine ancient state for the new determinise automaton
        ################################################################################################################
        dico_new_states = {}  #
        states_to_process = [initial_epsilon_state_tuple]
        processed_states = set()
        new_transitions = []



        # First pass: Generate all the new state names
        while states_to_process:
            current_bigstate = states_to_process.pop(0)
            if current_bigstate in processed_states:
                continue

            processed_states.add(current_bigstate)

            # Generate the combined state name for this macrostate
            new_state_name = Automate.generate_state_name(current_bigstate)
            dico_new_states[current_bigstate] = new_state_name

            # For each symbol in the alphabet
            for symbol in self.alphabet:
                # Calculate the set of states reachable with this symbol
                next_states = set()
                for state in current_bigstate:
                    if state in self.transitions and symbol in self.transitions[state]:
                        next_states.update(self.transitions[state][symbol])

                # Apply epsilon closures to the reached states
                epsilon_closure_next = set()
                for state in next_states:
                    epsilon_closure_next.update(epsilon_closures[state])

                if epsilon_closure_next:
                    # Convert to tuple to use as a key
                    epsilon_closure_next_tuple = tuple(Automate.function_to_sort(epsilon_closure_next))  # Use function_to_sort here

                    # Add new state to process if not seen before
                    if epsilon_closure_next_tuple not in dico_new_states and epsilon_closure_next_tuple not in states_to_process:
                        states_to_process.append(epsilon_closure_next_tuple)

        ################################################################################################################
        # Third Step : give the right transition for every new state
        ################################################################################################################
        for big_state in processed_states:
            current_state_name = dico_new_states[big_state]

            # For each symbol in the alphabet
            for symbol in self.alphabet:
                # Calculate the set of states reachable with this symbol
                next_states = set()
                for state in big_state:
                    if state in self.transitions and symbol in self.transitions[state]:
                        next_states.update(self.transitions[state][symbol])

                # Apply epsilon closures
                epsilon_closure_next = set()
                for state in next_states:
                    epsilon_closure_next.update(epsilon_closures[state])

                if epsilon_closure_next:
                    epsilon_closure_next_tuple = tuple(Automate.function_to_sort(epsilon_closure_next))  # Use function_to_sort here
                    next_state_name = dico_new_states[epsilon_closure_next_tuple]

                    # Add the transition using state names
                    new_transitions.append((current_state_name, symbol, next_state_name))

        ################################################################################################################
        # Last step : find new itnitial state and final state
        ################################################################################################################
        new_states = list(dico_new_states.values())

        # Determine the initial and final states of the new automaton
        new_initial_states = [dico_new_states[initial_epsilon_state_tuple]]

        new_final_states = []
        for big_state, state_name in dico_new_states.items():
            # A big_state is final if at least one of its states is final
            if any(state in self.final_states for state in big_state):
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



    # Fix for the complete() method in Classe_Automate.py

    def complete(self):
        """
        Completes the automaton by adding a sink state and missing transitions.
        Unlike the determinise() method, this does not determinise the automaton first.

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

    def minimise(self):
        """
        Minimises the automaton using Moore's algorithm.
        The automaton must be deterministic and complete.

        Returns:
        - A new minimised automaton
        """
        ################################################################################################################
        # Preliminary Step : Check the condition to minimise the automaton :
        ################################################################################################################
        if not self.is_determinist():
            print("The automaton must be deterministic, making determinisation : ")
            automaton = self.determinise()
        else:
            automaton = self
    # Dans notre version de notre projet on peut compléter et déterminiser séparément
        if not automaton.is_complete():
            print("The automaton must be complete, making completion : ")
            automaton = automaton.complete()

        print("Minimisation : ")

        ################################################################################################################
        # First step : Create the first group (teta) terminal State or none terminale state
        ################################################################################################################
        current_teta = {}
        for state in automaton.states:
            if state in automaton.final_states:
                current_teta[state] = 1  # Final states
            else:
                current_teta[state] = 0  # Non-final states

        # Start the refinement process
        cpt = 1
        stable = False

        while not stable:
            print(f"Teta number {cpt}: {current_teta}")

            ################################################################################################################
            # Second Step : Make a loop  to create new teta until the automaton is minimised
            ################################################################################################################
            new_teta = {}

            # For each state, create a key based on its current class and transition targets
            keys = {}
            ################################################################################################################
            # Creation of indivual keys for every state
            ################################################################################################################
            for state in automaton.states:
                # Start with the current class
                key = [current_teta[state]]

                # For each symbol, add the class of the target state
                for transition_letter in automaton.alphabet:
                    if state in automaton.transitions and transition_letter in automaton.transitions[state]:
                        target_state = automaton.transitions[state][transition_letter]
                        key.append((transition_letter, current_teta[target_state[0]]))

                # Store the signature as a tuple (hashable) and avoid double
                key_tuple = tuple(key)
                keys[state] = key_tuple
        ################################################################################################################
        # Complete general-dico_key by assigning a key for every state
        ################################################################################################################
            # Group states by signature
            key_groups = {}
            for state, key in keys.items():
                if key not in key_groups:
                    key_groups[key] = []
                key_groups[key].append(state)

        ################################################################################################################
        # Create a new class for every key
        ################################################################################################################
            new_class = 0
            for key, states in key_groups.items():
                for state in states:
                    new_teta[state] = new_class
                new_class += 1

            # Check if the partition is stable
            if new_teta == current_teta:
                stable = True
            else:
                current_teta = new_teta

            cpt += 1


        print("Minimisation completed : ")

        # Build the minimised automaton
        # Group states by their equivalence class
        different_classes = {}
        for state, class_number in current_teta.items():
            if class_number not in different_classes:
                different_classes[class_number] = []
            different_classes[class_number].append(state)


        # Create new states for each equivalence class
        new_states = []
        class_to_state = {}
        for class_number in different_classes:
            state_name = f"q{class_number}"
            new_states.append(state_name)
            class_to_state[class_number] = state_name

        # Determine initial and final states
        new_initial_states = []
        new_final_states = []

        for class_id, states in different_classes.items():
            state_name = class_to_state[class_id]

            # If any state in the class is initial, the class is initial
            if any(state in automaton.initial_states for state in states):
                new_initial_states.append(state_name)

            # If any state in the class is final, the class is final
            if any(state in automaton.final_states for state in states):
                new_final_states.append(state_name)

        # Create transitions for the new automaton
        new_transitions = []
        for class_id, states in different_classes.items():
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

        # Create the new minimised automaton
        minimised_automaton = Automate(
            num_automate=automaton.num_automate,
            alphabet=automaton.alphabet,
            states=new_states,
            initial_states=new_initial_states,
            final_states=new_final_states,
            transitions=new_transitions
        )

        return minimised_automaton

    def recognise_word(self, word):
        """
        Tests if a word is accepted by the automaton.
        This implementation works for both deterministic and non-deterministic automata,
        and properly handles epsilon transitions.

        Args:
            word (str): The word to test

        Returns:
            bool: True if the word is accepted, False otherwise
        """
        # Collect all epsilon transitions
        epsilon_transitions = []
        for state in self.states:
            if state in self.transitions and None in self.transitions[state]:
                for destination in self.transitions[state][None]:
                    epsilon_transitions.append((state, destination))

        # Compute epsilon closure of initial states
        current_states = set()
        for initial_state in self.initial_states:
            current_states.update(FileParser.compute_epsilon_closure({initial_state}, epsilon_transitions))

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

            # Compute epsilon closure of the next states
            current_states = set()
            for state in next_states:
                current_states.update(FileParser.compute_epsilon_closure({state}, epsilon_transitions))

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
            print("Warning: The automaton should be deterministic for complement to work correctly.")
            print("Determinising the automaton...")
            automaton = self.determinise()
        else:
            automaton = self

        if not automaton.is_complete():
            print("Warning: The automaton should be complete for complement to work correctly.")
            print("Completing the automaton...")
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
