# app/services/valuation_service.py
"""
Valuation service stub.
Provides:
 - estimate_value: quick heuristic estimator
 - call_partner_api: placeholder to call partner valuation APIs (Cars24/Spinny)
"""

from datetime import datetime
import random
import math
import requests
from .car_service import get_car_by_id

# Simple depreciation table (annual %)
DEFAULT_DEPRECIATION_RATE = 0.15  # 15% per year baseline

def _yearly_depreciation_rate(age_years: int) -> float:
    """
    Very simple model: higher depreciation in first 3 years, then slows.
    """
    if age_years <= 0:
        return 0.0
    if age_years == 1:
        return 0.25
    if age_years == 2:
        return 0.20
    if age_years == 3:
        return 0.17
    # older cars depreciate slower
    return max(0.07, DEFAULT_DEPRECIATION_RATE)

def estimate_value(model: str, year: int, kms: int = 0, condition: str = "good") -> int:
    """
    Heuristic car valuation:
    - Look up base price from car_service if available (new price).
    - Apply age-based depreciation and mileage/condition adjustments.
    Returns estimated INR (rounded).
    """
    today = datetime.utcnow()
    age = max(0, today.year - int(year))

    # find base price (if we have the model in catalogue)
    car = get_car_by_id(model)
    if car and car.get("price"):
        base_price = car["price"]
    else:
        # fallback base price based on category heuristics
        # if model not in DB, assume a mid-range price
        base_price = 1000000  # 10 lakh fallback

    # compute depreciation cumulatively
    est = base_price
    for y in range(age):
        r = _yearly_depreciation_rate(y+1)
        est = est * (1 - r)

    # mileage adjustment: more kms -> lower value
    # assume average annual kms 12,000 -> adjust ± by kms ratio
    kms_penalty = 0
    if kms and age > 0:
        avg_ann_kms = kms / max(1, age)
        # penalize if above 15000/yr, modest bonus if below 8000/yr
        if avg_ann_kms > 20000:
            kms_penalty = est * 0.10  # -10%
        elif avg_ann_kms > 15000:
            kms_penalty = est * 0.05
        elif avg_ann_kms < 8000:
            kms_penalty = -est * 0.03  # increase value by 3%

    est = est - kms_penalty

    # condition adjustments
    cond = condition.lower() if condition else "good"
    if cond in ("excellent", "like new"):
        est *= 1.03
    elif cond in ("good", ""):
        est *= 1.0
    elif cond in ("fair", "average"):
        est *= 0.94
    elif cond in ("poor", "bad"):
        est *= 0.80

    # random market noise ± up to 3% to simulate market fluctuations
    noise = 1 + random.uniform(-0.03, 0.03)
    est = est * noise

    # lower bound floor to 5% of base price
    floor = base_price * 0.05
    est = max(floor, est)

    return int(round(est))


def call_partner_api(model: str, year: int, kms: int = 0, reg_no: str = None) -> dict:
    """
    Placeholder: call a partner valuation API (Cars24 / Spinny / local provider).
    Implement auth and request according to partner docs.

    Returns:
        dict with keys: {estimated_value, currency, confidence, source}
    """
    # Example pseudocode (do not run):
    # url = "https://partner.example.com/valuation"
    # payload = {"model": model, "year": year, "kms": kms, "reg_no": reg_no}
    # headers = {"Authorization": f"Bearer {PARTNER_KEY}", "Content-Type": "application/json"}
    # resp = requests.post(url, json=payload, headers=headers, timeout=8)
    # resp.raise_for_status()
    # return resp.json()

    # For now return a simulated response using local estimator
    est = estimate_value(model=model, year=year, kms=kms, condition="good")
    return {
        "estimated_value": est,
        "currency": "INR",
        "confidence": 0.72,
        "source": "local_heuristic"
    }
