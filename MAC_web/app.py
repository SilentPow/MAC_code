from flask import Flask, render_template, jsonify, send_from_directory, request, redirect, url_for, send_file
from flask import Response
from flask_socketio import SocketIO, emit, join_room
from arduino import open_valve, close_valve, get_serial_connection, close_serial
import time
import threading
import os
import random
import json
import serial
from serial.tools import list_ports
import sys

LEADERBOARD_FILE = "leaderboard.json"

stop_event = threading.Event()

app = Flask(__name__, static_folder='static', template_folder='html')
socketio = SocketIO(app)
app.config["SERVER_NAME"] = "localhost:5000"

# Paths to video folders
NORMAL_VIDEOS_FOLDER = os.path.expanduser("./videos/normal")
ADS_VIDEOS_FOLDER = os.path.expanduser("./videos/ad")
ICE_VIDEOS_FOLDER = os.path.expanduser("./videos/ice")

# Supported video formats
SUPPORTED_FORMATS = ['mp4', 'webm', 'ogg']

# Initialize video counts
player_states = {
    1: {"name": None, "swipe_count": 0, "normal_count": 0, "last_videos": []},
    2: {"name": None, "swipe_count": 0, "normal_count": 0, "last_videos": []},
}

game_state = {
    "player1_ready": False,
    "player2_ready": False, 
    "game_running": False  # Whether the game is active
}

def reset_game():
    """Reset swipe counts and states for both players."""
    for player_id in player_states:
        player_states[player_id]["name"] = None
        player_states[player_id]["swipe_count"] = 0
        player_states[player_id]["normal_count"] = 0
        player_states[player_id]["last_videos"] = []
    game_state["player1_ready"] = False
    game_state["player2_ready"] = False
    game_state["game_running"] = False
    print("reset_game")
    stop_event.set()  # Reset the stop event for the next game

def get_video_list(folder):
    """Retrieve video files from a given folder."""
    return [
        f for f in os.listdir(folder)
        if f.split('.')[-1].lower() in SUPPORTED_FORMATS
    ]

video_cache = {
    "normal": [],
    "ad": [],
    "ice": []
}

# Populate video cache
for folder_name, folder_path in {
    "normal": NORMAL_VIDEOS_FOLDER,
    "ad": ADS_VIDEOS_FOLDER,
    "ice": ICE_VIDEOS_FOLDER,
}.items():
    if os.path.exists(folder_path):
        video_cache[folder_name] = [
            f for f in os.listdir(folder_path) if f.endswith(".m3u8")]

def get_cached_video_list(video_type):
    return video_cache.get(video_type, [])

def start_game_timer():
    """Start the game timer for one minute and determine the winner."""
    with app.app_context():  # Ensure app context for URL generation
        stop_event.clear()
        for i in range(60):
            print(i)
            if stop_event.is_set():
                print("Game timer stopped.")
                return  # Exit the thread gracefully
            time.sleep(1)  # Wait for one second each iteration
        print(game_state["game_running"])
        game_state["game_running"] = False

        # Determine the winner based on swipe counts
        if player_states[1]["swipe_count"] > player_states[2]["swipe_count"]:
            winner_id = 1
            loser_id = 2
        elif player_states[1]["swipe_count"] < player_states[2]["swipe_count"]:
            winner_id = 2
            loser_id = 1
        else:
            winner_id = None
            loser_id = None

        winner_score = player_states[winner_id]["swipe_count"] if winner_id else 0
        loser_score = player_states[loser_id]["swipe_count"] if loser_id else 0

        if winner_id:
            update_leaderboard(player_states[winner_id]["name"], winner_score)
        if loser_id:
            update_leaderboard(player_states[loser_id]["name"], loser_score)

        print("timer_game_over")
        # Notify players
        #open_valve(winner_id)
        socketio.emit("game_over", {
            "winner": winner_id,
            "winner_redirect": f"{url_for('winner_page')}?score={winner_score}",
            "loser_redirect": f"{url_for('loser_page')}?score={loser_score}"
        })  

        # Reset the game state
        reset_game()


def load_leaderboard():
    try:
        with open(LEADERBOARD_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return [{"game_name": "Swipe Master", "leaderboard": []}]

# Save leaderboard to file
def save_leaderboard(data):
    with open(LEADERBOARD_FILE, 'w') as file:
        json.dump(data, file, indent=4)

# Update leaderboard logic
def update_leaderboard(player_name, score):
    leaderboard_data = load_leaderboard()
    leaderboard = leaderboard_data[0]["leaderboard"]

    new_entry = {
        "player_name": player_name,
        "score": score,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
    }

    leaderboard.append(new_entry)
    leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)[:10]

    for idx, entry in enumerate(leaderboard, start=1):
        entry["rank"] = idx

    leaderboard_data[0]["leaderboard"] = leaderboard
    save_leaderboard(leaderboard_data)

@app.route('/leaderboard_data')
def leaderboard_data():
    """Serve the leaderboard JSON data."""
    try:
        with open(LEADERBOARD_FILE, 'r') as file:
            data = json.load(file)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/leaderboard')
def leaderboard_page():
    """Serve the leaderboard HTML page."""
    return render_template('leaderboard.html')

@app.route('/add_score', methods=['POST'])
def add_score():
    """Add a new score to the leaderboard."""
    data = request.json
    player_id = data.get("player_id")
    score = data.get("score")
    if player_id is None or score is None:
        return jsonify({"error": "Missing player_id or score"}), 400
    leaderboard = update_leaderboard(player_id, score)
    return jsonify(leaderboard)

@app.route('/')
def index():
    """Serve the index page."""
    return render_template('index.html')

@app.route('/spectator')
def spectator():
    """Serve the spectator page."""
    return render_template('spectator.html')

@app.route('/player/<int:player_id>')
def player(player_id):
    """Serve the player page."""
    player_name = request.args.get('name', f'Player{player_id}')
    player_states[player_id]["name"] = player_name  # Set the player's name in player_states
    return render_template('player.html', player_id=player_id, player_name=player_name)


@app.route('/reset_game', methods=['POST'])
def reset_game_route():
    """Reset the game and redirect to the index."""
    reset_game()
    return jsonify({"message": "Game reset successfully."})

@app.route('/winner')
def winner_page():
    """Serve the winner page."""
    return render_template('winner.html')

@app.route('/loser')
def loser_page():
    """Serve the loser page."""
    return render_template('loser.html')

@app.route('/random_video/<player_id>', methods=['POST'])
def random_video(player_id):
    """Serve a random video based on game rules."""
    try:
        player_id = int(player_id)
    except ValueError:
        return jsonify({"error": "Invalid player ID"}), 400
    
    if not game_state["game_running"]:
        return jsonify({"error": "Game has not started yet."}), 400

    # Initialize player state if not already present
    if player_id not in player_states:
        player_states[player_id] = {"swipe_count": 0, "normal_count": 0, "last_video": None}

    # Increment the swipe count
    player_states[player_id]["swipe_count"] += 1

    # Broadcast updated scores
    socketio.emit("update_scores", player_states)

    # Check for swipe type from the frontend
    swipe_type = request.json.get("swipe_type", "up")  # Default to "up" for regular swipes

    last_videos = player_states[player_id]["last_videos"]
    #bomb_videos_filt = [v for v in bomb_videos if v != last_video] if len(bomb_videos) > 1 else bomb_videos
    video = None
    video_type = None
    print(swipe_type)

    if swipe_type == "ad":
        open_valve(player_id)
        video_type = "ad"
    if swipe_type == "skip_ad":
        # Always play a normal video after skipping an ad
        video_type = "normal"
        close_valve(player_id)
        

    elif swipe_type == "normal":
        choice = random.random()
        if choice < 0.1:
            video_type = "ice"
        else:
            video_type = "normal"
            
    videos = video_cache.get(video_type, [])
    if not videos:
        return jsonify({"error": f"No videos available for type: {video_type}"}), 500
    print(videos)
    videos = [v for v in videos if v != last_videos] if len(videos) > 1 else videos
    
    video = random.choice(videos)
    last_videos.append(video)
    if len(last_videos) > 5:
        last_videos.pop(0)  # Keep only the last 5 videos

    player_states[player_id]["last_videos"] = last_videos
    print(video_type)
    print(video)

    socketio.emit("update_video", {
        "player_id": player_id,
        "video_url": f"/videos/{video_type}/{video}",
        "type": video_type
    }, room="spectators")

    return jsonify({"video_url": f"/videos/{video_type}/{video}", "type": video_type})

@app.route('/videos/<folder>/<path:filename>')
def serve_hls(folder, filename):
    """Serve HLS files (m3u8 and ts)."""
    folder_map = {
        "normal": NORMAL_VIDEOS_FOLDER,
        "ad": ADS_VIDEOS_FOLDER,
        "ice": ICE_VIDEOS_FOLDER,
    }
    if folder not in folder_map:
        return jsonify({"error": "Invalid folder"}), 404

    file_path = os.path.join(folder_map[folder], filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    if filename.endswith(".m3u8"):
        return Response(open(file_path).read(), mimetype="application/vnd.apple.mpegurl")
    elif filename.endswith(".ts") or filename.endswith(".m4s"):
        return send_file(file_path, mimetype="video/mp4")
    return jsonify({"error": "Invalid file type"}), 400

@app.route('/leave_game/<player_id>', methods=['POST'])
def leave_game(player_id):
    """Handle a player leaving the game."""
    try:
        player_id = int(player_id)
    except ValueError:
        return jsonify({"error": "Invalid player ID"}), 400

    # Determine the winner (the other player)
    winner_id = 2 if player_id == 1 else 1
    loser_id = 1 if player_id == 1 else 2
    winner_name = player_states[winner_id]["name"]
    loser_name = player_states[loser_id]["name"]
    game_state[f"player{1}_ready"] = False
    game_state[f"player{2}_ready"] = False

    with app.app_context():  # Ensure app context for URL generation
        # Notify both players and redirect the winner
        winner_score = player_states[winner_id]["swipe_count"]
        loser_score = player_states[loser_id]["swipe_count"]

        update_leaderboard(winner_name, winner_score)
        update_leaderboard(loser_name, loser_score)

        
        socketio.emit("game_over", {
            "winner": winner_id,
            "winner_redirect": f"{url_for('winner_page')}?score={winner_score}",
            "loser_redirect": f"{url_for('loser_page')}?score={loser_score}",
        })

    # Reset the game state
    reset_game()

    return jsonify({"message": f"Player {player_id} left the game. Player {winner_id} wins!"})


@socketio.on('join')
def on_join(data):
    """Handle player joining."""
    player_id = data.get("player_id")
    player_name = data.get("player_name")
    print(player_name)
    room = f"player_{player_id}"
    join_room(room)
    game_state[f"player{player_id}_ready"] = True
    print(f"Player {player_id} joined room {room}")

    # Start the game if both players are ready
    if (game_state["player1_ready"] == True and game_state["player2_ready"] == True) and not game_state["game_running"]:
        game_state["game_running"] = True
        print("Both players are ready. Starting the game.")
        socketio.emit("countdown_start", {"countdown": 3})  # Notify players to show countdown
        threading.Timer(3, start_game).start()  # Delay starting the game by 3 seconds

def start_game():
    """Start the game after the countdown."""
    game_state["game_running"] = True
    print("Game started.")
    socketio.emit("game_start")  # Notify players that the game has started
    threading.Thread(target=start_game_timer).start()

@socketio.on('join_spectator')
def on_join_spectator():
    """Handle a spectator joining."""
    join_room("spectators")
    print("A spectator joined the room.")

if __name__ == '__main__':
    try:
        socketio.run(app, debug=True, host='0.0.0.0')
    except Exception as e:
        close_serial()
    finally:
        close_serial()