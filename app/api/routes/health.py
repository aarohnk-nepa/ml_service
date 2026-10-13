from fastapi import APIRouter, Depends
from app.core.security import require_service_key

router = APIRouter()

@router.get("/", status_code=200)
def health_check(
	_: None = Depends(require_service_key)
):
	return {"status": "available"}