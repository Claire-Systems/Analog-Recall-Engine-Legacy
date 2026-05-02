import json
from hashlib import sha384
from datetime import datetime
from .config import settings
from .models import MemoryCapsule

def normalize_payload(payload):
    return json.dumps(payload, sort_keys=True, separators=(",",":"))

def capsule_id_for(task_type, payload):
    normalized = normalize_payload(payload)
    return sha384(f"{task_type}|{normalized}".encode()).hexdigest()[:32]

def integrity_for(task_type, payload, result):
    normalized = normalize_payload(payload)
    return sha384(f"{settings.SECRET_SALT}|{task_type}|{normalized}|{result}".encode()).hexdigest()

def lookup_memory(db, task_type, payload):
    cid = capsule_id_for(task_type, payload)
    capsule = db.query(MemoryCapsule).filter(MemoryCapsule.capsule_id == cid).first()
    if not capsule or not capsule.verified:
        return None, cid
    expected = integrity_for(task_type, payload, capsule.result)
    if expected != capsule.integrity_hash:
        capsule.verified = False
        db.commit()
        return None, cid
    capsule.use_count += 1
    capsule.last_used_at = datetime.utcnow()
    db.commit()
    db.refresh(capsule)
    return capsule, cid

def write_memory(db, task_type, payload, result, confidence):
    normalized = normalize_payload(payload)
    cid = capsule_id_for(task_type, payload)
    existing = db.query(MemoryCapsule).filter(MemoryCapsule.capsule_id == cid).first()
    if existing and existing.verified:
        return existing
    capsule = MemoryCapsule(
        capsule_id=cid,
        task_type=task_type,
        input_hash=sha384(f"{task_type}|{normalized}".encode()).hexdigest(),
        payload_hash=sha384(normalized.encode()).hexdigest(),
        result=result,
        confidence=confidence,
        integrity_hash=integrity_for(task_type, payload, result),
        verified=True,
    )
    db.merge(capsule)
    db.commit()
    return capsule
