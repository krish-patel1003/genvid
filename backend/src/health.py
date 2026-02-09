from fastapi import APIRouter, Depends

router = APIRouter()


@router.get("/healthz", tags=["health"])
def healthz():
    return {"status": "healthy"}


@router.get("/readyz", tags=["health"])
def readyz():
    # later: check DB connectivity, pubsub, etc.
    return {"status": "ready"}