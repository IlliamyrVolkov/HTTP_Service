from datetime import date
from typing import Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    login: str
    registration_date: date


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True


class CreditBase(BaseModel):
    user_id: int
    issuance_date: date
    return_date: Optional[date] = None
    actual_return_date: Optional[date] = None
    body: float
    percent: float


class CreditCreate(CreditBase):
    pass


class CreditResponse(CreditBase):
    id: int

    class Config:
        orm_mode = True


class DictionaryBase(BaseModel):
    name: str


class DictionaryCreate(DictionaryBase):
    pass


class DictionaryResponse(DictionaryBase):
    id: int

    class Config:
        orm_mode = True


class PlanBase(BaseModel):
    period: date
    sum: float
    category_id: int


class PlanCreate(PlanBase):
    pass


class PlanResponse(PlanBase):
    id: int

    class Config:
        orm_mode = True


class PaymentBase(BaseModel):
    sum: float
    payment_date: date
    credit_id: int
    type_id: int


class PaymentCreate(PaymentBase):
    pass


class PaymentResponse(PaymentBase):
    id: int

    class Config:
        orm_mode = True
