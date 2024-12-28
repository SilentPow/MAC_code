import tkinter as tk
from gui import GameGUI
from game_logic import GameLogic

if __name__ == "__main__":
    video_folder = "./videos"
    root = tk.Tk()
    gui = GameGUI(root, None)  # GUI initialized
    game_logic = GameLogic(video_folder, gui, root)  # Logic linked to GUI
    gui.canvas.bind("<Button-1>", lambda e: game_logic.player_swipe(1))  # Link Player 1
    gui.canvas.bind("<Button-3>", lambda e: game_logic.player_swipe(2))  # Link Player 2
    root.mainloop()
