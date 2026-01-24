const canvas = document.getElementById("scratchCanvas");
const ctx = canvas.getContext("2d");

canvas.width = 300;
canvas.height = 200;

ctx.fillStyle = "#A0A0A0";
ctx.fillRect(0, 0, canvas.width, canvas.height);

let scratching = false;
let revealed = false;

function getPosition(e) {
    const rect = canvas.getBoundingClientRect();
    if (e.touches) {
        return {
            x: e.touches[0].clientX - rect.left,
            y: e.touches[0].clientY - rect.top
        };
    } else {
        return {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
    }
}

function scratch(e) {
    if (!scratching || revealed) return;
    e.preventDefault();

    const pos = getPosition(e);

    ctx.globalCompositeOperation = "destination-out";
    ctx.beginPath();
    ctx.arc(pos.x, pos.y, 18, 0, Math.PI * 2);
    ctx.fill();

    checkScratchPercentage();
}

function checkScratchPercentage() {
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    let cleared = 0;

    for (let i = 3; i < imageData.data.length; i += 4) {
        if (imageData.data[i] === 0) cleared++;
    }

    const percent = (cleared / (canvas.width * canvas.height)) * 100;

    if (percent >= 60) reveal();
}

function reveal() {
    revealed = true;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    fetch("/mark_scratched", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ card_id: CARD_ID })
    });
}

/* Mouse Events */
canvas.addEventListener("mousedown", () => scratching = true);
canvas.addEventListener("mouseup", () => scratching = false);
canvas.addEventListener("mousemove", scratch);

/* Touch Events */
canvas.addEventListener("touchstart", () => scratching = true);
canvas.addEventListener("touchend", () => scratching = false);
canvas.addEventListener("touchmove", scratch);
