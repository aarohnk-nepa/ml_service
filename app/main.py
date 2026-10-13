from fastapi import FastAPI, APIRouter, Depends
from pydantic import BaseModel, version
from app.api.routes import kpi, demand, customers, health
from app.core.security import require_service_key

app = FastAPI(
    title="ml_service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None
)

ml_router = APIRouter(
    prefix="api/v1/ml",
    dependencies=[Depends(require_service_key)]
)

# api routers
ml_router.include_router(kpi.router, prefix="kpi", tags=["KPI Forecasts and Anomolies"])
ml_router.include_router(demand.router, prefix="/demand", tags=["Demand Forecast"])
ml_router.include_router(customers.router, prefix="/customer", tags=["Customer Risk and churn"])
ml_router.include_router(health.router, prefix="/healthz", tags=["health and models"])

#mount router
app.include_router(ml_router)




