import os


def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def pause(message: str = "Press Enter to continue..."):
    """Pauses execution until the user presses Enter."""
    print()
    input(message)
