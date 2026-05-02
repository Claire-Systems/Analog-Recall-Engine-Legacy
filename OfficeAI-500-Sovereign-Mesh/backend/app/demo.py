from .models import Agent
from .schemas import TaskInput

def ensure_agents(db, total=500):
    count = db.query(Agent).count()
    for i in range(count + 1, total + 1):
        db.add(Agent(id=i, role=f"office_agent_{i}"))
    db.commit()

def stable_tasks():
    types = ["GENERAL","EMAIL","SUPPORT","REPORT","RESEARCH","COMPLIANCE","FINANCIAL","INVOICE","PAYMENT_EXCEPTION","GENERAL"]
    tasks = []
    for i in range(500):
        t = types[i % len(types)]
        payload = {"subject": f"item-{i%50}", "recipient": f"u{i}@ex.com", "vendor": f"v{i%25}"}
        amount = 100.0 + (i % 30) * 250
        if t == "INVOICE" and i % 33 == 0:
            payload.pop("vendor", None)
        tasks.append(TaskInput(type=t, payload=payload, amount=amount, priority=(i % 5) + 1))
    return tasks
