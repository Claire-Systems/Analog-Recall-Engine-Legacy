from pydantic import BaseModel
from typing import Any

class TaskInput(BaseModel):
    type: str
    payload: Any
    amount: float = 0.0
    priority: int = 1

class BatchInput(BaseModel):
    tasks: list[TaskInput]
