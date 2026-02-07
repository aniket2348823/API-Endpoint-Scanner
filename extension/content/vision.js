// FILE: extension/content/vision.js
// IDENTITY: AGENT THETA (PRISM) - THE EYES
// MISSION: Passive DOM Analysis & Invisible Text Detection.

const PRISM_ENDPOINT = "http://localhost:8000/api/defense/analyze";

// 1. The Scanner Loop
const SCAN_INTERVAL = 1000; // 1s (Aggressive)

setInterval(() => {
    scanDOM();
}, SCAN_INTERVAL);

function scanDOM() {
    // 1.1 Snapshot Invisible Elements
    // We look for suspicious opacity, z-index, or font-size 0
    const allElements = document.querySelectorAll('*');

    allElements.forEach(el => {
        const style = window.getComputedStyle(el);
        const opacity = parseFloat(style.opacity);
        const zIndex = parseInt(style.zIndex);
        const fontSize = style.fontSize;

        let isSuspicious = false;

        if (opacity < 0.1 && el.innerText.length > 5) isSuspicious = true;
        if (zIndex < -1000 && el.innerText.length > 5) isSuspicious = true;
        if (fontSize === "0px" && el.innerText.length > 5) isSuspicious = true;

        // Prompt Injection Check (Client-Side Pre-Filter)
        const text = el.innerText.toLowerCase();
        if (text.includes("ignore previous instructions") || text.includes("system override")) {
            isSuspicious = true;
        }

        if (isSuspicious) {
            // Tag it so we don't resend constantly? (Optimization)
            if (el.dataset.prismScanned) return;
            el.dataset.prismScanned = "true";

            // 1.2 Send Snapshot to Backend (Prism Agent)
            sendSnapshot({
                agent_id: "THETA",
                url: window.location.href,
                content: {
                    style: {
                        opacity: opacity,
                        zIndex: zIndex,
                        fontSize: fontSize
                    },
                    innerText: el.innerText,
                    antigravity_id: generateId()
                }
            }, el);
        }
    });
}

function generateId() {
    return Math.random().toString(36).substr(2, 9);
}

// 2. Communication & Visualization
async function sendSnapshot(payload, element) {
    try {
        // Send to Background -> Backend? Or direct fetch?
        // Content scripts can fetch localhost if permissions allow.
        // Let's try direct fetch for speed, or message background if CORS issues.
        // Assuming localhost CORS is enabled on backend.

        const response = await fetch(PRISM_ENDPOINT, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const result = await response.json();
        // Server confirms "THREAT DETECTED"
        // Since backend broadcasts via socket to Dashboard, here we just get a "200 OK".
        // But if we want Visual Feedback (Red Box), we check response data.

        // Assuming backend returns analysis result in response payload?
        // Currently defense.py creates a JobPacket but doesn't return result directly (Async).
        // V6 Improvement: If we want immediate Red Box, backend defense.py should wait or we rely on socket?
        // For MVP: We just draw Red Box if we suspect it locally + confirm sent.

        // Wait, the prompt says "Extension: Draws a Red Box around the hidden text."
        // Let's draw it if we found it suspicious, assuming Prism agrees.
        drawVisualAlert(element);

    } catch (e) {
        console.error("Prism: Connection Error", e);
    }
}

function drawVisualAlert(element) {
    element.style.border = "4px solid #ff0055"; // Neon Red
    element.style.boxShadow = "0 0 15px #ff0055";
    element.setAttribute("title", "⚠️ PRISM: Hidden Content Detected");
}

// 3. HUD Toast Listener (For Chi)
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.type === "CHI_SHOW_TOAST") {
        showToast(msg.message, msg.color);
    }
});

function showToast(text, color) {
    const toast = document.createElement("div");
    toast.innerText = text;
    toast.style.position = "fixed";
    toast.style.top = "20px";
    toast.style.left = "50%";
    toast.style.transform = "translateX(-50%)";
    toast.style.background = "rgba(0,0,0,0.9)";
    toast.style.color = color || "#00fffa";
    toast.style.padding = "15px 30px";
    toast.style.borderRadius = "8px";
    toast.style.border = `1px solid ${color}`;
    toast.style.zIndex = 10000;
    toast.style.fontSize = "16px";
    toast.style.fontFamily = "monospace";
    document.body.appendChild(toast);

    setTimeout(() => toast.remove(), 4000);
}
