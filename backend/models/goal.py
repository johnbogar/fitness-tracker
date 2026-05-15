from sqlalchemy import Column, Integer, Text, Date, DateTime
from db import Base
from datetime import datetime, timezone


class Goal(Base):
    """
    Model for goals table
    """
    __tablename__ = "Goals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    goalname = Column(Text, nullable=False)
    goaldesc = Column(Text)

    creationdate = Column(DateTime, default=datetime.now(timezone.utc))
    lastupdated = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    enddate = Column(Date)

    userid = Column(Integer, nullable=False)
    estimated_workouts = Column(Integer, nullable=True, default=10)