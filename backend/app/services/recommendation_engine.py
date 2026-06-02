import logging
from typing import Dict

logger = logging.getLogger(__name__)

RECOMMENDATIONS: Dict[str, str] = {
    "queue_spike": "Open additional billing counter. Current queue exceeds optimal threshold of 8 people.",
    "conversion_drop": "Review queue congestion and staffing. Consider deploying mobile point-of-sale checkouts or active floor assistance.",
    "unusual_dwell": "Check for customer confusion in {zone_name}. Review shelf stocking, pricing tags clarity, or deploy a beauty advisor for assistance.",
    "low_footfall": "Increase storefront visual merchandising. Launch spot promotions in high footfall hours or direct social media campaigns for the Brigade Bangalore store.",
    "high_abandonment": "Deploy additional staff to billing area to assist checkout flow. Consider queue entertainment or express checkout lanes.",
    "revenue_leakage": "Cross-reference billing zone visitors with POS transaction times. Check for payment gateway timeouts or potential shrinkage.",
}

def get_ai_suggestion(anomaly_type: str, zone_name: str = "Store") -> str:
    """
    Returns AI suggestion mapped to the anomaly type.
    """
    template = RECOMMENDATIONS.get(
        anomaly_type, 
        "Perform general store layout audit and review staffing distribution during peak hours."
    )
    return template.format(zone_name=zone_name)
