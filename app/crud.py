from sqlalchemy.orm import Session
from datetime import date
from app.models import User, Credit, Plan, Dictionary, Payment


def create_user(db: Session, login: str, registration_date: date):
    user = User(login=login, registration_date=registration_date)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_users(db: Session):
    return db.query(User).all()


def get_user_credits(db: Session, user_id: int):
    return db.query(Credit).filter(Credit.user_id.is_(user_id)).all()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id.is_(user_id)).first()


def create_plan(db: Session, period: date, sum: float, category_id: int):
    existing_plan = db.query(Plan).filter(Plan.period.is_(period), Plan.category_id.is_(category_id))
    if existing_plan:
        return None

    plan = Plan(period=period, sum=sum, category_id=category_id)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def get_plans(db: Session):
    return db.query(Plan).all()


def get_dictionary(db: Session):
    return db.query(Dictionary).all()


def create_payment(db: Session, sum: float, payment_date: date, credit_id: int, type_id: int):
    payment = Payment(sum=sum, payment_date=payment_date, credit_id=credit_id, type_id=type_id)
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def get_payments(db: Session):
    return db.query(Payment).all()
