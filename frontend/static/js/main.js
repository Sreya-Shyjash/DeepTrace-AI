/* frontend/static/js/main.js */
const clockEl = document.getElementById('clock');
if (clockEl) { setInterval(() => { clockEl.innerText = new Date().toLocaleTimeString(); }, 1000); }

const dot = document.querySelector(".cursor-dot");
const outline = document.querySelector(".cursor-outline");

window.addEventListener("mousemove", (e) => {
    dot.style.left = `${e.clientX}px`;
    dot.style.top = `${e.clientY}px`;
    outline.style.left = `${e.clientX}px`;
    outline.style.top = `${e.clientY}px`;
});

window.addEventListener("mousedown", () => {
    outline.style.transform = "translate(-50%, -50%) scale(0.7)";
    dot.style.transform = "translate(-50%, -50%) scale(1.5)";
});

window.addEventListener("mouseup", () => {
    outline.style.transform = "translate(-50%, -50%) scale(1)";
    dot.style.transform = "translate(-50%, -50%) scale(1)";
});

function addLog(msg) {
    const logs = document.getElementById('logs');
    if (logs) {
        logs.innerHTML += `<br><span style="color: #666;">[${new Date().toLocaleTimeString()}]</span> ${msg}`;
        logs.scrollTop = logs.scrollHeight;
    }
}