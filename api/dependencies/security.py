import secrets
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials


basic_auth = HTTPBasic(auto_error=True)


def verify_basic_auth(credentials: HTTPBasicCredentials = Depends(basic_auth)) -> str:

    expected_password = os.getenv("PRIVATE_PASSWORD")

    if not expected_password:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Private endpoint auth is not configured",
        )

    if not secrets.compare_digest(credentials.password, expected_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username
