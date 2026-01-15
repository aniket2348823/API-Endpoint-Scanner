// Antigravity // Logic-Assessment-Engine v2.0
// Browser Interceptor Snippet (Ghost-in-the-Browser)
// Paste this into the Chrome Developer Tools Console of the target website.

(function () {
    const BACKEND_WS = "ws://localhost:5000"; // SocketIO default namespace

    // We use socket.io-client logic if available, or raw WebSocket if not.
    // However, since app.py uses Flask-SocketIO, raw WebSocket connection requires specific handshake.
    // For the "Snipppet" approach to be standalone without importing socket.io-client library, 
    // we should use the engine.io protocol or just standard WebSocket if the backend supports it.
    // Flask-SocketIO wraps Engine.IO.

    // SIMPLIFIED HACKATHON VERSION:
    // We will assume the user can load this script. 
    // Since we can't easily inject the full socket.io-client lib in a console snippet,
    // we will strictly use the standard `fetch` to POST the logs for the MVP "Ghost" mode if WS fails,
    // OR we can try a raw WebSocket connection to the engine.io endpoint.

    // Let's stick to the prompt's requested WebSocket implementation but acknowledge the protocol nuance.
    // A raw WebSocket connection to Flask-SocketIO needs: ws://localhost:5000/socket.io/?EIO=4&transport=websocket

    const wsUrl = "ws://localhost:5000/socket.io/?EIO=4&transport=websocket";
    const socket = new WebSocket(wsUrl);

    socket.onopen = function () {
        console.log("%c [ANTIGRAVITY] UPLINK ESTABLISHED ", "color: #06b6d4; font-weight: bold; background: #000;");
        // Handshake for Engine.IO might be needed, but usually it connects.
        // Send a probe
        socket.send('2probe');
    };

    socket.onmessage = function (event) {
        // Heartbeat
        if (event.data === '3probe') {
            socket.send('2'); // Ping
        }
    };

    const logToAntigravity = (data) => {
        if (socket.readyState === WebSocket.OPEN) {
            // Socket.IO message format: 42["message", data]
            const payload = `42["message", ${JSON.stringify({
                source: window.location.href,
                timestamp: new Date().toISOString(),
                ...data
            })}]`;
            socket.send(payload);
        } else {
            console.warn("[ANTIGRAVITY] Link unstable. Dropped packet.");
        }
    };

    // 1. Hooking FETCH
    const originalFetch = window.fetch;
    window.fetch = async (...args) => {
        const [resource, config] = args;
        const url = typeof resource === 'string' ? resource : resource.url;
        const method = config?.method || 'GET';

        logToAntigravity({ type: 'FETCH', method, url, body: config?.body });
        return originalFetch(...args);
    };

    // 2. Hooking XHR (The "Legacy" Logic)
    const originalOpen = XMLHttpRequest.prototype.open;
    const originalSend = XMLHttpRequest.prototype.send;

    XMLHttpRequest.prototype.open = function (method, url) {
        this._antigravity_data = { method, url };
        return originalOpen.apply(this, arguments);
    };

    XMLHttpRequest.prototype.send = function (body) {
        if (this._antigravity_data) {
            logToAntigravity({
                type: 'XHR',
                method: this._antigravity_data.method,
                url: this._antigravity_data.url,
                body
            });
        }
        return originalSend.apply(this, arguments);
    };

    console.log("%c [ANTIGRAVITY] GHOST-HOOK INJECTED ", "color: #06b6d4; font-weight: bold; background: #000;");
})();
