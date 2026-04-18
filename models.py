# models.py
from sqlalchemy import Column, Integer, String, DateTime, Enum
from database import Base
from datetime import datetime

class Packet(Base):
    __tablename__ = "packets"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now)
    src_ip = Column(String)
    dst_ip = Column(String)
    protocol = Column(Integer)
    length = Column(Integer)
    sport = Column(Integer, nullable=True)
    dport = Column(Integer, nullable=True)
    flags = Column(String, nullable=True)

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now)
    src_ip = Column(String)
    dst_ip = Column(String)
    rule_name = Column(String)
    severity = Column(Enum("LOW", "MEDIUM", "HIGH", "CRITICAL", name="severity_enum"))
    description = Column(String)