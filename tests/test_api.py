import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "database" in data

def test_schema_endpoint():
    response = client.get("/schema")
    assert response.status_code == 200
    data = response.json()
    assert "tables" in data
    table_names = [t["table_name"] for t in data["tables"]]
    assert "users" in table_names
    assert "orders" in table_names
    assert "products" in table_names
    assert "payments" in table_names

def test_query_endpoint_valid():
    payload = {"question": "Show me users who registered this month"}
    response = client.post("/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "sql" in data
    assert "explanation" in data
    assert "columns" in data
    assert "rows" in data
    assert isinstance(data["rows"], list)

def test_query_endpoint_security_rejection():
    payload = {"question": "Delete all users from the database"}
    response = client.post("/query", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data

def test_explain_endpoint():
    payload = {"sql": "SELECT * FROM users"}
    response = client.post("/explain", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_safe"] is True
    assert "explanation" in data
