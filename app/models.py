from sqlmodel import SQLModel, Field
from typing import Optional
import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    phone: str
    name: Optional[str] = None
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

class TestDrive(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_phone: str
    car_model: str
    scheduled_for: Optional[str]
    status: str = "created"
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

# Add other persistence models as needed (Bookings, Cars cache, etc.)
