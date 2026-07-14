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

def test_root(client):
    assert client.get("/").status_code == 200

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
    response = authed_client.get("/notes/019484b2-f300-7000-8000-123456789abc")

    assert response.status_code == 404

def test_get_note_unauthorized_user(authed_client):

    note_response = authed_client.post(
    "/notes",
    json={
        "title": "Foo Note",
        "content": "Foo Note's contents"
    })

    assert note_response.status_code == 201, "Note creation failed"

    note_id = note_response.json()["id"]

    create_and_login_user(authed_client, "username1")

    response = authed_client.get(f"/notes/{note_id}")

    assert response.status_code == 404

def test_get_notes(authed_client):
    note_response_a = authed_client.post(
        "/notes",
        json={
            "title": "Foo Note A", "content": "A's contents"
        }
    )

    assert note_response_a.status_code == 201, "Note initialisation fail"

    note_response_b = authed_client.post(
        "/notes",
        json={
            "title": "Foo Note B", "content": "B's contents"
        }
    )

    assert note_response_b.status_code == 201, "Note initialisation fail"

    response = authed_client.get("/notes")

    assert len(response.json()) == 2

    titles = [note["title"] for note in response.json()]
    assert "Foo Note A" in titles
    assert "Foo Note B" in titles

def test_get_notes_unauthenticated(client):
    response = client.get("/notes")
    assert response.status_code == 401

def test_get_notes_unauthorized_user(authed_client):
    authed_client.post("/notes", json={
        "title": "User0's note",
        "content": "note0 info"
    })

    create_and_login_user(authed_client, "username1")
    
    authed_client.post(
        "/notes", 
        json={
            "title": "User1's note", 
            "content": "note1 info"
        }
    )

    response = authed_client.get("/notes")
    titles = [note["title"] for note in response.json()]

    assert len(response.json()) == 1
    assert "User1's note" in titles
    assert "User0's note" not in titles

def test_update_note(authed_client):
    create_response = authed_client.post(
        "/notes",
        json={
            "title": "Incorrect Title",
            "content": "Correct Content"
        }
    )

    assert create_response.status_code == 201, "Failed to initialise note"

    note_id = create_response.json()["id"]

    response = authed_client.patch(
        f"/notes/{note_id}",
        json={
            "title": "Correct Title"
        }
    )

    assert response.status_code == 200, "Failed to update note"
    assert response.json()["title"] == "Correct Title"
    assert response.json()["content"] == "Correct Content"

    get_response = authed_client.get(f"/notes/{note_id}")

    assert get_response.status_code == 200, "Note not retrieved by /GET"
    assert get_response.json()["title"] == "Correct Title"
    assert get_response.json()["content"] == "Correct Content"

def test_update_note_unauthenticated(client):

    response = client.patch("/notes/019484b2-f300-7000-8000-123456789abc",
        json={
            "title": "Patched Title",
            "content": "Patched Content"
        }
    )
    
    assert response.status_code == 401

def test_update_note_unauthorized_user(authed_client):

    note_response = authed_client.post(
        "/notes",
        json={
            "title": "Foo Note",
            "content": "Foo Note's contents"
        }
    )

    assert note_response.status_code == 201, "Note creation failed"

    note_id = note_response.json()["id"]

    create_and_login_user(authed_client, "username1")

    response = authed_client.patch(
        f"/notes/{note_id}",
        json={
            "title": "Hacked Title"
        }
    )

    assert response.status_code == 404

def test_update_invalid_note(authed_client):
    response = authed_client.patch("/notes/019484b2-f300-7000-8000-123456789abc",
        json={
            "title": "Invalid title",
            "content": "No base content"
        }
    )

    assert response.status_code == 404

def test_delete_note(authed_client):
    create_response = authed_client.post(
        "/notes",
        json={
            "title": "Test note",
            "content": "Test note contents"
        }
    )

    assert create_response.status_code == 201, "Failed to initialise note"

    note_id = create_response.json()["id"]

    response = authed_client.delete(f"/notes/{note_id}")

    assert response.status_code == 204

def test_delete_note_unauthenticated(client):
    response = client.delete(f"/notes/019484b2-f300-7000-8000-123456789abc")

    assert response.status_code == 401

def test_delete_note_unauthorized_user(authed_client):
    note_response = authed_client.post(
        "/notes",
        json={
            "title": "By User0",
            "content": "Unique note"
        }
    )

    assert note_response.status_code == 201, "Note creation failed"

    note_id = note_response.json()["id"]

    create_and_login_user(authed_client, "username1")

    response = authed_client.delete(f"/notes/{note_id}")

    assert response.status_code == 404