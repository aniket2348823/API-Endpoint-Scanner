from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from backend.api.endpoints import recon, attack, reports
from backend.api.socket_manager import manager

app = FastAPI(title="Antigravity")

# CORS to allow Chrome Extension and Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(recon.router, prefix="/api/recon", tags=["Recon"])
app.include_router(attack.router, prefix="/api/attack", tags=["Attack"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
from backend.api.endpoints import dashboard
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])

@app.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket, client_type: str = "ui"):
    await manager.connect(websocket, client_type)
    try:
        while True:
            # Keep alive / listen for client commands
            await websocket.receive_text()
            # If Spy sends heartbeat or data via WS, handle here
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # If Spy disconnected, we need to notify UIs.
        # Can't await inside sync disconnect, so we do it here manually if it was a spy
        if client_type == "spy":
            await manager.broadcast_to_ui({
                "type": "SPY_STATUS",
                "payload": {"connected": False}
            })

if __name__ == "__main__":
    import uvicorn
    # Use uvloop for performance if available (handles async much faster)

        
    uvicorn.run(app, host="127.0.0.1", port=8000)
