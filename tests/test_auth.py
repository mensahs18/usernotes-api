import pytest
from freezegun import freeze_time
from conftest import get_test_database
from models import User

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


# JWT tests

@pytest.fixture()
def registered_user(client):
    client.post(
        url="/users/register",
        json={
            "username": "testuser0",
            "password": "Valid1!Password",
            "name": {
                "fname": "testFirstname",
                "sname": "testSurname"
            }
        },
    )

def test_valid_token(client, registered_user):
    response = client.post("/users/login", data={
            "username": "testuser0",
            "password": "Valid1!Password"
        })
    token = response.json()["access_token"]

    response = client.get("/users/me", headers={
            "Authorization": f"Bearer {token}"
        })
    
    assert response.status_code == 200

def test_expired_token(client, registered_user):
    with freeze_time("2026-01-01 00:00:00"):
        response = client.post("/users/login", data={
            "username": "testuser0",
            "password": "Valid1!Password"
        })
        token = response.json()["access_token"]

    # Token currently expires after 15 minutes. freeze_time allows manual time manipulation
    with freeze_time("2026-01-01 00:20:00"):
        response = client.get("/users/me", headers={
            "Authorization": f"Bearer {token}"
        })

        assert response.status_code == 401

def test_missing_token(client):
    response = client.get("/users/me")
    assert response.status_code == 401

@pytest.mark.parametrize("bad_token, description", [
    ("completelyinvalidtoken", "malformed"),
    ("abc.def.ghi", "bad structure"),
    ("Bearer falseprefix", "bad prefix"),
    ("kbsajhbyubr8ag38uyy.afbhkjrey83.incorrectsignature", "tampered signature"),
])
def test_invalid_tokens(client, registered_user, bad_token, description):
    response = client.get("/users/me", headers={
        "Authorization": f"Bearer {bad_token}"
    })
    assert response.status_code == 401, description
    
# Hashing tests

def test_password_hashed_in_db(client):
    password = "1!TestPassword"
    username = "testuser"
    client.post(
        url="/users/register",
        json={
            "username": username,
            "password": password,
            "name": {
                "fname": "testFirstname",
                "sname": "testSurname"
            }
        },
    )

    db = next(get_test_database())

    current_user = db.query(User).filter(User.username == username).first()

    assert current_user is not None
    assert current_user.password != password
    assert current_user.password.startswith("$argon2id")
