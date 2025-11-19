from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from clerk import Clerk
from os import environ
import logging

# In a real app, use a more secure way to manage secrets.
clerk_secret_key = environ.get("CLERK_SECRET_KEY")
clerk = None

if not clerk_secret_key:
    logging.warning(
        "CLERK_SECRET_KEY not found in environment variables. "
        "Authentication will not work."
    )
else:
    try:
        clerk = Clerk(secret_key=clerk_secret_key)
    except Exception as e:
        logging.error(f"Failed to initialize Clerk: {e}")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    # For local testing without authentication, return a test user ID
    if not clerk:
        logging.info("Auth not configured - using test user ID: test_user_123")
        return "test_user_123"
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        decoded_token = clerk.verify_token(token)
        user_id = decoded_token["sub"]
        return user_id
    except Exception as e:
        logging.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
