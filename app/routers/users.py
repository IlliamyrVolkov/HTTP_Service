from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import UserCreate, UserResponse
from app.crud import create_user

router = APIRouter()


@router.post("/", response_model=UserResponse)
def create_new_user(user_data: UserCreate, db: Session = Depends(get_db)):
    new_user = create_user(db, user_data.login, user_data.registration_date)
    return new_user
