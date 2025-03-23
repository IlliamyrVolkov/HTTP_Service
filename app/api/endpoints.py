from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from sqlalchemy.orm import Session
from datetime import date
import pandas as pd

from app.database import get_db
from app.models import Credit, Payment, Plan, Dictionary
from crud import get_user_credits

router = APIRouter()


@router.get('/user_credits/{user_id}')
async def user_credits(user_id: int, db: Session = Depends(get_db)):
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


@router.post('/plans_insert')
async def insert_plans(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        df = pd.read_csv(file.file, delimiter='\t')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Unable to read the file: {e}')

    for index, row in df.iterrows():
        period = row.get('period')
        category_name = row.get('category')
        plan_sum = row.get('sum')

        if pd.isna(period) or pd.isna(category_name) or pd.isna(plan_sum):
            raise HTTPException(status_code=400, detail=f'Empty values in the string {index}')

        if period.day != 1:
            raise HTTPException(status_code=400,
                                detail=f'The plan date in the {index} line is not the first day of the month')

        category = db.query(Dictionary).filter(Dictionary.name == category_name).first()
        if not category:
            raise HTTPException(status_code=400, detail=f"Category {category_name} not found in string {index}")

        existing_plan = db.query(Plan).filter(Plan.period == period, Plan.category_id == category.id).first()
        if existing_plan:
            raise HTTPException(status_code=400,
                                detail=f'A plan with this month and category already exists (line {index})')

        new_plan = Plan(
            period=period,
            sum=plan_sum,
            category_id=int(category.id.__clause_element__().value)

        )
        db.add(new_plan)

    db.commit()
    return {'detail': 'Plans successfully entered into the database'}


@router.get('/plans_performance')
async def plans_performance(
        as_of: date = Query(..., description='Дата перевірки виконання планів (формат: YYYY-MM-DD)'),
        db: Session = Depends(get_db)):
    results = []
    plans = db.query(Plan).all()
    for plan in plans:
        category_name = plan.category.name

        start_date = plan.period

        if category_name.lower() == 'видача':

            credits = db.query(Credit).filter(Credit.issuance_date >= start_date, Credit.issuance_date <= as_of).all()
            actual_sum = sum(c.body for c in credits)
        elif category_name.lower() == 'збір':

            payments = db.query(Payment).filter(Payment.payment_date >= start_date, Payment.payment_date <= as_of).all()
            actual_sum = sum(p.sum for p in payments)
        else:
            actual_sum = 0

        performance_percent = (actual_sum / plan.sum * 100) if plan.sum > 0 else 0
        results.append({
            'plan_period': str(plan.period),
            'category': category_name,
            'plan_sum': plan.sum,
            'actual_sum': actual_sum,
            'performance_percent': performance_percent
        })
    return results


@router.get('/year_performance')
async def year_performance(year: int, db: Session = Depends(get_db)):
    from sqlalchemy import func
    results = []

    for month in range(1, 13):
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)

        credits_count = db.query(func.count(Credit.id)).filter(Credit.issuance_date >= start_date,
                                                               Credit.issuance_date < end_date).scalar() or 0
        plan_issue_sum = db.query(func.sum(Plan.sum)) \
                             .join(Dictionary, Plan.category_id == Dictionary.id) \
                             .filter(Plan.period.is_(start_date), Dictionary.name.ilike('%видача%')).scalar() or 0
        actual_issue_sum = db.query(func.sum(Credit.body)).filter(Credit.issuance_date >= start_date,
                                                                  Credit.issuance_date < end_date).scalar() or 0
        performance_issue = (actual_issue_sum / plan_issue_sum * 100) if plan_issue_sum > 0 else 0

        payments_count = db.query(func.count(Payment.id)).filter(Payment.payment_date >= start_date,
                                                                 Payment.payment_date < end_date).scalar() or 0
        plan_collection_sum = db.query(func.sum(Plan.sum)) \
                                  .join(Dictionary) \
                                  .filter(Plan.period.is_(start_date), Dictionary.name.ilike('%збір%')).scalar() or 0
        actual_collection_sum = db.query(func.sum(Payment.sum)).filter(Payment.payment_date >= start_date,
                                                                       Payment.payment_date < end_date).scalar() or 0
        performance_collection = (actual_collection_sum / plan_collection_sum * 100) if plan_collection_sum > 0 else 0

        results.append({
            'month': month,
            'credits_count': credits_count,
            'plan_issue_sum': plan_issue_sum,
            'actual_issue_sum': actual_issue_sum,
            'performance_issue_percent': performance_issue,
            'payments_count': payments_count,
            'plan_collection_sum': plan_collection_sum,
            'actual_collection_sum': actual_collection_sum,
            'performance_collection_percent': performance_collection,
        })
    return results
