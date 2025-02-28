import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

KEYCLOAK_CLIENT_PUBLIC_KEY = os.getenv("KEYCLOAK_CLIENT_PUBLIC_KEY", "")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        print("TOKEN", KEYCLOAK_CLIENT_PUBLIC_KEY)
        public_key = (
            "-----BEGIN PUBLIC KEY-----\n"
            + "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAx3V7fKMuAO055R158iL18lehMdjFOZr1P7tmvrbQK3v/9hgbB6ROhOAmT1Aj+ml7rNMb+eMeJEPvDuE5sQm9hMUAU88bWC/pqWyCIegEEWEixeItUrBZLxEsmWagF5wFc90juNxu0qXEf2r/oKuRSdWuJXRx4IRkZm24XzlTLI/z7DZUvRL3t4e/XpnLgb8dVRw/xSmrqAFnbXbRaESDpp77KhTKlhxkVBiT5rBKRwAwI3a7kEYEFtvX3wpRimGPOh/uogtbHn1wKPmFLfpcchu6eIozvWTcVPkfPPSqOwS7HyYlHUdMS+MSjKlmM9dBCh81kgxRWbXLkz0vf6dQ3QIDAQAB"
            + "\n-----END PUBLIC KEY-----"
        )
        decoded_token = jwt.decode(
            token, public_key, algorithms=["RS256"], options={"verify_aud": False}
        )
        return decoded_token

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_current_user(user=Depends(verify_token)):
    return user
