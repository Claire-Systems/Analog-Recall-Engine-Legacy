from hashlib import sha256

VALID_TYPES = {"GENERAL","EMAIL","SUPPORT","REPORT","RESEARCH","COMPLIANCE","FINANCIAL","INVOICE","PAYMENT_EXCEPTION"}

def deterministic_conviction(task_type: str, payload: str) -> float:
    h = sha256(f"{task_type}|{payload}".encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF

def apply_governance(task_type: str, payload: dict, amount: float):
    if task_type not in VALID_TYPES:
        return False, "failed", "high", "unknown task type"
    if not payload:
        return False, "failed", "high", "empty payload"
    if task_type == "INVOICE" and not payload.get("vendor"):
        return False, "failed", "high", "missing vendor"
    if task_type == "EMAIL" and not payload.get("recipient"):
        return False, "failed", "high", "missing recipient"
    if task_type == "COMPLIANCE":
        return False, "needs_review", "medium", "compliance review required"
    if task_type == "PAYMENT_EXCEPTION" and amount > 5000:
        return False, "needs_review", "high", "high amount payment exception"
    if task_type == "FINANCIAL":
        c = deterministic_conviction(task_type, str(payload))
        if c < 0.95:
            return False, "needs_review", "medium", f"low conviction {c:.4f}"
    return True, "completed", "low", "policy pass"
