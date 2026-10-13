from datetime import date
from typing import List, Literal, Optional
from app.api.schemas import demand
from fastapi import APIRouter, Depends, HTTPException, Query


router = APIRouter()

@router.get('/forecast', response_model=demand.DemandResponse)
def get_demand(
    wh_id: str = Query(..., description="warehouse/vanlabel (warehouse{companyid} or van{journalid})"),
    product_id: int = Query(..., description="product template id"),
    horizon_weeks: int = Query(..., description="forecast length")
    ):
    """
    returns forecast per wh-product pair
    """
    # TODO: get forecast data from db
    pass