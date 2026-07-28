import pytest

@pytest.fixture
async def authed_client(client):
    await create_and_login_user(client, "username0")

    return client

async def create_and_login_user(client, username, password="ValidPassword1!"):
    await client.post(
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

    response = await client.post(
        "/users/login",
        data={
            "username": username,
            "password": password
        }
    )

    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"

    return client

async def test_root(client):
    response = await client.get("/")
    assert response.status_code == 200

async def test_create_note_successful(authed_client):
    title = "Test Note A"
    content = "This is the body of A"
    response = await authed_client.post(
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
async def test_create_note_missing_fields(authed_client, title, content):

    response = await authed_client.post(
        "/notes",
        json={
            "title": title,
            "content": content
        })


    assert response.status_code == 422

async def test_create_note_unauthenticated(client):

    response = await client.post(
        "/notes",
        json={
            "title": "Test Note B",
            "content": "This is B's body"
        }
    )

    assert response.status_code == 401
    

async def test_get_individual_note(authed_client):

    title = "Test Note C"
    content = "Body of C"

    response = await authed_client.post(
    "/notes",
    json={
        "title": title,
        "content": content
    })

    assert response.status_code == 201, "Note creation failed"

    note_id = response.json()["id"]

    get_response = await authed_client.get(f"/notes/{note_id}")

    assert get_response.status_code == 200, "/GET note failed"

    assert get_response.json()["id"] == note_id
    assert get_response.json()["title"] == title
    assert get_response.json()["content"] == content


async def test_get_invalid_note(authed_client):
    response = await authed_client.get("/notes/019484b2-f300-7000-8000-123456789abc")

    assert response.status_code == 404

async def test_get_note_unauthorized_user(authed_client):

    note_response = await authed_client.post(
    "/notes",
    json={
        "title": "Foo Note",
        "content": "Foo Note's contents"
    })

    assert note_response.status_code == 201, "Note creation failed"

    note_id = note_response.json()["id"]

    await create_and_login_user(authed_client, "username1")

    response = await authed_client.get(f"/notes/{note_id}")

    assert response.status_code == 404

async def test_get_notes(authed_client):
    note_response_a = await authed_client.post(
        "/notes",
        json={
            "title": "Foo Note A", "content": "A's contents"
        }
    )

    assert note_response_a.status_code == 201, "Note initialisation fail"

    note_response_b = await authed_client.post(
        "/notes",
        json={
            "title": "Foo Note B", "content": "B's contents"
        }
    )

    assert note_response_b.status_code == 201, "Note initialisation fail"

    response = await authed_client.get("/notes")

    assert len(response.json()) == 2

    titles = [note["title"] for note in response.json()]
    assert "Foo Note A" in titles
    assert "Foo Note B" in titles

async def test_get_notes_unauthenticated(client):
    response = await client.get("/notes")
    assert response.status_code == 401

async def test_get_notes_unauthorized_user(authed_client):
    await authed_client.post("/notes", json={
        "title": "User0's note",
        "content": "note0 info"
    })

    await create_and_login_user(authed_client, "username1")
    
    await authed_client.post(
        "/notes", 
        json={
            "title": "User1's note", 
            "content": "note1 info"
        }
    )

    response = await authed_client.get("/notes")
    titles = [note["title"] for note in response.json()]

    assert len(response.json()) == 1
    assert "User1's note" in titles
    assert "User0's note" not in titles

async def test_update_note(authed_client):
    create_response = await authed_client.post(
        "/notes",
        json={
            "title": "Incorrect Title",
            "content": "Correct Content"
        }
    )

    assert create_response.status_code == 201, "Failed to initialise note"

    note_id = create_response.json()["id"]

    response = await authed_client.patch(
        f"/notes/{note_id}",
        json={
            "title": "Correct Title"
        }
    )

    assert response.status_code == 200, "Failed to update note"
    assert response.json()["title"] == "Correct Title"
    assert response.json()["content"] == "Correct Content"

    get_response = await authed_client.get(f"/notes/{note_id}")

    assert get_response.status_code == 200, "Note not retrieved by /GET"
    assert get_response.json()["title"] == "Correct Title"
    assert get_response.json()["content"] == "Correct Content"

async def test_update_note_unauthenticated(client):

    response = await client.patch("/notes/019484b2-f300-7000-8000-123456789abc",
        json={
            "title": "Patched Title",
            "content": "Patched Content"
        }
    )
    
    assert response.status_code == 401

async def test_update_note_unauthorized_user(authed_client):

    note_response = await authed_client.post(
        "/notes",
        json={
            "title": "Foo Note",
            "content": "Foo Note's contents"
        }
    )

    assert note_response.status_code == 201, "Note creation failed"

    note_id = note_response.json()["id"]

    await create_and_login_user(authed_client, "username1")

    response = await authed_client.patch(
        f"/notes/{note_id}",
        json={
            "title": "Hacked Title"
        }
    )

    assert response.status_code == 404

async def test_update_invalid_note(authed_client):
    response = await authed_client.patch("/notes/019484b2-f300-7000-8000-123456789abc",
        json={
            "title": "Invalid title",
            "content": "No base content"
        }
    )

    assert response.status_code == 404

async def test_update_note_empty_field(authed_client):
    create_response = await authed_client.post(
        "/notes",
        json={
            "title": "Incorrect Title",
            "content": "Correct Content"
        }
    )

    assert create_response.status_code == 201, "Failed to initialise note"

    note_id = create_response.json()["id"]

    response = await authed_client.patch(
        f"/notes/{note_id}",
        json={"title": ""}
    )
    assert response.status_code == 422

async def test_update_note_no_fields(authed_client):
    create_response = await authed_client.post(
            "/notes",
            json={
                "title": "Incorrect Title",
                "content": "Correct Content"
            }
        )
    
    assert create_response.status_code == 201, "Failed to initialise note"
    
    note_id = create_response.json()["id"]
    
    response = await authed_client.patch(
        f"/notes/{note_id}",
        json={}
    )
    assert response.status_code == 400

async def test_delete_note(authed_client):
    create_response = await authed_client.post(
        "/notes",
        json={
            "title": "Test note",
            "content": "Test note contents"
        }
    )

    assert create_response.status_code == 201, "Failed to initialise note"

    note_id = create_response.json()["id"]

    response = await authed_client.delete(f"/notes/{note_id}")

    assert response.status_code == 204

async def test_delete_note_unauthenticated(client):
    response = await client.delete(f"/notes/019484b2-f300-7000-8000-123456789abc")

    assert response.status_code == 401

async def test_delete_note_unauthorized_user(authed_client):
    note_response = await authed_client.post(
        "/notes",
        json={
            "title": "By User0",
            "content": "Unique note"
        }
    )

    assert note_response.status_code == 201, "Note creation failed"

    note_id = note_response.json()["id"]

    await create_and_login_user(authed_client, "username1")

    response = await authed_client.delete(f"/notes/{note_id}")

    assert response.status_code == 404