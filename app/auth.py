import os
from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User

security = HTTPBearer(auto_error=True)


@dataclass
class AuthContext:
    user: User
    token_sub: str


def _get_db_session() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _decode_supabase_token(token: str) -> str:
    secret = os.getenv("SUPABASE_JWT_SECRET")
    if secret:
        try:
            payload = jwt.decode(token, secret, algorithms=["HS256"], options={"verify_aud": False})
            sub = payload.get("sub")
            if not sub:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Supabase token")
            return str(sub)
        except JWTError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Supabase token") from exc

    # Dev fallback: token format "dev-<external_auth_id>"
    if token.startswith("dev-") and len(token) > 4:
        return token[4:]

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Supabase auth not configured. Set SUPABASE_JWT_SECRET or use dev- token format.",
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(_get_db_session),
) -> AuthContext:
    sub = _decode_supabase_token(credentials.credentials)
    user = db.query(User).filter(User.external_auth_id == sub).first()
    if user is None:
        user = User(external_auth_id=sub)
        db.add(user)
        db.commit()
        db.refresh(user)
    return AuthContext(user=user, token_sub=sub)
