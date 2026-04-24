# ARE Spectacle v2

Governed, append-only local memory runtime with deterministic intent classification, lane discipline, TrailLink provenance, and write-barrier controls.

## Module Tree

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
```

## Durable Schema (Truth Spine)

SQLite tables:
- `durable_records` (append-only authority)
- `trail_edges` (TrailLink graph)
- `session_events` (turn event log)
- `session_state` (current snapshot)

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
