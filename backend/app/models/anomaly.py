from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, func
from app.database import Base

class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, index=True)
    anomaly_type = Column(String(64), nullable=False, index=True)  # queue_spike, conversion_drop, unusual_dwell, low_footfall, high_abandonment, revenue_leakage
    severity = Column(String(16), nullable=False, default="medium")  # low, medium, high, critical
    description = Column(Text, nullable=False)
    suggested_action = Column(Text, nullable=True)
    detected_at = Column(DateTime, index=True, default=func.now())
    confidence = Column(Float, nullable=False, default=1.0)
    metric_value = Column(Float, nullable=True)
    threshold_value = Column(Float, nullable=True)
    zone_name = Column(String(128), index=True, nullable=True)
    resolved = Column(Boolean, default=False)
    manager_feedback = Column(Text, nullable=True)
    disagreed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    @property
    def ai_recommendation(self) -> dict:
        import json
        default_impact = "Enhance retail conversion and mitigate customer checkout friction."
        
        if self.suggested_action:
            try:
                data = json.loads(self.suggested_action)
                if isinstance(data, dict) and "recommendation" in data:
                    # Make sure fields are present
                    return {
                        "recommendation": data.get("recommendation", self.suggested_action),
                        "confidence": float(data.get("confidence", self.confidence)),
                        "reasoning": data.get("reasoning", f"Operational alert triggered for {self.anomaly_type} in {self.zone_name or 'Store'}."),
                        "expected_business_impact": data.get("expected_business_impact", default_impact)
                    }
            except Exception:
                pass
                
            return {
                "recommendation": self.suggested_action,
                "confidence": round(self.confidence, 2),
                "reasoning": f"Flagged based on operational metric value of {self.metric_value} exceeding threshold {self.threshold_value} in {self.zone_name or 'Store'}.",
                "expected_business_impact": default_impact
            }
            
        return {
            "recommendation": "Perform general store layout audit and staff training.",
            "confidence": 1.0,
            "reasoning": "System operational status monitoring.",
            "expected_business_impact": default_impact
        }

