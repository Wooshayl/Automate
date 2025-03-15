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
            print("4. Exit")

            choice = input("Enter your choice: ")

            if choice == "1":
                self.select_automaton()
            elif choice == "2":
                self.check_determinism()
            elif choice == "3":
                self.determinize_automaton()
            elif choice == "4":
                print("Exiting the program. Goodbye!")
                self.running = False
            else:
                print("⚠ Invalid choice. Please enter a number between 1 and 4.")

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



