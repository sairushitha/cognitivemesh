from sqlalchemy import Column, String, Text, DateTime, Integer
from sqlalchemy.sql import func
from db.database import Base
import uuid


class Debate(Base):
    __tablename__ = "debates"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    topic = Column(Text, nullable=False)
    status = Column(String, default="pending")  # pending | running | complete | error
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)


class DebateMessage(Base):
    __tablename__ = "debate_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    debate_id = Column(String, nullable=False, index=True)
    agent = Column(String, nullable=False)  # scientist | critic | ethicist | optimizer | consensus
    round_num = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
