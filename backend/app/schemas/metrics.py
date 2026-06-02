from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import date

class HourCount(BaseModel):
    hour: int
    count: int

class ZoneMetric(BaseModel):
    zone_name: str
    visitor_count: int
    avg_dwell_seconds: float

class DatePeriod(BaseModel):
    start: date
    end: date

class MetricsResponse(BaseModel):
    total_footfall: int
    unique_visitors: int
    conversion_rate: float
    average_dwell_time_seconds: float
    revenue_per_visitor: float
    bounce_rate: float
    peak_hours: List[HourCount]
    zone_metrics: List[ZoneMetric]
    staff_count: int
    customer_count: int
    confidence: float
    period: DatePeriod
