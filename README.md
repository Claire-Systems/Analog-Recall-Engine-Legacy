# ARE Spectacle v2

Governed, append-only local memory runtime with deterministic intent classification, lane discipline, TrailLink provenance, and write-barrier controls.

## Proposed Module Tree

```text
app/
  api/routes.py
  core/turn_engine.py
  domain/types.py
  services/
    intake.py
    intent_classifier.py
    lane_router.py
    recall_service.py
    relevance_gate.py
    answer_planner.py
    contradiction_checker.py
    sentinel.py
    lycanthrope.py
    write_barrier.py
    gyro_are.py
    recognition_rail.py
    visor_builder.py
    traillink.py
  storage/
    sqlite_store.py
    session_store.py
    gravel_store.py
  tracing/veritas.py
  main.py
tests/test_turn_flow.py
requirements.txt
```

## Durable Schema (Truth Spine)

SQLite tables:
- `durable_records` (append-only authority)
- `trail_edges` (TrailLink graph)
- `session_events` (turn event log)
- `session_state` (current snapshot)

All durable record rows include record metadata such as `record_id`, `record_kind`, `created_at`, canonical payload fields, lane tags, policy status, parent/supersession links, and hash/trace/session identifiers.

## Turn Flow

1. **prepare_turn**: session_event append → classify → lane route → gyro orient.
2. **execute_turn**: recall candidates from allowed lanes → relevance gate → answer plan → visor/rail payload → contradiction check.
3. **finalize_turn**: Sentinel + Lycanthrope governance → WriteBarrier durable commits → TrailLink edges → session snapshot update → Gravel artifact update.

## API Endpoints

- `GET /health`
- `POST /ingest`
- `POST /query`
- `GET /gyro`
- `POST /prompt-prefix`
- `GET /trace/{id}`
- `GET /report/{id}`

## Migration Plan From Legacy Runtime

1. Keep externally useful API surface (`/health`, `/ingest`, `/query`, `/gyro`, tracing/report endpoints).
2. Move canonical truth to SQLite append-only `durable_records` with write-barrier enforcement.
3. Split session event/state from durable truth commits.
4. Add deterministic intent/lane routing and relevance gating before recall-to-context handoff.
5. Rebuild secondary artifacts in Gravel from Truth Spine + TrailLink + trace data.

## Preserved vs Replaced

Preserved:
- FastAPI service boundary and endpoint style.
- Gyro orientation concept and trace/report observability.
- Prompt-prefix / visor envelope concept.

Replaced:
- JSONL-style authority assumptions with SQLite append-only authority.
- Weak retrieval flow with lane-disciplined routing + relevance gate.
- Uncontrolled memory writes with Sentinel/Lycanthrope mediated write barrier.

## Run and Test

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

```bash
pytest
```
