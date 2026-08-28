from fastapi import APIRouter, HTTPException, Response, status

from app.api.deps import BearerToken, CurrentAttorney, DbSession
from app.schemas.auth import LoginRequest, LoginResponse, MeResponse
from app.services.auth import authenticate, create_session, invalidate_session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, db: DbSession) -> LoginResponse:
    attorney = authenticate(db, username=body.username, password=body.password)
    if attorney is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid username or password")
    session = create_session(db, attorney)
    return LoginResponse(token=session.token, username=attorney.username)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(db: DbSession, token: BearerToken) -> Response:
    if token:
        invalidate_session(db, token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=MeResponse)
def me(current_attorney: CurrentAttorney) -> MeResponse:
    return MeResponse(username=current_attorney.username)
