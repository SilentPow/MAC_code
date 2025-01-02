import tkinter as tk
from gui import GameGUI
from game_logic import GameLogic
import threading
from queue import Queue

if __name__ == "__main__":
    video_folder = "./videos"

    # Create the main thread's event queue
    gui_queues = {"player1": Queue(), "player2": Queue()}

    # Player 1 GUI
    root1 = tk.Tk()
    gui1 = GameGUI(root1, 1, lambda p: gui_queues["player1"].put(p))

    # Player 2 GUI
    root2 = tk.Toplevel()  # Create a second window on the main thread
    gui2 = GameGUI(root2, 2, lambda p: gui_queues["player2"].put(p))

    # Initialize GameLogic
    game_logic = GameLogic(video_folder, gui1, gui2)

    # Define GUI update loop
    def gui_update():
        try:
            # Process Player 1 actions
            while not gui_queues["player1"].empty():
                player = gui_queues["player1"].get_nowait()
                game_logic.player_swipe(player)

            # Process Player 2 actions
            while not gui_queues["player2"].empty():
                player = gui_queues["player2"].get_nowait()
                game_logic.player_swipe(player)

        except Exception as e:
            print(f"Error in GUI update loop: {e}")
        
        # Schedule next update
        root1.after(50, gui_update)

    # Start the update loop
    gui_update()

    # Run both windows
    root1.mainloop()