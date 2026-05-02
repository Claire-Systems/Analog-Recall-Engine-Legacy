from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .models import Agent, Task, MemoryCapsule, AuditTrace
from .schemas import TaskInput, BatchInput
from .mesh import process_task
from .demo import ensure_agents, stable_tasks
from .memory import write_memory, lookup_memory, capsule_id_for, integrity_for
from .governance import deterministic_conviction
import uuid

Base.metadata.create_all(bind=engine)
app = FastAPI(title="OfficeAI-500 Sovereign Mesh")

@app.get('/health')
def health(): return {"status": "ok"}

@app.get('/agents')
def agents(db: Session = Depends(get_db)): return [a.__dict__ for a in db.query(Agent).all()]

@app.get('/tasks')
def tasks(limit: int = 50, db: Session = Depends(get_db)): return [t.__dict__ for t in db.query(Task).order_by(Task.id.desc()).limit(limit).all()]

@app.get('/tasks/{task_id}')
def task(task_id: int, db: Session = Depends(get_db)):
    t = db.query(Task).filter(Task.id == task_id).first()
    if not t: raise HTTPException(404, "not found")
    return t.__dict__

@app.post('/mesh/dispatch')
def dispatch(task_in: TaskInput, db: Session = Depends(get_db)):
    task = Task(type=task_in.type, payload=str(task_in.payload), amount=task_in.amount, priority=task_in.priority)
    db.add(task); db.commit(); db.refresh(task)
    return process_task(db, task)

@app.post('/mesh/batch')
def batch(body: BatchInput, db: Session = Depends(get_db)):
    out=[]
    for ti in body.tasks:
        task = Task(type=ti.type, payload=str(ti.payload), amount=ti.amount, priority=ti.priority)
        db.add(task); db.commit(); db.refresh(task)
        out.append(process_task(db, task))
    return {"results": out}

@app.post('/demo/load')
def load_demo(db: Session = Depends(get_db)):
    ensure_agents(db, 500)
    return {"agents_loaded": db.query(Agent).count()}

@app.post('/demo/run_500')
def run_500(db: Session = Depends(get_db)):
    ensure_agents(db, 500)
    tasks = stable_tasks(); results=[]
    for ti in tasks:
        task = Task(type=ti.type, payload=str(ti.payload), amount=ti.amount, priority=ti.priority)
        db.add(task); db.commit(); db.refresh(task)
        results.append(process_task(db, task))
    completed = sum(1 for r in results if r['status']=='completed')
    needs_review = sum(1 for r in results if r['status']=='needs_review')
    failed = sum(1 for r in results if r['status']=='failed')
    hits = sum(1 for r in results if r['memory_hit'])
    misses = len(results)-hits
    total_latency = sum(r['latency_ms'] for r in results)
    savings = hits * 0.12
    return {"batch_id": str(uuid.uuid4()), "submitted": len(results), "completed": completed, "needs_review": needs_review, "failed": failed, "memory_hits": hits, "memory_misses": misses, "total_latency_ms": total_latency, "average_latency_ms": total_latency/len(results), "estimated_api_savings": round(savings,2)}

@app.get('/audit/{task_id}')
def audit(task_id:int, db: Session=Depends(get_db)):
    traces = db.query(AuditTrace).filter(AuditTrace.task_id==task_id).all()
    return [t.__dict__ for t in traces]

@app.get('/memory/search')
def mem_search(q:str="", db: Session=Depends(get_db)):
    rows = db.query(MemoryCapsule).filter(MemoryCapsule.task_type.contains(q) | MemoryCapsule.result.contains(q)).limit(100).all()
    return [r.__dict__ for r in rows]

@app.post('/memory/{capsule_id}/tamper')
def tamper(capsule_id:str, db:Session=Depends(get_db)):
    c = db.query(MemoryCapsule).filter(MemoryCapsule.capsule_id==capsule_id).first()
    if not c: raise HTTPException(404, "not found")
    c.result = c.result + "::tampered"
    db.commit()
    return {"tampered": True, "capsule_id": capsule_id}

@app.get('/memory/{capsule_id}/verify')
def verify(capsule_id:str, db:Session=Depends(get_db)):
    c = db.query(MemoryCapsule).filter(MemoryCapsule.capsule_id==capsule_id).first()
    if not c: raise HTTPException(404, "not found")
    candidate = eval(db.query(Task).filter(Task.type==c.task_type).first().payload)
    ok = integrity_for(c.task_type, candidate, c.result) == c.integrity_hash
    if not ok:
        c.verified = False
        db.commit()
    return {"capsule_id": capsule_id, "verified": ok}

@app.post('/review/{task_id}/approve')
def approve(task_id:int, db: Session=Depends(get_db)):
    t = db.query(Task).filter(Task.id==task_id).first()
    if not t: raise HTTPException(404, "not found")
    if t.status != "needs_review": raise HTTPException(400, "task not in review")
    payload = eval(t.payload)
    t.status = "completed"
    t.result = t.result or f"approved:{t.type}"
    write_memory(db, t.type, payload, t.result, deterministic_conviction(t.type, str(payload)))
    db.commit()
    return {"task_id": task_id, "status": t.status}

@app.post('/review/{task_id}/reject')
def reject(task_id:int, db: Session=Depends(get_db)):
    t = db.query(Task).filter(Task.id==task_id).first()
    if not t: raise HTTPException(404, "not found")
    if t.status != "needs_review": raise HTTPException(400, "task not in review")
    t.status = "rejected"; db.commit(); return {"task_id": task_id, "status": t.status}

@app.get('/metrics')
def metrics(db: Session=Depends(get_db)):
    tasks = db.query(Task).all()
    agents = db.query(Agent).all()
    hits = db.query(AuditTrace).filter(AuditTrace.memory_hit==True).count()
    misses = db.query(AuditTrace).filter(AuditTrace.memory_hit==False).count()
    current_spend = misses * 0.12
    counts = {s: sum(1 for t in tasks if t.status==s) for s in ["queued","in_progress","completed","needs_review","failed","rejected"]}
    return {"agents_total": len(agents), "agents_idle": sum(1 for a in agents if a.status=="idle"), "agents_busy": sum(1 for a in agents if a.status=="busy"), "tasks_total": len(tasks), **counts, "memory_capsules": db.query(MemoryCapsule).count(), "memory_hits": hits, "memory_misses": misses, "estimated_api_savings": round(hits*0.12,2), "budget_limit": 50000.0, "current_spend": round(current_spend,2)}
