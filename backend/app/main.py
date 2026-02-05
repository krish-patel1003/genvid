import json
from fastapi import FastAPI, Request, Depends, WebSocket, WebSocketDisconnect, Body, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException

from app.core.config import settings
from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.videos.router import router as videos_router
from app.feed.router import router as feed_router
from app.core.dependencies import create_db_and_tables

app = FastAPI()

# Add SessionMiddleware to enable session support
# Generate a random secret key for session encryption
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

templates = Jinja2Templates(directory="templates")

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(videos_router)
app.include_router(feed_router)

class WebsocketBroadcaster:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self._connections.discard(websocket)

    async def broadcast(self, message: str) -> None:
        if not self._connections:
            return
        stale: list[WebSocket] = []
        for ws in self._connections:
            try:
                await ws.send_text(message)
            except Exception:
                stale.append(ws)
        for ws in stale:
            self._connections.discard(ws)

broadcaster = WebsocketBroadcaster()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    google_auth_url = request.url_for("google_login")
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "google_auth_url": google_auth_url}
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await broadcaster.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        broadcaster.disconnect(websocket)
    except Exception:
        broadcaster.disconnect(websocket)


@app.post("/ws/notify")
async def websocket_notify(payload: dict = Body(...)):
    try:
        message = json.dumps(payload)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid payload")
    await broadcaster.broadcast(message)
    return {"ok": True}
