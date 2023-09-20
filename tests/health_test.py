def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data == {"status_code": 200, "detail": "ok", "result": "working"}
