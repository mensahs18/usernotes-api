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
    
    
