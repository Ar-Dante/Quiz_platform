from starlette import status


def test_create_user(client):
    user_data = {
        "user_email": "tq1e1st@example.com",
        "user_firstname": "John",
        "user_lastname": "Doe",
        "hashed_password": "hashed_password_here",
    }

    response = client.post("/users/SingUp", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    created_user = response.json()
    assert "user_id" in created_user
    assert created_user["user_firstname"] == user_data["user_firstname"]
    assert created_user["user_lastname"] == user_data["user_lastname"]


def test_get_users(client):
    response = client.get("/users/")
    assert response.status_code == status.HTTP_200_OK
    users_list = response.json()

    assert isinstance(users_list, list)
    assert len(users_list) > 0

    user = users_list[0]
    assert "user_id" in user
    assert "user_firstname" in user
    assert "user_lastname" in user


def test_read_user(client):
    user_id = 8
    response = client.get(f"/users/{user_id}")
    assert response.status_code == status.HTTP_200_OK
    user_detail = response.json()

    assert "user_id" in user_detail
    assert "user_firstname" in user_detail
    assert "user_lastname" in user_detail

    assert user_detail["user_id"] == user_id


def test_update_user(client):
    user_id = 14
    updated_user_data = {
        "user_email": "update@gmail.com",
        "user_firstname": "update_firstname",
        "user_lastname": "update_lastname",
        "user_city": "update_sity",
        "user_phone": "123456"
    }

    response = client.put(f"/users/{user_id}", json=updated_user_data)
    assert response.status_code == status.HTTP_200_OK
    updated_user = response.json()
    assert updated_user["user_firstname"] == updated_user_data["user_firstname"]
    assert updated_user["user_lastname"] == updated_user_data["user_lastname"]
    assert updated_user["user_email"] == updated_user_data["user_email"]
    assert updated_user["user_city"] == updated_user_data["user_city"]
    assert updated_user["user_phone"] == updated_user_data["user_phone"]


def test_delete_user(client):
    user_id = 16

    response = client.delete(f"/users/{user_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
