import tkinter as tk

class GameGUI:
    def __init__(self, root, update_callback):
        self.root = root
        self.update_callback = update_callback  # Callback to update the logic
        self.root.title("Two-Player Reel Swiping Game")
        self.root.geometry("600x600")
        self.root.configure(bg="#282c34")

        # GUI Components
        self.top_frame = tk.Frame(self.root, bg="#3c4049", height=100)
        self.top_frame.pack(fill="x", side="top")

        self.middle_frame = tk.Frame(self.root, bg="#282c34", height=400)
        self.middle_frame.pack(fill="both", expand=True, side="top")

        self.bottom_frame = tk.Frame(self.root, bg="#3c4049", height=100)
        self.bottom_frame.pack(fill="x", side="bottom")

        self.title_label = tk.Label(
            self.top_frame, text="Two-Player Reel Swiping Game", font=("Helvetica", 20, "bold"), bg="#3c4049", fg="white"
        )
        self.title_label.pack(pady=10)

        self.timer_label = tk.Label(
            self.top_frame, text="Timer: 00:00", font=("Helvetica", 14), bg="#3c4049", fg="lightgray"
        )
        self.timer_label.pack()

        self.player1_label = tk.Label(
            self.middle_frame, text="Player 1: Left Click to Swipe", font=("Helvetica", 12), bg="#282c34", fg="white"
        )
        self.player1_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        self.player2_label = tk.Label(
            self.middle_frame, text="Player 2: Right Click to Swipe", font=("Helvetica", 12), bg="#282c34", fg="white"
        )
        self.player2_label.grid(row=0, column=1, padx=20, pady=10, sticky="e")

        self.status_label = tk.Label(
            self.middle_frame,
            text="Player 1 Swipes: 0 | Player 2 Swipes: 0",
            font=("Helvetica", 12),
            bg="#282c34",
            fg="lightgray",
        )
        self.status_label.grid(row=1, column=0, columnspan=2, pady=10)

        self.canvas = tk.Canvas(self.bottom_frame, width=550, height=300, bg="#1e222a", highlightthickness=0)
        self.canvas.pack(pady=10)

    def update_status(self, player1_swipes, player2_swipes):
        self.status_label.config(
            text=f"Player 1 Swipes: {player1_swipes} | Player 2 Swipes: {player2_swipes}"
        )

    def set_frozen(self, player, frozen):
        if player == 1:
            self.player1_label.config(text="Player 1: Frozen!" if frozen else "Player 1: Left Click to Swipe", fg="red" if frozen else "white")
        elif player == 2:
            self.player2_label.config(text="Player 2: Frozen!" if frozen else "Player 2: Right Click to Swipe", fg="red" if frozen else "white")
