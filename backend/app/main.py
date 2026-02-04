from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import secrets

from auth.google_oauth import google

app = FastAPI()

# Add SessionMiddleware to enable session support
# Generate a random secret key for session encryption
app.add_middleware(SessionMiddleware, secret_key=secrets.token_urlsafe(16))

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    google_auth_url = request.url_for("auth_callback")
    return templates.TemplateResponse("index.html", {"request": request, "google_auth_url": f"/login"})

@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth_callback")
    return await google.authorize_redirect(request, redirect_uri)


@app.get("/auth/callback")
async def auth_callback(request: Request):

    try:
        token = await google.authorize_access_token(request)
        print("TOKEN STRUCTURE: ", token)
        print("TOKEN KEYS: ", list(token.keys()))

        # Use userinfo endpoint instead of trying to parse id_token
        user_info = await google.userinfo(token=token)
        print({"message": "Authentication Successful", "user_info": user_info})

    except Exception as e:
        print(f"Error during auth callback: {e}")
        return {"error": str(e)}
