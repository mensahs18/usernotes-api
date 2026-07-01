import pytest

@pytest.fixture
def authed_client(client):
    client.post(
        "/users/register",
        json={
            "username": "notesuser0",
            "password": "0!NotePassword",
            "name": {
                "fname": "Tester",
                "sname": "Zero"
            }
        }
    )

    response = client.post(
        "/users/login",
        data={
            "username": "notesuser0",
            "password": "0!NotePassword"
        }
    )

    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"

    return client
