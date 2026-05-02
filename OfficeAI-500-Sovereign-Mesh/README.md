# OfficeAI-500-Sovereign-Mesh

OfficeAI-500 Sovereign Mesh is an enterprise task-orchestration MVP that simulates a 500-agent virtual office for operations and finops workflows. It is a governed execution kernel with durable storage, deterministic memory reuse, review gates, tamper checks, and auditable traces.

## Not a chatbot / not plain RAG
This system routes structured tasks through governance, memory integrity checks, and review queues. It processes operational work units, not free-form assistant dialog.

## Run backend
```bash
cd backend
pip install -r requirements.txt
python run.py
```

## Run frontend
```bash
cd frontend
npm install
npm run dev
```

## Run tests
```bash
cd backend
pytest
```

## Run 500 demo
```bash
curl -X POST http://localhost:8000/demo/load
curl -X POST http://localhost:8000/demo/run_500
curl -X POST http://localhost:8000/demo/run_500
```
Second run should show increased `memory_hits` and reduced `memory_misses`.

## Tamper detection
1. Find a capsule via `/memory/search?q=`.
2. Tamper with `POST /memory/{capsule_id}/tamper`.
3. Verify with `GET /memory/{capsule_id}/verify`.
4. Failed verification marks capsule `verified=false` and prevents reuse.

## Enterprise office / finops mapping
- **Agents** = virtual back-office workers.
- **Tasks** = invoices, support tickets, reports, exceptions.
- **Governance** = policy and risk controls.
- **Review queue** = human checkpoint on risky/regulated work.
- **Memory capsules** = deterministic reuse for repeat workflows and spend reduction.
- **Audit traces** = compliance and incident visibility.
