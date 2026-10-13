from datetime import date
from typing import List, Literal, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from app.api.schemas import kpi


router = APIRouter()

@router.get("/forecast", response_model=kpi.KPIForecastResponse)
def get_kpi_forecast(
        kpi: str = Query(..., description="target KPI slice name"),
        warehouse_id: Optional[str] = Query(None, description="optional warehouse identifier"),
        horizon_weeks: int = Query(..., description="Number of weeks to forecast"),
    ):
    """
    returns weekly quantile forecasts per for the requested kpi slice
    """
    # TODO: get kpi forecast from db
    return 1



@router.get("/anomalies", response_model=kpi.KPIAnaomalyResponse)
def get_kpi_forecast(
        target_week: date = Query(..., description="target week date in iso format (yyyy-mm-dd)"),
        kpi: str = Query(..., description="target KPI slice name"),
    ):
    """
    Returns flagged unusualgaps for a target week, including expected p50. actuals, percentage gap, direction and and unusualness score (0.0 to 1.0)
    """
    
    # TODO: get anomalies from db

    return

