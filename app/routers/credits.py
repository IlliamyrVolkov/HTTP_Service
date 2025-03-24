from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.crud import get_user_credits

router = APIRouter()


@router.get("/user_credits/{user_id}")
def user_credits(user_id: int, db: Session = Depends(get_db)):
    credits = get_user_credits(db, user_id)
    if not credits:
        raise HTTPException(status_code=404, detail="No credits found")

    result = []
    today = date.today()
    for credit in credits:
        closed = credit.actual_return_date is not None
        credit_data = {
            'issuance_date': str(credit.issuance_date),
            'body': credit.body,
            'percent': credit.percent,
            'is_closed': closed
        }

        if closed:
            payments_sum = sum(p.sum for p in credit.payments)
            credit_data.update({
                'return_date': str(credit.actual_return_date),
                'payments_sum': payments_sum
            })

        else:
            overdue_days = (today - credit.return_date).days if today > credit.return_date else 0
            payments_body = sum(p.sum for p in credit.payments if p.type_id == 1)
            payments_percent = sum(p.sum for p in credit.payments if p.type_id == 2)
            credit_data.update({
                'due_date': str(credit.return_date),
                'overdue_days': overdue_days,
                'payments_body': payments_body,
                'payments_percent': payments_percent
            })

            result.append(credit_data)
    return result
