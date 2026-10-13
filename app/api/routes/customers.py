from datetime import date
from fastapi import APIRouter, Depends, Query, HTTPException
from app.api.schemas import customers


router = APIRouter()

@router.get("/risk", response_model=customers.CustomerResponse)
def get_cust_at_risk(
        date: date
    ):
    """
    returns ranked custs at risk
    """
    # TODO: get kpi forecast from db
    return 1
