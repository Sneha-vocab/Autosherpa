from ..db import get_session
from ..models import TestDrive
from typing import Optional
from datetime import datetime

def book_testdrive(user_phone: str, car_model: str, slot: str):
    session = get_session()
    td = TestDrive(user_phone=user_phone, car_model=car_model, scheduled_for=slot)
    session.add(td)
    session.commit()
    session.refresh(td)
    session.close()
    return td

def available_slots(location: Optional[str]=None, date: Optional[str]=None):
    # Return simple mock slots
    return ["2025-11-12 10:00", "2025-11-12 14:00", "2025-11-13 11:00"]
