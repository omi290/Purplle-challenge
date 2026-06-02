from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class ComponentScore(BaseModel):
    score: float
    weight: float

class StoreHealth(BaseModel):
    overall_score: float
    grade: str
    components: Dict[str, ComponentScore]

class RevenueLeakage(BaseModel):
    leakage_rate: float
    estimated_leaked_revenue: float
    potential_total_revenue: float

class OpportunityLoss(BaseModel):
    total_opportunities_lost: int
    estimated_revenue_impact: float
    top_reasons: list[str]

class SystemHealthResponse(BaseModel):
    status: str
    version: str
    uptime_seconds: float
    database: str
    last_event_time: Optional[datetime] = None
    total_events: int
    store_health: StoreHealth
    revenue_leakage: RevenueLeakage
    opportunity_loss: OpportunityLoss
