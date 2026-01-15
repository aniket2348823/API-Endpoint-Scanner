// ghost.js
(function () {
    console.log("%c ANTIGRAVITY // INJECTED ", "background: #000; color: #06b6d4; font-weight: bold;");

    const XHR = XMLHttpRequest.prototype;
    const originalOpen = XHR.open;
    const originalSend = XHR.send;
    const originalFetch = window.fetch;

    // Helper to send data out to content.js
    const transmit = (data) => {
        // Filter: Ignore boring static assets
        if (data.url.match(/\.(css|png|jpg|svg|js)$/)) return;

        window.postMessage({
            type: "ANTIGRAVITY_CAPTURE",
            payload: {
                timestamp: Date.now(),
                ...data
            }
        }, "*");
    };

    // --- HOOK 1: FETCH API ---
    window.fetch = async (...args) => {
        const [resource, config] = args;
        const url = (typeof resource === 'string') ? resource : resource.url;
        const method = (config && config.method) ? config.method : 'GET';

        // Perform the actual request
        const response = await originalFetch(...args);

        // CLONE the response so we can read it without breaking the app
        const clone = response.clone();

        clone.json().then(body => {
            transmit({
                type: "FETCH",
                method: method,
                url: url,
                request_body: config ? config.body : null,
                response_body: body,
                status: response.status
            });
        }).catch(err => {
            // Response wasn't JSON, ignore
        });

        return response;
    };

    // --- HOOK 2: XHR (Legacy) ---
    XHR.open = function (method, url) {
        this._ag_method = method;
        this._ag_url = url;
        return originalOpen.apply(this, arguments);
    };

    XHR.send = function (body) {
        this.addEventListener('load', function () {
            // Try to parse JSON response
            try {
                const responseBody = JSON.parse(this.responseText);
                transmit({
                    type: "XHR",
                    method: this._ag_method,
                    url: this._ag_url,
                    request_body: body,
                    response_body: responseBody,
                    status: this.status
                });
            } catch (e) {
                // Not JSON, ignore
            }
        });
        return originalSend.apply(this, arguments);
    };

})();
