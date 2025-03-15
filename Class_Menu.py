from Classe_Automate import *

class Menu:
    """Handles user interaction for selecting and testing automata."""

    def __init__(self):
        self.running = True  # Control loop execution

    def start(self):
        """Displays the main menu and handles user input."""
        while self.running:
            print("\n=== Automaton Tester ===")
            print("1. Select an automaton and display it")
            print("2. Exit")

            choice = input("Enter your choice: ")

            if choice == "1":
                self.select_automaton()
            elif choice == "2":
                print("Exiting the program. Goodbye!")
                self.running = False
            else:
                print("⚠ Invalid choice. Please enter 1 or 2.")

    def select_automaton(self):
        """Prompts the user to enter an automaton number and displays it."""
        try:
            file_number = int(input("Enter the automaton number: "))
            automate = Automate.from_file(file_number)

            if automate:
                automate.display_table()
            else:
                print(f"⚠ Error: Could not load automaton {file_number}.")
        except ValueError:
            print("⚠ Invalid input. Please enter a valid number.")

