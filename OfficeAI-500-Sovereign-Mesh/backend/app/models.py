from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey
from .database import Base

class Agent(Base):
    __tablename__ = "agents"
    id = Column(Integer, primary_key=True)
    role = Column(String, default="virtual_worker")
    status = Column(String, default="idle")
    current_task_id = Column(Integer, nullable=True)
    completed_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    last_seen = Column(DateTime, default=datetime.utcnow)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    type = Column(String)
    payload = Column(Text)
    amount = Column(Float, default=0.0)
    priority = Column(Integer, default=1)
    status = Column(String, default="queued")
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    result = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    trace_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class MemoryCapsule(Base):
    __tablename__ = "memory_capsules"
    capsule_id = Column(String, primary_key=True)
    task_type = Column(String)
    input_hash = Column(String)
    payload_hash = Column(String)
    result = Column(Text)
    confidence = Column(Float)
    integrity_hash = Column(String)
    verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, default=datetime.utcnow)
    use_count = Column(Integer, default=0)

class AuditTrace(Base):
    __tablename__ = "audit_traces"
    trace_id = Column(String, primary_key=True)
    task_id = Column(Integer)
    agent_id = Column(Integer, nullable=True)
    task_type = Column(String)
    memory_hit = Column(Boolean, default=False)
    governance_allowed = Column(Boolean, default=False)
    governance_status = Column(String)
    risk_level = Column(String)
    reason = Column(Text)
    input_hash = Column(String)
    output_hash = Column(String)
    latency_ms = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
