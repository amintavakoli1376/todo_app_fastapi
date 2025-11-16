

def test_login_invalid_data_response_401(annon_client):
    payload = {
        "username": "amintavakoli",
        "password": "amin1376"
    }
    response = annon_client.post("/users/login", json=payload)
    assert response.status_code == 401

    payload = {
        "username": "testuser",
        "password": "amin1376"
    }
    response = annon_client.post("/users/login", json=payload)
    assert response.status_code == 401


def test_login_response_200(annon_client):
    payload = {
        "username": "testuser",
        "password": "12345678"
    }
    response = annon_client.post("/users/login", json=payload)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


def test_register_response_201(annon_client):
    payload = {
        "username": "amintavakoli",
        "password": "amin1376",
        "password_confirm": "amin1376"
    }
    response = annon_client.post("/users/register", json=payload)
    assert response.status_code == 201
