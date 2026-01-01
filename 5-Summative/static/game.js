document.addEventListener("DOMContentLoaded", function () {
    setupTimer();
    setupStereo();
    setupPoster();
});

function setupTimer() {
    const timerEl = document.getElementById("timer");
    if (!timerEl) return;

    const limit = parseInt(timerEl.dataset.limit || "0");

    const started = timerEl.dataset.gameStarted === "yes";

    if (!started) {
        timerEl.textContent = "Time left: --";
        return;
    }

    function updateTimer() {
        fetch("/time_status")
            .then((res) => res.json())
            .then((data) => {
                const remaining = data.remaining;
                timerEl.textContent = "Time left: " + formatTime(remaining);

                if (remaining <= 0) {
                    window.location.href = "/game_over";
                }
            })
            .catch((err) => {
                console.log("timer error", err);
            });
    }

    updateTimer();
    setInterval(updateTimer, 1000);
}

function formatTime(seconds) {
    const s = Math.max(0, seconds);
    const mins = Math.floor(s / 60);
    const secs = s % 60;
    return mins + ":" + (secs < 10 ? "0" + secs : secs);
}

function setupStereo() {
    const btn = document.getElementById("stereo-btn");
    const text = document.getElementById("stereo-text");

    if (!btn || !text) return;

    btn.addEventListener("click", function () {
        text.textContent =
            "You press play. A chiptune beat starts blasting. " +
            "The tiny display on the stereo says: 'NOW PLAYING: RETRO MODE'.";
    });
}

function setupPoster() {
    const poster = document.getElementById("poster");
    const posterText = document.getElementById("poster-text");

    if (!poster || !posterText) return;

    let clicks = 0;

    poster.addEventListener("click", function () {
        clicks += 1;

        if (clicks < 5) {
            posterText.textContent =
                "The cat's eyes seem to follow you. (Clicks: " + clicks + ")";
        } else if (clicks < 10) {
            posterText.textContent =
                "Something shiny appears under the poster... keep tapping. (Clicks: " + clicks + ")";
        } else {
            posterText.textContent =
                "The poster rips slightly and you see numbers written on the wall: 4 5 3 1.";
        }
    });
}
