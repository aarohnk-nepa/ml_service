from datetime import date
from typing import List, Literal, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field


router = APIRouter()

class KPIForecaseItem(BaseModel):
    date: date
    p10: float
    p50: float
    p90: float

class KPIForecastResponse(BaseModel):
    kpi: str
    warehouse_id: Optional[str] = None
    horizon_weeks: int
    data_through: date
    forecasts: List[KPIForecaseItem]

class KPIAnomalyItem(BaseModel):
    date: date
    expected_p50: float
    actuals: float
    precentage_gap: float
    direction: Literal['above', 'below'] = Field(
        ..., 
        description="Indicates if the actuals are 'above' or 'below' the expected baseline"
    )
    unusualness_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Anomaly score ranging from 0.0 (normal) to 1.0 (highly unusual)"
    )

class KPIAnaomalyResponse(BaseModel):
    target_week: date
    data_through: date
    anomalies: List[KPIForecaseItem]

@router.get("/forecast", response_mode=KPIForecastResponse)
def get_kpi_forecast(
        kpi: str = Query(..., description="target KPI slice name"),
        warehouse_id: Optional[str] = Query(..., description="optional warehouse identifier"),
        horizon_weeks: int = Query(..., description="Number of weeks to forecast"),
    ):
    """
    returns weekly quantile forecasts per for the requested kpi slice
    """
    # TODO: get kpi forecast from db
    return 1



@router.get("/anomalies", response_mode=KPIAnaomalyResponse)
def get_kpi_forecast(
        target_week: date = Query(..., description="target week date in iso format (yyyy-mm-dd)"),
        kpi: str = Query(..., description="target KPI slice name"),
    ):
    """
    Returns flagged unusualgaps for a target week, including expected p50. actuals, percentage gap, direction and and unusualness score (0.0 to 1.0)
    """
    
    # TODO: get anomalies from db

    return

