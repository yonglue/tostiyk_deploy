from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Any
from app.services.printer import print_receipt, print_test_page, printer_status
from app.deps import get_current_actor 

router = APIRouter(prefix="/api/printer", tags=["printer"])


class ReceiptPayload(BaseModel):
    data: dict[str, Any]


@router.get("/status", dependencies=[Depends(get_current_actor)])
def status():
    return printer_status()


@router.post("/test", dependencies=[Depends(get_current_actor)])
def test_print():
    try:
        return print_test_page()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"print failed: {e}")


@router.post("/receipt", dependencies=[Depends(get_current_actor)])
def receipt(payload: ReceiptPayload):
    try:
        return print_receipt(payload.data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"print failed: {e}")
