import pytest

# Registration tests
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

def test_register_missing_username(client):
    response = client.post(
        url="/users/register",
        json={
            "password": "1!TestPassword",
            "name": {
                "fname": "testFirstname",
                "sname": "testSurname"
            }
        },
    )

    assert response.status_code == 422

def test_register_missing_name_fields(client):
    response = client.post(
        url="/users/register",
        json={
            "username": "testuser1",
            "password": "1!TestPassword",
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize("login_payload", [
    {"username": 4, "password": "valid_Password1!", "name": {"fname": "John", "sname": "Smith"}},
    {"username": "valid_user", "password": ["array", "for", "pw"], "name": {"fname": "John", "sname": "Smith"}},
    {"username": "valid_user", "password": "valid_Password1!", "name": {"fname": 4.5, "sname": "Smith"}},
    {"username": "valid_user", "password": "valid_Password1!", "name": {"fname": "John", "sname": True}},
    
])
def test_register_incorrect_data_types(client, login_payload):
    response = client.post(
        url="/users/register",
        json=login_payload
    )

    assert response.status_code == 422
    assert "valid string" in response.json()['detail'][0]['msg']



@pytest.mark.parametrize("username, expected_message", [
    ("", "at least 3"),
    ("fo", "at least 3")
])
def test_register_username_validation(client, username, expected_message):
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

@pytest.mark.parametrize("malicious_input", [
    "' OR '1'='1",
    "'; DROP TABLE users; --",
    "' OR 1=1 --",
    "\\",
    "' UNION SELECT * FROM users --",
    "A" * 10000,
    "%s%s%s%s"
])
def test_malicious_registration(client, malicious_input):
    response = client.post(
        url="/users/register",
        json={
            "username": malicious_input,
            "password": "1!TestPassword",
            "name": {
                "fname": "testFirstname",
                "sname": "testSurname"
            }
        },
    )

    assert response.status_code != 500


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

# Login tests

def test_login(client):
    client.post(
        url="/users/register",
        json={
            "username": "testuser2",
            "password": "2!TestPassword",
            "name": {
                "fname": "testFirstname",
                "sname": "testSurname"
            }
        },
    )

    response = client.post(
        url="/users/login",
        data={
            "username": "testuser2",
            "password": "2!TestPassword"
        }
    )

    assert response.status_code == 200
    assert response.json()["access_token"]

@pytest.mark.parametrize("username, password", [
    ("correctuser", "1!Falsepassword"),
    ("correctuser", "falsepassword"),
    ("falseuser", "1!CorrectPassword"),
])
def test_login_validation(client, username, password):
    client.post(
        url="/users/register",
        json={
            "username": "correctuser",
            "password": "1!CorrectPassword",
            "name": {
                "fname": "testFirstname",
                "sname": "testSurname"
            }
        },
    )

    response = client.post(
        url="/users/login",
        data={
            "username": username,
            "password": password
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials."

@pytest.mark.parametrize("username, password", [
    ("", ""),
    ("", "1!CorrectPassword"),
    ("correctuser", "")
])
def test_empty_login_fields(client, username, password):
    client.post(
    url="/users/register",
        json={
            "username": "correctuser",
            "password": "1!CorrectPassword",
            "name": {
                "fname": "testFirstname",
                "sname": "testSurname"
            }
    },
)

    response = client.post(
        url="/users/login",
        data={
            "username": username,
            "password": password
        }
    )

    assert response.status_code == 422


def test_login_json(client):
    client.post(
        url="/users/register",
        json={
            "username": "jsonuser",
            "password": "3!TestPassword",
            "name": {
                "fname": "testFirstname",
                "sname": "testSurname"
            }
        },
    )

    response = client.post(
        url="/users/login",
        json={
            "username": "jsonuser",
            "password": "3!TestPassword"
        }
    )

    assert response.status_code == 422

@pytest.mark.parametrize("malicious_input", [
    "' OR '1'='1",
    "'; DROP TABLE users; --",
    "' OR 1=1 --",
    "\\",
    "' UNION SELECT * FROM users --",
    "%s%s%s%s"
])
def test_malicious_login(client, malicious_input):
    response = client.post(
        url="/users/login",
        data={
            "username": malicious_input,
            "password": malicious_input
        },
    )

    assert response.status_code in [401,422]