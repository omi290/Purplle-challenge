import os
import json
import logging
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)

def call_gemini_api(prompt: str, expect_json: bool = False) -> str:
    """
    Sends request to Gemini 1.5 Flash API.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return ""
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    
    if expect_json:
        payload["generationConfig"] = {
            "responseMimeType": "application/json"
        }
        
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=5) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            candidates = res_data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "").strip()
    except Exception as e:
        logger.warning(f"Failed to communicate with Gemini API: {e}")
    return ""

def explain_anomaly_ai(anomaly_type: str, severity: str, metric_val: float, threshold_val: float, zone_name: str) -> str:
    """
    Returns a human-readable explanation of an anomaly. Falls back to rule-based logic.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        prompt = (
            f"Explain this retail store anomaly to a manager:\n"
            f"Anomaly Type: {anomaly_type}\n"
            f"Severity: {severity}\n"
            f"Metric Value: {metric_val}\n"
            f"Threshold: {threshold_val}\n"
            f"Zone: {zone_name}\n"
            f"Keep the explanation to exactly 1 or 2 concise, professional sentences explaining why this happened."
        )
        ai_resp = call_gemini_api(prompt)
        if ai_resp:
            return ai_resp

    # Local Rule-Based Fallback
    if anomaly_type == "queue_spike":
        return f"Billing queue congestion detected in {zone_name}. Queue depth ({int(metric_val)}) has exceeded the optimal service threshold of {int(threshold_val)} shoppers."
    elif anomaly_type == "high_abandonment":
        return f"Checkout abandonment rate reached {metric_val*100:.1f}%, exceeding the warning threshold of {threshold_val*100:.1f}%. Customers are leaving the billing queue without making purchases."
    elif anomaly_type == "unusual_dwell":
        return f"Unusually high dwell time of {metric_val/60:.1f} minutes detected in {zone_name}. Customers are spending longer than the {threshold_val/60:.1f} minute category average, suggesting layout confusion or high advisory interest."
    elif anomaly_type == "dead_zone":
        return f"Dead zone alert in {zone_name}. The category attracted low traffic today, representing a spatial drop-off compared to active browse shelves."
    return f"Store anomaly detected in {zone_name} zone."

def suggest_action_ai(anomaly_type: str, severity: str, metric_val: float, zone_name: str) -> dict:
    """
    Returns a structured recommendation dictionary. Falls back to rule-based logic.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        prompt = (
            f"Generate a structured recommendation json for this retail anomaly:\n"
            f"Anomaly: {anomaly_type}\n"
            f"Severity: {severity}\n"
            f"Value: {metric_val}\n"
            f"Zone: {zone_name}\n"
            f"Response MUST be a single JSON object containing exact keys:\n"
            f"- 'recommendation': brief action (max 15 words)\n"
            f"- 'confidence_score': float between 0.8 and 0.99\n"
            f"- 'reasoning': short justification sentence\n"
            f"- 'expected_business_impact': economic outcome sentence"
        )
        ai_resp = call_gemini_api(prompt, expect_json=True)
        if ai_resp:
            try:
                return json.loads(ai_resp)
            except Exception:
                pass

    # Local Rule-Based Fallback
    if anomaly_type == "queue_spike":
        return {
            "recommendation": "Open additional billing counter immediately. Deploy mobile checkout floor advisors.",
            "confidence_score": 0.94,
            "reasoning": f"Queue size of {int(metric_val)} exceeds operational threshold, creating checkout bottleneck.",
            "expected_business_impact": "Reduces queue wait times, protects brand reputation, and lowers checkout abandonment risks."
        }
    elif anomaly_type == "high_abandonment":
        return {
            "recommendation": "Deploy floor supervisors to assist checkout queue and handle cashier escalations.",
            "confidence_score": 0.93,
            "reasoning": f"Abandonment rate of {metric_val*100:.1f}% indicates customer friction and lost purchase conversion.",
            "expected_business_impact": "Recovers up to 15% of checkout drop-off sales leakage and increases transaction conversion."
        }
    elif anomaly_type == "unusual_dwell":
        return {
            "recommendation": "Deploy a beauty advisor to assist customers in the category.",
            "confidence_score": 0.85,
            "reasoning": f"High category dwell indicates customers are interested but may be confused by layout or signage.",
            "expected_business_impact": "Shortens category bottleneck and improves customer purchase conversion."
        }
    elif anomaly_type == "dead_zone":
        return {
            "recommendation": "Refresh marketing display signage or offer promotional product bundling in the category.",
            "confidence_score": 0.90,
            "reasoning": f"Under-utilized category zone indicates low shopper traffic attraction.",
            "expected_business_impact": "Increases category traffic and drives browsing activity into dead zone shelves."
        }
    return {
        "recommendation": "Deploy a store assistant to audit layout layout categories.",
        "confidence_score": 0.80,
        "reasoning": "Standard anomaly response template.",
        "expected_business_impact": "Protects overall retail conversions."
    }

def generate_store_summary_ai(metrics: dict, leakage: dict, opportunity: dict) -> dict:
    """
    Generates an executive store operational summary. Falls back to rule-based logic.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        prompt = (
            f"Generate an executive store operational summary JSON for these metrics:\n"
            f"Footfall: {metrics.get('total_footfall')}\n"
            f"Conversion Rate: {metrics.get('conversion_rate')*100:.1f}%\n"
            f"Revenue Leakage: ₹{leakage.get('estimated_leaked_revenue')}\n"
            f"Opportunity Loss: ₹{opportunity.get('estimated_revenue_impact')}\n"
            f"Response MUST be a single JSON object containing exact keys:\n"
            f"- 'summary': executive status sentence (max 20 words)\n"
            f"- 'risks': operational threat sentence (max 20 words)\n"
            f"- 'opportunities': growth opportunity sentence (max 20 words)"
        )
        ai_resp = call_gemini_api(prompt, expect_json=True)
        if ai_resp:
            try:
                return json.loads(ai_resp)
            except Exception:
                pass

    # Local Rule-Based Fallback
    footfall = metrics.get('total_footfall', 0)
    conversion = metrics.get('conversion_rate', 0.0) * 100
    leaked = leakage.get('estimated_leaked_revenue', 0.0)
    lost = opportunity.get('estimated_revenue_impact', 0.0)
    
    if footfall > 0:
        summary = f"Store is operating with {footfall} visitors and {conversion:.1f}% customer conversion rate."
        risks = f"Revenue leakage of ₹{leaked:,.2f} detected from checkout line abandonments."
        opportunities = f"Recovering 15% of unconverted browse traffic can recover ₹{lost:,.2f} in sales."
    else:
        summary = "Operational console starts clean. Awaiting video ingestion to build metrics."
        risks = "No operational risks registered."
        opportunities = "Awaiting transaction data to highlight conversion opportunities."
        
    return {
        "summary": summary,
        "risks": risks,
        "opportunities": opportunities
    }
