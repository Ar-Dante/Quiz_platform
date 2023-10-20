from typing import Optional

from pydantic import BaseModel


class CompanyCreate(BaseModel):
    company_name: str
    company_title: Optional[str] = None
    company_description: Optional[str] = None
    company_city: Optional[str] = None
    company_phone: Optional[str] = None


class CompanyDetail(BaseModel):
    company_name: str
    company_title: Optional[str] = None
    company_description: Optional[str] = None


class CompanyUpdate(BaseModel):
    company_name: str
    company_title: Optional[str] = None
    company_description: Optional[str] = None
    company_city: Optional[str] = None
    company_phone: Optional[str] = None
    is_visible: bool

