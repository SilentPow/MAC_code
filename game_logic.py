import cv2
import os
import random
import numpy as np
from threading import Thread
from tkinter import messagebox

class GameLogic:
    def __init__(self, video_folder, gui, root):
        self.gui = gui
        self.root = root
        self.video_folder = video_folder
        self.player1_swipes = 0
        self.player2_swipes = 0
        self.player1_frozen = False
        self.player2_frozen = False
        self.videos = [f for f in os.listdir(video_folder) if f.endswith(('.mp4', '.avi'))]
        self.video_thread = Thread(target=self.display_videos)
        self.video_thread.daemon = True
        self.video_thread.start()
        self.current_videos = {"player1": None, "player2": None}
        self.reload_video_flags = {"player1": False, "player2": False}  # Initialize here
        self.stop_video = False

    def player_swipe(self, player):
        if player == 1 and not self.player1_frozen:
            self.player1_swipes += 1
            self.check_freeze(2)

            # Select a new random video for Player 1
            self.current_videos["player1"] = self.get_random_video()
            self.reload_video_flags["player1"] = True

        elif player == 2 and not self.player2_frozen:

            self.player2_swipes += 1
            self.check_freeze(1)

            # Select a new random video for Player 2
            self.current_videos["player2"] = self.get_random_video()
            self.reload_video_flags["player2"] = True

        self.gui.update_status(self.player1_swipes, self.player2_swipes)

    def check_freeze(self, player_to_freeze):

        if player_to_freeze == 1 and self.player2_swipes % 5 == 0:
            self.freeze_player(1)

        elif player_to_freeze == 2 and self.player1_swipes % 5 == 0:
            self.freeze_player(2)

    def freeze_player(self, player):

        if player == 1:
            self.player1_frozen = True
            self.gui.set_frozen(1, True)
            self.gui.root.after(1000, lambda: self.unfreeze_player(1))  # Schedule unfreeze after 3 seconds

        elif player == 2:
            self.player2_frozen = True
            self.gui.set_frozen(2, True)
            self.gui.root.after(1000, lambda: self.unfreeze_player(2))  # Schedule unfreeze after 3 seconds

    def unfreeze_player(self,player):
        if player == 1:
            self.player1_frozen = False
            self.gui.set_frozen(1, False)  # Update GUI to remove Player 1's frozen state
        elif player == 2:
            self.player2_frozen = False
            self.gui.set_frozen(2, False)  # Update GUI to remove Player 2's frozen state

    def get_random_video(self):
        if not self.videos:
            messagebox.showerror("Error", "No videos found in the folder!")
            return None
        return os.path.join(self.video_folder, random.choice(self.videos))

    def display_videos(self):
        print("Display_Video started")
        width = 320  # Half of the total window width
        height = 240  # Video frame height
        player1_cap = None
        player2_cap = None

        while not self.stop_video:
            # Reload Player 1 video if flagged
            if self.reload_video_flags["player1"] and self.current_videos["player1"]:
                if player1_cap:
                    player1_cap.release()
                player1_cap = cv2.VideoCapture(self.current_videos["player1"])
                self.reload_video_flags["player1"] = False

            # Reload Player 2 video if flagged
            if self.reload_video_flags["player2"] and self.current_videos["player2"]:
                if player2_cap:
                    player2_cap.release()
                player2_cap = cv2.VideoCapture(self.current_videos["player2"])
                self.reload_video_flags["player2"] = False

            # Create blank frames as fallback
            player1_frame = np.zeros((height, width, 3), dtype=np.uint8)
            player2_frame = np.zeros((height, width, 3), dtype=np.uint8)

            # Read frames for Player 1
            if player1_cap and player1_cap.isOpened() and not self.player1_frozen:
                ret1, frame1 = player1_cap.read()
                if ret1:
                    player1_frame = cv2.resize(frame1, (width, height))

            # Red overlay if Player 1 is frozen
            if self.player1_frozen:
                overlay = np.zeros_like(player1_frame)
                overlay[:, :] = [0, 0, 255]  # Red color
                player1_frame = cv2.addWeighted(player1_frame, 0.5, overlay, 0.5, 0)
                cv2.putText(
                    player1_frame,
                    "Frozen!",
                    (width // 4, height // 2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

            # Read frames for Player 2
            if player2_cap and player2_cap.isOpened() and not self.player2_frozen:
                ret2, frame2 = player2_cap.read()
                if ret2:
                    player2_frame = cv2.resize(frame2, (width, height))

            # Red overlay if Player 2 is frozen
            if self.player2_frozen:
                overlay = np.zeros_like(player2_frame)
                overlay[:, :] = [0, 0, 255]  # Red color
                player2_frame = cv2.addWeighted(player2_frame, 0.5, overlay, 0.5, 0)
                cv2.putText(
                    player2_frame,
                    "Frozen!",
                    (width // 4, height // 2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

            # Add borders and labels
            player1_frame = cv2.copyMakeBorder(player1_frame, 40, 0, 10, 10, cv2.BORDER_CONSTANT, value=[50, 50, 50])
            player2_frame = cv2.copyMakeBorder(player2_frame, 40, 0, 10, 10, cv2.BORDER_CONSTANT, value=[50, 50, 50])

            cv2.putText(
                player1_frame,
                "Player 1",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                player2_frame,
                "Player 2",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            # Combine frames horizontally
            combined_frame = np.hstack((player1_frame, player2_frame))

            # Display the combined frame
            cv2.imshow("Reels", combined_frame)

            if cv2.waitKey(30) & 0xFF == ord('q'):
                self.stop_video = True
                break

        if player1_cap:
            player1_cap.release()
        if player2_cap:
            player2_cap.release()
        cv2.destroyAllWindows()