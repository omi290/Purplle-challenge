import logging
import json
from typing import Dict, Any

logger = logging.getLogger(__name__)

RECOMMENDATIONS_STRUCTURED: Dict[str, Dict[str, Any]] = {
    "queue_spike": {
        "recommendation": "Open additional billing counter immediately.",
        "confidence": 0.94,
        "reasoning": "Billing queue size has climbed to {value} shoppers, exceeding the maximum speed limit of {threshold}.",
        "expected_business_impact": "Reduces checkout wait times, saving up to ₹8,500 in potential hourly queue abandonments."
    },
    "conversion_drop": {
        "recommendation": "Deploy active floor salesperson assistance and mobile point-of-sale checkouts.",
        "confidence": 0.89,
        "reasoning": "Overall store conversion rate dropped to {value_pct}%, falling below target of {threshold_pct}%.",
        "expected_business_impact": "Recovers up to 15% of dropping customer conversions, boosting daily revenue by ₹12,000+."
    },
    "unusual_dwell": {
        "recommendation": "Check for customer confusion or stock shortage in {zone_name}. Deploy a beauty advisor.",
        "confidence": 0.85,
        "reasoning": "Average customer dwell duration in {zone_name} is abnormally high at {value_min} minutes, indicating bottleneck.",
        "expected_business_impact": "Resolves shelf-layout confusion, increasing category basket penetration by 8%."
    },
    "low_footfall": {
        "recommendation": "Refresh storefront visual merchandising and launch active cosmetic spot promotions.",
        "confidence": 0.91,
        "reasoning": "Unique customer count has declined, dropping store traffic below standard target.",
        "expected_business_impact": "Increases retail storefront stop-by traffic by 12-18%."
    },
    "high_abandonment": {
        "recommendation": "Deploy express checkout checkout zones or mobile checkout assistants immediately.",
        "confidence": 0.93,
        "reasoning": "Queue abandonment rate reached {value_pct}%, exceeding maximum threshold of {threshold_pct}%.",
        "expected_business_impact": "Recovers lost cosmetics revenue by preventing checkout abandonment."
    },
    "revenue_leakage": {
        "recommendation": "Integrate POS transaction timestamps with checkout cameras to audit potential shrinkage.",
        "confidence": 0.88,
        "reasoning": "Potential revenue leakage detected due to unconverted checkout zone visitors.",
        "expected_business_impact": "Reduces shrinkage rate and queue dropoff leakage, recovering high cosmetic margins."
    },
    "dead_zone": {
        "recommendation": "Relocate cosmetic visual displays or optimize promotional signages in {zone_name}.",
        "confidence": 0.90,
        "reasoning": "Zone {zone_name} has generated zero activity or attracted critically low traffic today.",
        "expected_business_impact": "Revitalizes store floor utilization, increasing category footfall by up to 25%."
    }
}

def get_ai_suggestion(anomaly_type: str, zone_name: str = "Store") -> str:
    """
    Returns AI suggestion mapped to the anomaly type as a plain string.
    Provided for backward compatibility.
    """
    rec_dict = get_ai_suggestion_structured(anomaly_type, zone_name)
    return rec_dict.get("recommendation", "Perform general store layout audit.")

def get_ai_suggestion_structured(
    anomaly_type: str, 
    zone_name: str = "Store", 
    value: float = 0.0, 
    threshold: float = 0.0
) -> Dict[str, Any]:
    """
    Returns a complete structured AI recommendation dictionary containing:
    - recommendation
    - confidence
    - reasoning
    - expected_business_impact
    """
    rec_template = RECOMMENDATIONS_STRUCTURED.get(
        anomaly_type,
        {
            "recommendation": "Perform general store layout audit and review staffing distribution during peak hours.",
            "confidence": 0.80,
            "reasoning": f"General operational check triggered for {anomaly_type}.",
            "expected_business_impact": "Maintains baseline operations efficiency and store standards."
        }
    )
    
    # Format templates
    value_pct = f"{value * 100:.1f}" if value <= 1.0 else f"{value:.1f}"
    threshold_pct = f"{threshold * 100:.1f}" if threshold <= 1.0 else f"{threshold:.1f}"
    value_min = f"{value / 60:.1f}" if value > 60 else f"{value:.1f}"
    
    formatted_reasoning = rec_template["reasoning"].format(
        value=f"{value:.1f}" if value else "N/A",
        threshold=f"{threshold:.1f}" if threshold else "N/A",
        value_pct=value_pct,
        threshold_pct=threshold_pct,
        value_min=value_min,
        zone_name=zone_name
    )
    
    formatted_rec = rec_template["recommendation"].format(zone_name=zone_name)
    
    return {
        "recommendation": formatted_rec,
        "confidence": rec_template["confidence"],
        "reasoning": formatted_reasoning,
        "expected_business_impact": rec_template["expected_business_impact"]
    }

def get_ai_suggestion_json(
    anomaly_type: str, 
    zone_name: str = "Store", 
    value: float = 0.0, 
    threshold: float = 0.0
) -> str:
    """
    Returns the structured recommendation serialized to a JSON string.
    """
    return json.dumps(get_ai_suggestion_structured(anomaly_type, zone_name, value, threshold))

