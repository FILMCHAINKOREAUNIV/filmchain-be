from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.database import get_db
from app.user import crud, models, router
from typing import Optional

security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, router.SECRET_KEY, algorithms=[router.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional), db: Session = Depends(get_db)):
    if not credentials:
        return None
    token = credentials.credentials
    try:
        payload = jwt.decode(token, router.SECRET_KEY, algorithms=[router.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None
    
    user = crud.get_user_by_email(db, email=email)
    return user
