// content.js
const s = document.createElement('script');
s.src = chrome.runtime.getURL('ghost.js');
s.onload = function () {
    this.remove(); // Clean up the tag, logic remains in memory
};
(document.head || document.documentElement).appendChild(s);

// Listen for messages from the injected 'ghost.js'
window.addEventListener("message", (event) => {
    // Only accept messages from ourselves
    if (event.source !== window || !event.data.type || event.data.type !== "ANTIGRAVITY_CAPTURE") {
        return;
    }

    // Forward to background.js
    chrome.runtime.sendMessage({
        type: "TRAFFIC_LOG",
        payload: event.data.payload
    });
});
