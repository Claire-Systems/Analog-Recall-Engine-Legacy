from datetime import datetime
import time
from .models import Agent, Task
from .memory import lookup_memory, write_memory
from .governance import apply_governance, deterministic_conviction
from .audit import write_audit


def assign_agent(db):
    agent = db.query(Agent).filter(Agent.status == "idle").first()
    if not agent:
        return None
    agent.status = "busy"
    agent.last_seen = datetime.utcnow()
    db.commit()
    db.refresh(agent)
    return agent

def release_agent(db, agent, success):
    agent.status = "idle"
    agent.current_task_id = None
    if success:
        agent.completed_count += 1
    else:
        agent.failed_count += 1
    agent.last_seen = datetime.utcnow()
    db.commit()

def process_task(db, task):
    t0 = time.time()
    agent = assign_agent(db)
    if not agent:
        task.status = "failed"
        task.error = "no idle agents"
        db.commit()
        return {"task_id": task.id, "status": task.status, "memory_hit": False, "latency_ms": 0}
    task.agent_id = agent.id
    task.status = "in_progress"
    agent.current_task_id = task.id
    task.updated_at = datetime.utcnow()
    db.commit()

    payload = eval(task.payload) if isinstance(task.payload, str) else task.payload
    capsule, _ = lookup_memory(db, task.type, payload)
    memory_hit = capsule is not None

    if memory_hit:
        task.result = capsule.result
        task.status = "completed"
        task.error = None
        allowed, gov_status, risk, reason = True, "completed", "low", "memory reuse"
    else:
        allowed, gov_status, risk, reason = apply_governance(task.type, payload, task.amount)
        if gov_status == "failed":
            task.status = "failed"
            task.error = reason
            task.result = None
        elif gov_status == "needs_review":
            task.status = "needs_review"
            task.result = f"pending_review:{task.type}"
        else:
            task.status = "completed"
            task.result = f"processed:{task.type}:{payload}"
            write_memory(db, task.type, payload, task.result, deterministic_conviction(task.type, str(payload)))
        task.updated_at = datetime.utcnow()

    latency = int((time.time() - t0) * 1000)
    task.trace_id = write_audit(db, task, memory_hit, allowed, gov_status, risk, reason, task.result or task.error, latency)
    db.commit()
    release_agent(db, agent, task.status == "completed")
    return {"task_id": task.id, "status": task.status, "memory_hit": memory_hit, "latency_ms": latency}
