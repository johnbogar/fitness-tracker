from db import Base
from sqlalchemy import Column, Integer, Text, Date, DateTime
from datetime import datetime, timezone, date

class Workout(Base):
    __tablename__ = "Workouts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    goal_id = Column(Integer, nullable=True)
    date = Column(Date, default=date.today)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))