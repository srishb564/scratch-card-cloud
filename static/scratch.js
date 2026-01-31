const canvas = document.getElementById("scratchCanvas");
if (!canvas) {
    // Card already scratched → nothing to do
    console.log("Scratch canvas not present (already scratched)");
} else {
    const ctx = canvas.getContext("2d");

    // Cover layer
    ctx.fillStyle = "#bdbdbd";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Set scratch mode
    ctx.globalCompositeOperation = "destination-out";

    let isScratching = false;
    let revealed = false;

    const radius = 16;
    const revealThreshold = 0.3; // 30%

    // -------------------------------
    // GET SCRATCH POSITION
    // -------------------------------
    function getPosition(e) {
        const rect = canvas.getBoundingClientRect();

        if (e.touches && e.touches.length > 0) {
            return {
                x: e.touches[0].clientX - rect.left,
                y: e.touches[0].clientY - rect.top
            };
        }

        return {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
    }

    // -------------------------------
    // SCRATCH DRAW
    // -------------------------------
    function scratch(e) {
        if (!isScratching || revealed) return;

        e.preventDefault();

        const pos = getPosition(e);

        ctx.beginPath();
        ctx.arc(pos.x, pos.y, radius, 0, Math.PI * 2);
        ctx.fill();

        checkReveal();
    }

    // -------------------------------
    // CHECK SCRATCH PERCENTAGE
    // -------------------------------
    function checkReveal() {
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const pixels = imageData.data;

        let transparentPixels = 0;

        for (let i = 3; i < pixels.length; i += 4) {
            if (pixels[i] === 0) transparentPixels++;
        }

        const scratchedRatio = transparentPixels / (canvas.width * canvas.height);

        if (scratchedRatio >= revealThreshold) {
            revealReward();
        }
    }

    // -------------------------------
    // REVEAL + BACKEND UPDATE
    // -------------------------------
    function revealReward() {
        if (revealed) return;
        revealed = true;

        canvas.style.display = "none";
        document.getElementById("reward").style.display = "block";

        fetch(`/mark_scratched/${CARD_ID}`, {
            method: "POST"
        })
        .then(res => res.json())
        .then(data => {
            console.log("Scratch DB update:", data);
        })
        .catch(err => {
            console.error("Failed to update scratch status:", err);
        });
    }

    // -------------------------------
    // EVENT LISTENERS
    // -------------------------------
    canvas.addEventListener("mousedown", () => isScratching = true);
    canvas.addEventListener("mouseup", () => isScratching = false);
    canvas.addEventListener("mouseleave", () => isScratching = false);
    canvas.addEventListener("mousemove", scratch);

    canvas.addEventListener("touchstart", () => isScratching = true);
    canvas.addEventListener("touchend", () => isScratching = false);
    canvas.addEventListener("touchcancel", () => isScratching = false);
    canvas.addEventListener("touchmove", scratch);
}
