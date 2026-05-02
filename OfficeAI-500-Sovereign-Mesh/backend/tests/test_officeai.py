from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_works():
    assert client.get('/health').status_code == 200

def test_dispatch_works():
    client.post('/demo/load')
    r = client.post('/mesh/dispatch', json={"type":"GENERAL","payload":{"subject":"x"},"amount":10,"priority":1})
    assert r.status_code == 200
    assert r.json()["status"] in ["completed","needs_review","failed"]

def test_bad_invoice_fails():
    client.post('/demo/load')
    r = client.post('/mesh/dispatch', json={"type":"INVOICE","payload":{"subject":"x"}})
    assert r.json()["status"] == "failed"

def test_email_missing_recipient_fails():
    client.post('/demo/load')
    r = client.post('/mesh/dispatch', json={"type":"EMAIL","payload":{"subject":"x"}})
    assert r.json()["status"] == "failed"

def test_financial_low_confidence_needs_review():
    client.post('/demo/load')
    r = client.post('/mesh/dispatch', json={"type":"FINANCIAL","payload":{"subject":"low"}})
    assert r.json()["status"] == "needs_review"

def test_compliance_needs_review():
    client.post('/demo/load')
    r = client.post('/mesh/dispatch', json={"type":"COMPLIANCE","payload":{"subject":"x"}})
    assert r.json()["status"] == "needs_review"

def test_demo_500_and_second_run_hits():
    client.post('/demo/load')
    first = client.post('/demo/run_500').json()
    second = client.post('/demo/run_500').json()
    assert first["submitted"] == 500
    assert second["memory_hits"] > first["memory_hits"]

def test_tamper_verification_fails():
    client.post('/demo/load')
    client.post('/mesh/dispatch', json={"type":"GENERAL","payload":{"subject":"m"}})
    cap = client.get('/memory/search?q=GENERAL').json()[0]["capsule_id"]
    client.post(f'/memory/{cap}/tamper')
    verify = client.get(f'/memory/{cap}/verify').json()
    assert verify["verified"] is False

def test_tasks_limit_and_metrics():
    r = client.get('/tasks?limit=50')
    assert r.status_code == 200
    m = client.get('/metrics')
    assert m.status_code == 200
    assert 'agents_total' in m.json()
