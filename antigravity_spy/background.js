// background.js
let socket = null;
const BACKEND_URL = "ws://localhost:5000/stream";

function connect() {
    socket = new WebSocket(BACKEND_URL);

    socket.onopen = () => {
        console.log("%c[AG] LINK ESTABLISHED", "color: #06b6d4");
        // Keep alive
        setInterval(() => socket.send(JSON.stringify({ type: "ping" })), 25000);
    };

    socket.onclose = () => {
        console.log("[AG] LINK LOST. Retrying...");
        setTimeout(connect, 2000);
    };

    socket.onerror = (err) => console.error("[AG] SOCKET ERROR:", err);
}

// Connect immediately
connect();

// Listen for traffic from content.js and forward to Python
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === "TRAFFIC_LOG") {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify(message.payload));
        }
    }
});
