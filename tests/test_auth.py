import pytest

def test_register(client):
    response = client.post(
        url="/users/register",
        json={
            "username": "testuser1",
            "password": "1!TestPassword",
            "name": {
                "fname": "testFirstname",
                "sname": "testSurname"
            }
        },
    )

    assert response.status_code == 201

def test_duplicate_username(client):
    client.post(
        url="/users/register",
        json={
            "username": "testuserA",
            "password": "1!TestPassword",
            "name": {
                "fname": "testFirstname",
                "sname": "testSurname"
            }
        }
    )

    response = client.post(
        url="/users/register",
        json={
            "username": "testuserA",
            "password": "1!TestPassword",
            "name": {
                "fname": "testFirstname",
                "sname": "testSurname"
            }
        }
    )

    assert response.status_code == 409

@pytest.mark.parametrize("username, expected_message", [
    ("fo", "at least 3")
])
def test_username_validation(client, username, expected_message):
    response = client.post(
        url="/users/register",
        json={
            "username": username,
            "password": "testPassword1!",
            "name": {
                "fname": "testFirstname",
                "sname": "testSurname"
                }
            }
    )

    assert expected_message in response.json()['detail'][0]['msg']
    assert response.status_code == 422

@pytest.mark.parametrize("password, expected_message", [
    ("Short!", "at least 8"),
    ("Aa" * 65, "at most 128"),
    ("testPassword", "must contain at least 1 number"),
    ("testpassword2", "must contain at least one uppercase"),
    ("CAPSTEST1", "must contain at least one lowercase"),
    ("missingSPECIALchar1", "must contain at least one special character"),
    ("testW1TH sp@ce", "must not contain spaces")
])
def test_password_validation(client, password, expected_message):
    response = client.post(
        url="/users/register",
        json={
            "username": "testuser2",
            "password": password,
            "name": {
                "fname": "testFirstname",
                "sname": "testSurname"
            }
        }
    )

    assert response.status_code == 422
    assert expected_message in response.json()['detail'][0]['msg']