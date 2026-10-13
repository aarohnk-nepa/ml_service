import hmac
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from app.core.config import settings

api_key_header = APIKeyHeader(
    name='X-API-Key',
    auto_error=False,
)

def require_service_key(
        supplied_key: str | None = Security(api_key_header),
    ) -> None:
    
    expected_key = settings.ml_service_key.get_secret_value()

    if not supplied_key or not hmac.compare_digest(
        supplied_key.encode('utf-8'),
        expected_key.encode('utf-8')

    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing service creds"
        )