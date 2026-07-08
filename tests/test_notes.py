import pytest

@pytest.fixture
def authed_client(client):
    create_and_login_user(client, "username0")

    return client

def create_and_login_user(client, username, password="ValidPassword1!"):
    client.post(
        "/users/register",
        json={
            "username": username,
            "password": password,
            "name": {
                "fname": username,
                "sname": "TESTER"
            }
        }
    )

    response = client.post(
        "/users/login",
        data={
            "username": username,
            "password": password
        }
    )

    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"

    return client

def test_create_note_successful(authed_client):
    title = "Test Note A"
    content = "This is the body of A"
    response = authed_client.post(
        "/notes",
        json={
            "title": title,
            "content": content
        })


    assert response.status_code == 201
    assert response.json()["title"] == title
    assert response.json()["content"] == content

@pytest.mark.parametrize("title, content", [
    ("", "titleless content"),
    ("title with no content", ""),
])
def test_create_note_missing_fields(authed_client, title, content):

    response = authed_client.post(
        "/notes",
        json={
            "title": title,
            "content": content
        })


    assert response.status_code == 422

def test_create_note_unauthenticated(client):

    response = client.post(
        "/notes",
        json={
            "title": "Test Note B",
            "content": "This is B's body"
        }
    )

    assert response.status_code == 401
    

def test_get_individual_note(authed_client):

    title = "Test Note C"
    content = "Body of C"

    response = authed_client.post(
    "/notes",
    json={
        "title": title,
        "content": content
    })

    assert response.status_code == 201, "Note creation failed"

    note_id = response.json()["id"]

    get_response = authed_client.get(f"/notes/{note_id}")

    assert get_response.status_code == 200, "/GET note failed"

    assert get_response.json()["id"] == note_id
    assert get_response.json()["title"] == title
    assert get_response.json()["content"] == content


def test_get_invalid_note(authed_client):
    response = authed_client.get("/notes/1")

    assert response.status_code == 404
