// Antigravity Spy V2 - Background Service Worker
// Modules: Synapse (Key Capture) + Traffic Interception + Aegis (Active Defense)
importScripts('background/active_defense.js');

// ============================================================================
// CONFIGURATION
// ============================================================================

const BACKEND_URL = "http://127.0.0.1:8000";
const WS_ENDPOINT = "ws://127.0.0.1:8000/stream?client_type=spy";

// Filter out static assets
const IGNORE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.css', '.js', '.woff', '.woff2', '.ttf', '.svg', '.ico'];
const IGNORE_METHODS = ['OPTIONS', 'HEAD'];

// Synapse: Headers to capture
const SENSITIVE_HEADERS = [
    'authorization',
    'cookie',
    'x-api-key',
    'x-auth-token',
    'x-csrf-token',
    'x-access-token',
    'x-session-id',
    'bearer'
];

// ============================================================================
// SYNAPSE MODULE - Auto Key Theft
// ============================================================================

function extractSensitiveHeaders(requestHeaders) {
    const captured = {};
    for (const h of requestHeaders) {
        const headerName = h.name.toLowerCase();
        if (SENSITIVE_HEADERS.includes(headerName)) {
            captured[h.name] = h.value;
        }
        // Also capture Bearer tokens in any header
        if (h.value && h.value.toLowerCase().startsWith('bearer ')) {
            captured[h.name] = h.value;
        }
    }
    return captured;
}

async function sendCapturedKeys(url, keys) {
    if (Object.keys(keys).length === 0) return;

    try {
        await fetch(`${BACKEND_URL}/api/recon/keys`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url: url,
                keys: keys,
                timestamp: Date.now() / 1000
            })
        });

        // Show badge notification
        chrome.action.setBadgeText({ text: '🔑' });
        chrome.action.setBadgeBackgroundColor({ color: '#8A2BE2' });

        // Clear badge after 3 seconds
        setTimeout(() => chrome.action.setBadgeText({ text: '' }), 3000);

        console.log("[SYNAPSE] Keys captured from:", url);
    } catch (err) {
        console.error("[SYNAPSE] Failed to send keys:", err);
    }
}

// ============================================================================
// SCANNER ENGINE RELAY
// ============================================================================

async function sendScanResults(results) {
    if (!results || !results.findings || results.findings.length === 0) return;

    try {
        await fetch(`${BACKEND_URL}/api/recon/ingest`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url: results.meta.url,
                method: "SCAN",
                headers: { "x-scanner": "v12-engine" },
                timestamp: results.meta.timestamp / 1000,
                payload: results // Send full structure
            })
        });
        console.log("[SPY V2] Scanner Engine results relayed.");
    } catch (err) {
        console.error("[SPY V2] Failed to relay scan results:", err);
    }
}

// Listen for messages from Content Scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'SCAN_RESULTS') {
        console.log("[SPY V2] Received Scan Results from Tab:", sender.tab.id);
        sendScanResults(message.payload);
    }

    // 2. DEFENSE SHIELD (Agent Prism & Chi)
    if (message.type === "ANALYZE_THREAT") {
        console.log("[BACKGROUND] Relaying threat to Hive:", message.payload);

        // 1. Send Data to Python Backend
        fetch("http://127.0.0.1:8000/api/defense/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(message.payload)
        })
            .then(res => res.json())
            .then(response => {
                console.log("[BACKGROUND] Hive Verdict:", response);
                if (response.verdict === "BLOCK") {
                    // 2. If Backend says BLOCK, notify the user
                    chrome.scripting.executeScript({
                        target: { tabId: sender.tab.id },
                        func: showBlockNotification,
                        args: [response.reason]
                    });
                }
            })
            .catch(err => console.error("Hive Disconnected:", err));

        return true;
    }
});


// ============================================================================
// TRAFFIC INTERCEPTION
// ============================================================================

function shouldCapture(details) {
    if (IGNORE_METHODS.includes(details.method)) return false;

    try {
        const url = new URL(details.url);
        const path = url.pathname.toLowerCase();

        // Ignore static assets
        for (const ext of IGNORE_EXTENSIONS) {
            if (path.endsWith(ext)) return false;
        }

        // Ignore our own backend traffic
        if (url.origin.includes("127.0.0.1:8000") || url.origin.includes("localhost:8000")) {
            return false;
        }

        return true;
    } catch (e) {
        return false;
    }
}

// ============================================================================
// WEBSOCKET CONNECTION
// ============================================================================

let socket = null;

function connectWebSocket() {
    socket = new WebSocket(WS_ENDPOINT);

    socket.onopen = () => {
        console.log("[SPY V2] Connected to Backend Stream");
    };

    socket.onclose = () => {
        console.log("[SPY V2] Disconnected. Retrying in 2s...");
        setTimeout(connectWebSocket, 2000);
    };

    socket.onerror = (err) => {
        console.error("[SPY V2] WebSocket Error:", err);
        socket.close();
    };

    socket.onmessage = (event) => {
        // Handle commands from backend if needed
        console.log("[SPY V2] Message:", event.data);
    };
}

// Start WebSocket
connectWebSocket();

// ============================================================================
// REQUEST LISTENER
// ============================================================================

chrome.webRequest.onBeforeSendHeaders.addListener(
    function (details) {
        if (!shouldCapture(details)) return;

        // Extract headers
        const headers = {};
        const capturedKeys = {};

        if (details.requestHeaders) {
            for (const h of details.requestHeaders) {
                headers[h.name] = h.value;

                // Synapse: Check for sensitive headers
                if (SENSITIVE_HEADERS.includes(h.name.toLowerCase())) {
                    capturedKeys[h.name] = h.value;
                }
            }
        }

        // Send recon packet
        const packet = {
            url: details.url,
            method: details.method,
            headers: headers,
            timestamp: Date.now() / 1000
        };

        fetch(`${BACKEND_URL}/api/recon/ingest`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(packet)
        }).catch(err => console.log("[SPY V2] Relay failed:", err));

        // Synapse: Send captured keys
        sendCapturedKeys(details.url, capturedKeys);
    },
    { urls: ["<all_urls>"] },
    ["requestHeaders", "extraHeaders"]
);

function showBlockNotification(reason) {
    // Inject a Toast Notification into the page
    const toast = document.createElement("div");
    toast.innerText = `🛡️ ANTIGRAVITY BLOCKED THREAT: ${reason}`;
    toast.style = "position:fixed; top:20px; right:20px; background:#ef4444; color:white; padding:15px; z-index:999999; border-radius:5px; font-family:monospace; box-shadow: 0 10px 30px rgba(0,0,0,0.5); font-weight: bold; border: 1px solid #b91c1c;";
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 5000);
}

console.log("[SPY V2] Antigravity Spy V2 Initialized");
