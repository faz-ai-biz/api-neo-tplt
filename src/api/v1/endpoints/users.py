from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(tags=["users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    """
    Get current user information
    Requires authentication
    """
    return {"username": "testuser", "email": "test@example.com"}
