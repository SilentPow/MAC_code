### game_logic.py
import cv2
import os
import random
import numpy as np
from tkinter import messagebox
import threading

class GameLogic:
    def __init__(self, video_folder, gui1, gui2):
        self.gui1 = gui1
        self.gui2 = gui2
        self.video_folder = video_folder
        self.player1_swipes = 0
        self.player2_swipes = 0
        self.player1_frozen = False
        self.player2_frozen = False
        self.videos = [f for f in os.listdir(video_folder) if f.endswith(('.mp4', '.avi'))]
        self.current_videos = {"player1": None, "player2": None}
        self.reload_video_flags = {"player1": False, "player2": False}
        self.stop_video = False

        # Threads for each player video
        self.player1_thread = threading.Thread(target=self.display_video, args=("player1", self.gui1))
        self.player1_thread.daemon = True
        self.player1_thread.start()

        self.player2_thread = threading.Thread(target=self.display_video, args=("player2", self.gui2))
        self.player2_thread.daemon = True
        self.player2_thread.start()

    def player_swipe(self, player):
        if player == 1 and not self.player1_frozen:
            self.player1_swipes += 1
            self.check_freeze(2)
            self.current_videos["player1"] = self.get_random_video()
            self.reload_video_flags["player1"] = True
            self.gui1.update_status(self.player1_swipes)

        elif player == 2 and not self.player2_frozen:
            self.player2_swipes += 1
            self.check_freeze(1)
            self.current_videos["player2"] = self.get_random_video()
            self.reload_video_flags["player2"] = True
            self.gui2.update_status(self.player2_swipes)

    def check_freeze(self, player_to_freeze):
        if player_to_freeze == 1 and self.player2_swipes % 5 == 0:
            self.freeze_player(1)

        elif player_to_freeze == 2 and self.player1_swipes % 5 == 0:
            self.freeze_player(2)

    def freeze_player(self, player):
        if player == 1:
            self.player1_frozen = True
            self.gui1.set_frozen(True)
            self.gui1.root.after(3000, lambda: self.unfreeze_player(1))

        elif player == 2:
            self.player2_frozen = True
            self.gui2.set_frozen(True)
            self.gui2.root.after(3000, lambda: self.unfreeze_player(2))

    def unfreeze_player(self, player):
        if player == 1:
            self.player1_frozen = False
            self.gui1.set_frozen(False)
        elif player == 2:
            self.player2_frozen = False
            self.gui2.set_frozen(False)

    def get_random_video(self):
        if not self.videos:
            messagebox.showerror("Error", "No videos found in the folder!")
            return None
        return os.path.join(self.video_folder, random.choice(self.videos))

    def display_video(self, player, gui):
        cap = None
        width, height = 550, 500

        while not self.stop_video:
            if self.reload_video_flags[player] and self.current_videos[player]:
                if cap:
                    cap.release()
                cap = cv2.VideoCapture(self.current_videos[player])
                self.reload_video_flags[player] = False

            frame = np.zeros((height, width, 3), dtype=np.uint8)

            if cap and cap.isOpened() and not (self.player1_frozen if player == "player1" else self.player2_frozen):
                ret, video_frame = cap.read()
                if ret:
                    frame = cv2.resize(video_frame, (width, height))

            if player == "player1" and self.player1_frozen:
                overlay = np.zeros_like(frame)
                overlay[:, :] = [0, 0, 255]
                frame = cv2.addWeighted(frame, 0.5, overlay, 0.5, 0)

            if player == "player2" and self.player2_frozen:
                overlay = np.zeros_like(frame)
                overlay[:, :] = [0, 0, 255]
                frame = cv2.addWeighted(frame, 0.5, overlay, 0.5, 0)

            gui.update_video(frame)

            if cv2.waitKey(30) & 0xFF == ord('q'):
                self.stop_video = True
                break

        if cap:
            cap.release()