from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from core.dependencies import get_db, get_current_user
from auth.schemas import SignupSchema, TokenSchema, UserPublicSchema
from auth.models import User, OAuthAccount
from auth.password import hash_password, verify_password
from auth.jwt import create_access_token
from auth.google_oauth import google

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=TokenSchema)
def signup(data: SignupSchema, db=Depends(get_db)):
    # Minimal example: enforce unique username/email yourself (recommended)
    existing = db.query(User).filter((User.email == data.email) | (User.username == data.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        email=data.email,
        username=data.username,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}


@router.post("/token", response_model=TokenSchema)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db=Depends(get_db),
):
    # allows both email and username login via same field
    user = db.query(User).filter((User.username == form_data.username) | (User.email == form_data.username)).first()
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=str(user.id))
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserPublicSchema)
def me(current_user: User = Depends(get_current_user)):
    return current_user


# ---------- Google OAuth (unchanged conceptually) ----------

@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = request.url_for("google_callback")
    return await google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback", name="google_callback", response_model=TokenSchema)
async def google_callback(request: Request, db=Depends(get_db)):
    token = await google.authorize_access_token(request)

    # tutorial doesn’t cover this, but userinfo is usually more robust than parsing id_token
    user_info = await google.userinfo(token=token)

    oauth = (
        db.query(OAuthAccount)
        .filter_by(provider="google", provider_user_id=user_info["sub"])
        .first()
    )

    if oauth:
        user = oauth.user
    else:
        # create user
        user = User(
            email=user_info["email"],
            username=user_info["email"].split("@")[0],
            profile_pic=user_info.get("picture"),
            hashed_password=None,
        )
        db.add(user)
        db.flush()

        oauth = OAuthAccount(
            user_id=user.id,
            provider="google",
            provider_user_id=user_info["sub"],
        )
        db.add(oauth)

    db.commit()

    jwt_token = create_access_token(subject=str(user.id))
    return {"access_token": jwt_token, "token_type": "bearer"}
