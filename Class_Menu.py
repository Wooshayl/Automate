from Classe_Automate import *


class Menu:
    """Handles user interaction for selecting and testing automata."""

    def __init__(self):
        self.running = True  # Control loop execution
        self.current_automate = None  # Store the selected automaton

    def start(self):
        """Displays the main menu and handles user input."""
        while self.running:
            print("\n=== Automaton Tester ===")
            print("1. Select an automaton and display it")
            print("2. Check if automaton is deterministic")
            print("3. Determinize automaton")
            print("4. Check if automaton is complete")
            print("5. Complete automaton")
            print("6. Minimize automaton")
            print("7. Test word recognition")  # Nouvelle option
            print("8. Create complement automaton")  # Nouvelle option
            print("9. Exit")  # Modifié

            choice = input("Enter your choice: ")

            if choice == "1":
                self.select_automaton()
            elif choice == "2":
                self.check_determinism()
            elif choice == "3":
                self.determinize_automaton()
            elif choice == "4":
                self.check_completeness()
            elif choice == "5":
                self.complete_automaton()
            elif choice == "6":
                self.minimize_automaton()
            elif choice == "7":  # Nouvelle fonction
                self.test_word_recognition()
            elif choice == "8":  # Nouvelle fonction
                self.create_complement_automaton()
            elif choice == "9":  # Modifié
                print("Exiting the program. Goodbye!")
                self.running = False
            else:
                print("⚠ Invalid choice. Please enter a number between 1 and 9.")  # Modifié

    def check_determinism(self):
        """Checks if the current automaton is deterministic."""
        if not self.current_automate:
            print("⚠ Please select an automaton first.")
            return

        if self.current_automate.is_determinist():
            print("✓ The automaton is deterministic.")
        else:
            print("✗ The automaton is NOT deterministic.")

    def determinize_automaton(self):
        """Determinizes the current automaton."""
        if not self.current_automate:
            print("⚠ Please select an automaton first.")
            return

        if self.current_automate.is_determinist():
            print("✓ The automaton is already deterministic.")
            return

        print("Determinizing automaton...")
        self.current_automate = self.current_automate.determinize()
        print("✓ Automaton successfully determinized.")
        self.current_automate.display_table()

    def check_completeness(self):
        """Checks if the current automaton is complete."""
        if not self.current_automate:
            print("⚠ Please select an automaton first.")
            return

        if self.current_automate.is_complete():
            print("✓ The automaton is complete.")
        else:
            print("✗ The automaton is NOT complete.")

    def complete_automaton(self):
        """Completes the current automaton."""
        if not self.current_automate:
            print("⚠ Please select an automaton first.")
            return

        if self.current_automate.is_complete():
            print("✓ The automaton is already complete.")
            return

        print("Completing automaton...")
        self.current_automate = self.current_automate.complete()
        print("✓ Automaton successfully completed.")
        self.current_automate.display_table()


    def select_automaton(self):
        """Prompts the user to enter an automaton number and displays it."""
        try:
            file_number = int(input("Enter the automaton number: "))
            self.current_automate = Automate.from_file(file_number)

            if self.current_automate:
                print("\nAutomaton successfully loaded.")
                self.current_automate.display_table()
            else:
                print(f"⚠ Error: Could not load automaton {file_number}.")
        except ValueError:
            print("⚠ Invalid input. Please enter a valid number.")

    def minimize_automaton(self):
        """Minimizes the current automaton."""
        if not self.current_automate:
            print("⚠ Please select an automaton first.")
            return

        print("Minimizing automaton...")
        self.current_automate = self.current_automate.minimize()
        print("✓ Automaton successfully minimized.")
        self.current_automate.display_table()

    def test_word_recognition(self):
        """Tests if a word is recognized by the current automaton."""
        if not self.current_automate:
            print("⚠ Please select an automaton first.")
            return

        word = input("Enter the word to test: ")

        if self.current_automate.recognize_word(word):
            print(f"✓ The word '{word}' is accepted by the automaton.")
        else:
            print(f"✗ The word '{word}' is NOT accepted by the automaton.")

    def create_complement_automaton(self):
        """Creates the complement of the current automaton."""
        if not self.current_automate:
            print("⚠ Please select an automaton first.")
            return

        print("Creating complement automaton...")
        self.current_automate = self.current_automate.complement()
        print("✓ Complement automaton successfully created.")
        self.current_automate.display_table()
