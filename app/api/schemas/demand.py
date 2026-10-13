from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class DemandItem(BaseModel):
    p10: float
    p50: float
    p90: float


class DemandResponse(BaseModel):
    wh_id: str
    product_id: int
    forecast: List[DemandItem]