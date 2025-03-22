from Classe_Automate import *


class Menu:
    """Handles user interaction for selecting and testing automata."""

    def __init__(self):
        self.running = True             # Control loop execution
        self.current_automate = None    # Store the selected automaton
        self.automaton_number = None    # Store the automaton file number

    def start(self):
        """Displays the main menu and handles user input."""

        while self.running:
            self._display_main_menu()
            choice = input("Enter your choice: ")

            if choice == "1":
                self.select_automaton()
            elif choice == "2":
                if self._check_automaton_selected():
                    self._display_operations_menu()
            elif choice == "3":
                print("Cheers for trying our project out, if there are any errors please contact the team.")
                self.running = False
            else:
                print("Invalid choice. Please enter a number between 1 and 3.")

    def _display_main_menu(self):
        """Displays the main menu options."""

        print("\n===================== Automaton Tester =====================")
        print("1. Select the automaton you'd like to see")
        if self.current_automate:
            print(f"  Currently selected: Automaton n°={self.automaton_number}")
        else:
            print("  No automaton currently selected")
        print("2. Perform our proposed operations on the selected automaton")
        print("3. Exit the program")
        print("============================================================")

    def _display_operations_menu(self):
        """Displays the operations menu and handles user input."""
        operations_running = True

        while operations_running and self.current_automate:
            print("\n========== Automaton Operations ==========")
            print(f"Currently working with: Automaton {self.automaton_number}")
            print("1. Display automaton details")
            print("2. Check automaton properties (deterministic, complete, standard)")
            print("3. Determinise automaton")
            print("4. Complete automaton")
            print("5. Minimise automaton")
            print("6. Test word recognition")
            print("7. Create complement automaton")
            print("8. Standardise automaton")
            print("9. Return to main menu")
            print("=========================================")

            op_choice = input("Enter your operation choice: ")

            if op_choice == "1":
                self.display_automaton_details()
            elif op_choice == "2":
                self.check_automaton_properties()
            elif op_choice == "3":
                self.determinise_automaton()
            elif op_choice == "4":
                self.complete_automaton()
            elif op_choice == "5":
                self.minimise_automaton()
            elif op_choice == "6":
                self.test_word_recognition()
            elif op_choice == "7":
                self.create_complement_automaton()
            elif op_choice == "8":
                self.standardise_automaton()
            elif op_choice == "9":
                operations_running = False
            else:
                print("Invalid choice. Please enter a number between 1 and 9.")

    def _check_automaton_selected(self):
        """Checks if an automaton is selected and informs the user if not."""

        if not self.current_automate:
            print("Please select an automaton first (Option 1 in the main menu).")
            return False
        return True

    def select_automaton(self):
        """Prompts the user to enter an automaton number and displays it."""

        try:
            file_number = int(input("Enter the automaton number: "))
            automaton = Automate.from_file(file_number)

            if automaton:
                self.current_automate = automaton
                # Store the file number for reference
                self.automaton_number = file_number
                print(f"\nAutomaton {file_number} successfully loaded.")
                self.current_automate.display_table()
            else:
                print(f"Error: Could not load automaton {file_number}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    def display_automaton_details(self):
        """Displays detailed information about the current automaton."""

        print("\n=== Automaton Details ===")
        self.current_automate.display_value()

    def check_automaton_properties(self):
        """Checks if the current automaton is deterministic, complete, and standardised."""

        print("\n=== Automaton Properties ===")

        # Check if deterministic
        is_det = self.current_automate.is_determinist()
        print(f"Deterministic: {'Yes' if is_det else 'No'}")

        # Check if complete
        is_comp = self.current_automate.is_complete()
        print(f"Complete: {'Yes' if is_comp else 'No'}")

        # Check if standardised
        is_std = self.current_automate.is_standard()
        print(f"Standardised: {'Yes' if is_std else 'No'}")

    def determinise_automaton(self):
        """Determinises the current automaton."""

        if self.current_automate.is_determinist():
            print("The automaton is already deterministic.")
            return

        self.current_automate = self.current_automate.determinise()
        print("Automaton successfully determinised.")
        self.current_automate.display_table()

    def complete_automaton(self):
        """Completes the current automaton."""

        if self.current_automate.is_complete():
            print("The automaton is already complete.")
            return

        self.current_automate = self.current_automate.complete()
        print("Automaton successfully completed.")
        self.current_automate.display_table()

    def minimise_automaton(self):
        """Minimises the current automaton."""

        self.current_automate = self.current_automate.minimise()
        print("Automaton successfully minimised.")
        self.current_automate.display_table()

    def test_word_recognition(self):
        """Tests if a word is recognised by the current automaton."""

        word = input("Enter the word to test: ")

        if self.current_automate.recognise_word(word):
            print(f"The word '{word}' is accepted by the automaton.")
        else:
            print(f"The word '{word}' is NOT accepted by the automaton.")

    def create_complement_automaton(self):
        """Creates the complement of the current automaton."""

        self.current_automate = self.current_automate.complement()
        print("Complement automaton successfully created.")
        self.current_automate.display_table()

    def standardise_automaton(self):
        """Standardises the current automaton."""

        if self.current_automate.is_standard():
            print("The automaton is already standardised.")
            return

        self.current_automate = self.current_automate.standardise()
        print("Automaton successfully standardised.")
        self.current_automate.display_table()
