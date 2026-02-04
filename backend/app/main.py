from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException

from core.config import settings
from auth.router import router as auth_router
from core.dependencies import create_db_and_tables

app = FastAPI()

# Add SessionMiddleware to enable session support
# Generate a random secret key for session encryption
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

templates = Jinja2Templates(directory="templates")

app.include_router(auth_router)

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
