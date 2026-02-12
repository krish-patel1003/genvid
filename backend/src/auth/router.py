from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from src.db import get_session
from src.auth.models import User, OAuthAccount
from src.auth.schema import SignupSchema, TokenSchema
from src.auth.password import hash_password, verify_password
from src.security import create_access_token
from src.auth.utils import get_current_user
from src.auth.google_oauth import google
from src.config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=TokenSchema)
def signup(data: SignupSchema, session: Session = Depends(get_session)):
    stmt = select(User).where(
        (User.email == data.email) | (User.username == data.username)
    )
    existing = session.exec(stmt).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        email=data.email,
        username=data.username,
        hashed_password=hash_password(data.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    token = create_access_token(subject=str(user.id))
    return {"access_token": token}


@router.post("/token", response_model=TokenSchema)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    stmt = select(User).where(
        (User.username == form_data.username) | (User.email == form_data.username)
    )
    user = session.exec(stmt).first()

    if not user or not user.hashed_password:
        raise HTTPException(status_code=401, detail="Incorrect credentials")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect credentials")

    token = create_access_token(subject=str(user.id))
    return {"access_token": token}


@router.get("/google/login")
async def google_login(request: Request):
    settings = get_settings()
    base_url = settings.SERVICE_URL.rstrip("/")
    redirect_uri = f"{base_url}/auth/google/callback"
    return await google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback", name="google_callback", response_model=TokenSchema)
async def google_callback(request: Request, session: Session = Depends(get_session)):
    token = await google.authorize_access_token(request)
    user_info = await google.userinfo(token=token)

    stmt = select(OAuthAccount).where(
        OAuthAccount.provider == "google",
        OAuthAccount.provider_user_id == user_info["sub"],
    )
    oauth = session.exec(stmt).first()

    if oauth:
        user = oauth.user
    else:
        user = User(
            email=user_info["email"],
            username=user_info["email"].split("@")[0],
            profile_pic=user_info.get("picture"),
        )
        session.add(user)
        session.flush()

        oauth = OAuthAccount(
            user_id=user.id,
            provider="google",
            provider_user_id=user_info["sub"],
        )
        session.add(oauth)

    session.commit()

    jwt_token = create_access_token(subject=str(user.id))
    return {"access_token": jwt_token}
