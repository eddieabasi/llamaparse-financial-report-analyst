from pydantic import BaseModel
from typing import Optional


class FinancialMetrics(BaseModel):
    company: str
    ticker: Optional[str] = None
    period: str
    revenue: Optional[float] = None
    gross_profit: Optional[float] = None
    gross_margin_pct: Optional[float] = None
    net_income: Optional[float] = None
    eps_basic: Optional[float] = None
    eps_diluted: Optional[float] = None
    total_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    cash_and_equivalents: Optional[float] = None
    forward_guidance: Optional[str] = None
    key_risk_factors: list[str] = []
