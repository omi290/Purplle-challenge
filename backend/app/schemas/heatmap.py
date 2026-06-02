from pydantic import BaseModel
from typing import List, Dict, Optional

class HeatmapZoneCoordinates(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float

class HeatmapZone(BaseModel):
    zone_name: str
    zone_type: str
    visitor_count: int
    avg_dwell_seconds: float
    intensity: float
    data_confidence: str
    coordinates: HeatmapZoneCoordinates

class HeatmapResponse(BaseModel):
    zones: List[HeatmapZone]
    max_visitors: int
    total_zones: int
