from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.schemas import CreditResponse
from app.crud import get_user_credits

router = APIRouter()


@router.get("/{user_id}", response_model=list[CreditResponse])
async def user_credits(user_id: int, db: Session = Depends(get_db)):
    credits = get_user_credits(db, user_id)
    if not credits:
        raise HTTPException(status_code=404, detail="No credits found")
    return credits
