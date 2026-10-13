from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from datetime import date

class CustomerItem(BaseModel):
    id: int 
    p_lapse_30d: float
    p_lapse_9d: float
    d_next_order: int
    feat_attr: str

class CustomerResponse(BaseModel):
    date: date
    at_risk_cust: List[CustomerItem]
