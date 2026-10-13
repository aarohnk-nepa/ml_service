from typing import List, Literal, Optional
from datetime import date
from pydantic import BaseModel, Field

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