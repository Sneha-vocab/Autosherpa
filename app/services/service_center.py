# app/services/service_center.py
"""
Service center stub:
 - list_packages()
 - available_slots(location=None, date=None)
 - book_service(user_phone, car_model, slot, package_id=None)
"""

from typing import List, Dict, Optional
from ..db import get_session
from ..models import TestDrive  # reuse or create a ServiceBooking model in production
from datetime import datetime, timedelta

# simple in-memory packages (replace with DB)
SERVICE_PACKAGES = [
    {"id": "basic", "name": "Basic Service", "price": 1499, "desc": "Oil change, filter check, basic inspection"},
    {"id": "comprehensive", "name": "Comprehensive Service", "price": 4499, "desc": "Full inspection, fluids, brakes check"},
    {"id": "detailing", "name": "Complete Detailing", "price": 2499, "desc": "Interior + Exterior detailing and polish"},
]

# Slots generator for next 7 days, 10:00, 13:00, 16:00
def available_slots(location: Optional[str] = None, date: Optional[str] = None) -> List[str]:
    slots = []
    base = datetime.utcnow()
    # if date provided, parse naive YYYY-MM-DD
    if date:
        try:
            d = datetime.strptime(date, "%Y-%m-%d")
            base = d
        except Exception:
            base = datetime.utcnow()
    # generate 7 days of slots
    for d_offset in range(0, 7):
        d = (base + timedelta(days=d_offset)).replace(hour=0, minute=0, second=0, microsecond=0)
        for h in (10, 13, 16):
            slot = d + timedelta(hours=h)
            slots.append(slot.strftime("%Y-%m-%d %H:%M"))
    return slots

# list available service packages
def list_packages() -> List[Dict]:
    return SERVICE_PACKAGES

# simple booking that stores in TestDrive model for demo purposes.
def book_service(user_phone: str, car_model: str, slot: str, package_id: Optional[str] = None):
    """
    In production create ServiceBooking model and persist.
    For demo we reuse TestDrive table to persist a record, but you should create ServiceBooking.
    """
    session = get_session()
    # create a TestDrive-like record (temporary)
    try:
        sd = TestDrive(user_phone=user_phone, car_model=car_model, scheduled_for=slot)
        session.add(sd)
        session.commit()
        session.refresh(sd)
        return sd
    finally:
        session.close()
