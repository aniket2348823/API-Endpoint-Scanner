importScripts('socket.io.min.js');

const socket = io('http://localhost:5000');
let attachedTabs = new Set();

socket.on('connect', () => {
    console.log('[LEECH] Connected to Antigravity Backend');
});

// Attach debugger to tabs as they are updated/activated
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url && !tab.url.startsWith('chrome://')) {
        attachDebugger(tabId);
    }
});

function attachDebugger(tabId) {
    if (attachedTabs.has(tabId)) return;

    chrome.debugger.attach({ tabId: tabId }, "1.3", () => {
        if (chrome.runtime.lastError) {
            console.log(`[LEECH] Attach failed: ${chrome.runtime.lastError.message}`);
            return;
        }
        attachedTabs.add(tabId);
        chrome.debugger.sendCommand({ tabId: tabId }, "Network.enable");
        console.log(`[LEECH] Attached to tab ${tabId}`);
    });
}

chrome.debugger.onDetach.addListener((source, reason) => {
    attachedTabs.delete(source.tabId);
    console.log(`[LEECH] Detached from tab ${source.tabId}`);
});

chrome.debugger.onEvent.addListener(async (source, method, params) => {
    if (method === "Network.requestWillBeSent") {
        // Capture Request
        const payload = {
            type: 'REQUEST',
            requestId: params.requestId,
            url: params.request.url,
            method: params.request.method,
            headers: params.request.headers,
            postData: params.request.postData,
            timestamp: Date.now()
        };
        socket.emit('traffic_log', payload);
    }

    if (method === "Network.responseReceived") {
        // Capture Response Metadata
        // We need to fetch the body separately using getResponseBody
        const requestId = params.requestId;
        const url = params.response.url;
        const type = params.type; // XHR, Fetch, etc.

        if (type === 'XHR' || type === 'Fetch') {
            chrome.debugger.sendCommand({ tabId: source.tabId }, "Network.getResponseBody", { requestId }, (response) => {
                if (chrome.runtime.lastError) {
                    // Body might not be available (redirects, etc)
                    return;
                }

                let body = response.body;
                if (response.base64Encoded) {
                    // Keep it base64 or decode if needed. Backend can handle it.
                }

                const payload = {
                    type: 'RESPONSE',
                    requestId: requestId,
                    url: url,
                    status: params.response.status,
                    headers: params.response.headers,
                    body: body,
                    timestamp: Date.now()
                };
                socket.emit('traffic_log', payload);
            });
        }
    }
});
