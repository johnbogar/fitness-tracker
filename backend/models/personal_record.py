from db import Base
from sqlalchemy import Column, Integer, Text, Float, Date, DateTime
from datetime import datetime, timezone, date

class PersonalRecord(Base):
    __tablename__ = "PersonalRecords"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(Integer, nullable=False)
    exercise    = Column(Text, nullable=False)
    value       = Column(Float, nullable=False)
    unit        = Column(Text, nullable=False)
    achieved_on = Column(Date, default=date.today)
    notes       = Column(Text, nullable=True)
    created_at  = Column(DateTime, default=lambda: datetime.now(timezone.utc))
