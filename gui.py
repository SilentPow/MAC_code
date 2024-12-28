### gui.py
import tkinter as tk
from PIL import Image, ImageTk
import cv2
import threading
import numpy as np

class GameGUI:
    def __init__(self, root, player, update_callback):
        self.root = root
        self.player = player
        self.update_callback = update_callback  # Callback to update the logic
        self.root.title(f"Player {self.player} Reel Swiping Game")
        self.root.geometry("600x600")
        self.root.configure(bg="#282c34")

        # Canvas for Player Video
        self.player_label = tk.Label(self.root, text=f"Player {self.player}: Tap to Swipe", font=("Helvetica", 12), bg="#3c4049", fg="white")
        self.player_label.pack(pady=10)
        self.player_canvas = tk.Canvas(self.root, width=550, height=500, bg="#1e222a", highlightthickness=0)
        self.player_canvas.pack(pady=10)
        self.player_canvas.bind("<Button-1>", lambda e: self.update_callback(self.player))  # Touch for this player

    def update_status(self, swipes):
        self.player_label.config(text=f"Player {self.player}: Swipes: {swipes}")

    def set_frozen(self, frozen):
        self.player_label.config(text=f"Player {self.player}: Frozen!" if frozen else f"Player {self.player}: Swipes:", fg="red" if frozen else "white")

    def update_video(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(image=Image.fromarray(frame))
        self.player_canvas.create_image(0, 0, anchor=tk.NW, image=img)
        self.player_canvas.image = img