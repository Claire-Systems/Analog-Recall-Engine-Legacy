from datetime import datetime
from hashlib import sha384
import uuid
from .models import AuditTrace

def write_audit(db, task, memory_hit, governance_allowed, governance_status, risk_level, reason, output_text, latency_ms):
    trace_id = str(uuid.uuid4())
    tr = AuditTrace(
        trace_id=trace_id,
        task_id=task.id,
        agent_id=task.agent_id,
        task_type=task.type,
        memory_hit=memory_hit,
        governance_allowed=governance_allowed,
        governance_status=governance_status,
        risk_level=risk_level,
        reason=reason,
        input_hash=sha384(str(task.payload).encode()).hexdigest(),
        output_hash=sha384(str(output_text).encode()).hexdigest(),
        latency_ms=latency_ms,
        timestamp=datetime.utcnow(),
    )
    db.add(tr)
    db.commit()
    return trace_id
