document.addEventListener("DOMContentLoaded", () => {
    const videoPlayer = document.getElementById("video-player");
    const errorMessage = document.getElementById("error-message");
    const timeLeftElement = document.getElementById("time-left");
    const skipAdButton = document.getElementById("skip-ad-button");
    const quitButton = document.getElementById("quit-button");
    const leaveGameButton = document.getElementById("leave-game");
    const player1Score = document.getElementById("player1-score");
    const player2Score = document.getElementById("player2-score");
    const winnerMessage = document.getElementById("winner-message");
    const winnerLoserContainer = document.getElementById("winner-loser-container");
    const iceContainer = document.getElementById("ice-container"); // Container for the ice elements
    const iceMessage = document.getElementById("ice-message");     // Text for the ice warning
    const iceDrinkButton = document.getElementById("ice-drink-button"); // Button to confirm drinking
    const countdownTimer = document.getElementById("countdown-timer");
    const countdownNumber = document.getElementById("countdown-number");

    const playerName = new URLSearchParams(window.location.search).get('name');
    const playerInfo = document.getElementById("player-info");

    const playerId = parseInt(window.location.pathname.split("/").pop());
    const socket = io();

    console.log("hey")
    let skipAdCountdown = null; // Interval for countdown timer
    let timeLeft = 5; // Default countdown time
    let gameTimeLeft = 60; // Initial game time (in seconds)
    let timerInterval = null;
    let gameRunning = false;
    let nextVideoUrl = null; // Store the URL of the next video
    let nextVideoType = null; // Store the URL of the next video
    let swipesDone = 0;
    let isLoading = false; // Prevent concurrent video loading
    let videoReady = true; // Prevent swiping before video is ready

    
    videoPlayer.preload = "auto"; // Preload as much as possible
    videoPlayer.autoplay = true;  // Ensure videos autoplay

    // Join the player's room
    socket.emit("join", { player_id: playerId , player_name: playerName});

    function startGameTimer() {
        timerInterval = setInterval(() => {
            gameTimeLeft--;
            timeLeftElement.textContent = gameTimeLeft;

            if (gameTimeLeft <= 0) {
                clearInterval(timerInterval); // Stop the timer when time is up
            }
        }, 1000);
    }

    // Handle game start event
    socket.on("game_start", () => {
        console.log("Game started!");
        startGameTimer(); // Start the timer when the game begins
        gameRunning = true;
    });

    socket.on("countdown_start", (data) => {
        let countdown = data.countdown;
        countdownTimer.style.display = "block"; // Show the countdown timer
        countdownNumber.textContent = countdown;
    
        const interval = setInterval(() => {
            countdown -= 1;
            countdownNumber.textContent = countdown;
    
            if (countdown <= 0) {
                clearInterval(interval);
                countdownTimer.style.display = "none"; // Hide the countdown timer
            }
        }, 1000);
    });

    function updateSkipAdButton() {
        skipAdButton.textContent = `Skip Ad in ${timeLeft}s`;
        skipAdButton.style.opacity = 0.5; // Make button appear inactive
        skipAdButton.style.cursor = "not-allowed"; // Indicate non-clickable
        skipAdButton.disabled = true; // Prevent clicks
    }

    function startSkipAdCountdown() {
        skipAdButton.style.display = "block"; // Make the button visible
        updateSkipAdButton();
    
        console.log("Starting countdown:", timeLeft);
    
        skipAdCountdown = setInterval(() => {
            timeLeft--;
            console.log("Countdown:", timeLeft); // Debug log for countdown
    
            if (timeLeft > 0) {
                updateSkipAdButton();
            } else {
                clearInterval(skipAdCountdown);
                skipAdButton.textContent = "Skip Ad";
                skipAdButton.style.opacity = 1; // Restore button appearance
                skipAdButton.style.cursor = "pointer"; // Make clickable
                skipAdButton.disabled = false; // Enable the button
                console.log("Countdown ended. Button is now clickable.");
            }
        }, 1000);
    }
    

    // Update swipe scores
    socket.on("update_scores", (scores) => {
        player1Score.textContent = `Player 1: ${scores[1].swipe_count}`;
        player2Score.textContent = `Player 2: ${scores[2].swipe_count}`;
        // Highlight current player's score
        if (playerId === 1) {
            player1Score.style.fontWeight = "bold";
            player2Score.style.fontWeight = "normal";
        } else {
            player2Score.style.fontWeight = "bold";
            player1Score.style.fontWeight = "normal";
        }
    });

    // Handle game over
    socket.on("game_over", (data) => {
        clearInterval(timerInterval); // Stop the timer
        const isWinner = playerId === data.winner;

        // Redirect to the winner or loser page
        const redirectUrl = isWinner ? data.winner_redirect : data.loser_redirect;
        console.log(redirectUrl)
        gameRunning = false;
        window.location.href = redirectUrl;
    });

    // Handle leaving the game
    leaveGameButton.addEventListener("click", async () => {
        console.log("Player is leaving the game.");
        const otherPlayerId = playerId === 1 ? 2 : 1;
        try {
            const response = await fetch(`/leave_game/${playerId}`, { method: "POST" });
            const data = await response.json();
            console.log(data.message);
            socket.emit("game_over", { winner: otherPlayerId });
            gameRunning = false;
            window.location.href = "/";
        } catch (error) {
            console.error("Error leaving the game:", error);
        }
    });

    // Function to show the "Skip Ad" button in a random position
    function showSkipAdButton() {
        const randomTop = Math.random() * 80 + 10; // Between 10% and 90% of the viewport height
        const randomLeft = Math.random() * 80 + 10; // Between 10% and 90% of the viewport width
        skipAdButton.style.top = `${randomTop}%`;
        skipAdButton.style.left = `${randomLeft}%`;
        skipAdButton.style.display = "block";
    }

    // Handle play_ad event
    socket.on("play_ad", (data) => {
        currentVideoType = "ad";
        videoPlayer.src = data.video_url;
        videoPlayer.load();
        videoPlayer.loop = true; // Set the video to loop continuously
        videoPlayer.play().catch((error) => {
            console.error("Error playing ad video:", error);
        });

        // Reset timer to 5 seconds for the new ad
        timeLeft = 5;
        startSkipAdCountdown();
    });

    iceDrinkButton.addEventListener("click", async () => {
        console.log("Player clicked 'I drank'. Resuming video."); // Debug log
        iceContainer.style.display = "none"; // Hide the ice container
        iceDrinkButton.disabled = true; // Disable the button
        isSwiping = false; // Allow swiping again after handling ice
    
        try {
            await loadVideo("normal"); // Load the next video
            console.log("Next video loaded successfully after 'I drank'.");
        } catch (error) {
            console.error("Error loading next video after 'I drank':", error);
        }
    });

    skipAdButton.addEventListener("click", async () => {
        if (!skipAdButton.disabled) {
            console.log("Skipping ad.");
            skipAdButton.style.display = "none";
            clearInterval(skipAdCountdown); // Ensure no residual intervals
            await loadVideo("skip_ad"); // Transition to a normal video after skipping ad
        }
    });

    let touchStartY = 0;
    let isSwiping = false;
    let currentVideoType = "normal";


    async function preloadVideo() {
        try {
            const response = await fetch(`/random_video/${playerId}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ swipe_type: "normal" }), // Default to normal swipe for preloading
            });

            const data = await response.json();
            if (data.error) {
                throw new Error(data.error);
            }

            nextVideoUrl = data.video_url; // Save the preloaded video URL
            nextVideoType = data.type;
        } catch (error) {
            console.error("Error preloading video:", error);
        }
    }
    async function loadVideo(swipeType = "normal") {
        if (isLoading) {
            console.log("Video is already loading. Ignoring additional requests.");
            return; // Prevent loading a new video while one is already in progress
        }
    
        try {
            isLoading = true; // Set loading state
            videoReady = false; // Block interactions until video is ready
            // If no preloaded video or swipe type is not normal, fetch a new video
            console.log("Fetching a new video...");
            const response = await fetch(`/random_video/${playerId}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ swipe_type: swipeType }),
            });

            const data = await response.json();
            if (data.error) {
                throw new Error(data.error);
            }

            videoUrl = data.video_url;
            currentVideoType = data.type;


            
    
            if (Hls.isSupported()) {
                const hls = new Hls();
                hls.loadSource(videoUrl);
                hls.attachMedia(videoPlayer);
                hls.on(Hls.Events.MANIFEST_PARSED, () => {
                    videoPlayer.play().then(() => {
                        videoReady = true; // Allow interactions once video starts playing
                    }).catch((error) => {
                        console.error("Error playing video:", error);
                    });
                });
            } else if (videoPlayer.canPlayType('application/vnd.apple.mpegurl')) {
                videoPlayer.src = videoUrl;
                videoPlayer.play().then(() => {
                    videoReady = true; // Allow interactions once video starts playing
                }).catch((error) => {
                    console.error("Error playing video:", error);
                });
            } else {
                throw new Error("HLS is not supported in this browser.");
            }
    
    
            if (currentVideoType === "ad") {
                console.log("Ad video loaded. Starting Skip Ad countdown.");
                timeLeft = 5; // Reset the timer
                startSkipAdCountdown(); // Start the countdown for the Skip Ad button
            } else {
                skipAdButton.style.display = "none"; // Hide the Skip Ad button for non-ad videos
                iceContainer.style.display = "none";
            }

        } catch (error) {
            console.error("Error loading video:", error);
            errorMessage.style.display = "block";
            errorMessage.textContent = error.message;
        } finally {
            //videoReady = true
            isLoading = false; // Reset loading state
        }
    }
    
    videoPlayer.addEventListener("ended", () => {
        if (gameRunning) {
            videoPlayer.currentTime = 0;
            videoPlayer.play().catch((error) => {
                console.error("Error replaying video:", error);
            });
        }
    });
    

    videoPlayer.addEventListener("touchstart", (e) => {
        touchStartY = e.touches[0].clientY;
    });

    videoPlayer.addEventListener("touchend", async (e) => {
        console.log(videoReady)
        if (!gameRunning || !videoReady) return;
        const touchEndY = e.changedTouches[0].clientY;
        const swipeThreshold = 50;

        if (currentVideoType === "ad") {
            if (timeLeft == 0) return;
            // Prevent interactions during ad playback
            console.log("Swiped up on an ad video. Adding 1 second to the timer.");
            timeLeft += 1; // Add 1 second to the timer
            updateSkipAdButton(); // Update the button text
            return;
        }

        if (touchStartY - touchEndY > swipeThreshold && !isSwiping) {
            // Swipe up: Load the next video (normal behavior)
            isSwiping = true;
            if (currentVideoType === "ice") {
                console.log("Ice video detected. Showing ad.");
                await loadVideo("ad");
            }
            else {
                await loadVideo("normal"); // Normal video
                swipesDone += 1
            }
            console.log(swipesDone);
            isSwiping = false;
        }
        else if (touchEndY - touchStartY > swipeThreshold && !isSwiping) {
            // Swipe down: Skip the ice video without showing the message
            isSwiping = true;
            if (currentVideoType === "ice") {
                console.log("Swiping down on an ice video. Skipping to next video.");
                await loadVideo("normal"); // Load a new normal video
            }
            isSwiping = false;
        }
    });

    quitButton.addEventListener("click", async () => {
        console.log("Quitting game.");
        await fetch("/reset_game", { method: "POST" });
        window.location.href = "/";
    });

    loadVideo("normal"); // Load the initial video
});
