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

def test_too_short_username(client):
    response = client.post(
        url="/users/register",
        json={
            "username": "fo",
            "password": "testPassword1!",
            "name": {
                "fname": "testFirstname",
                "sname": "testSurname"
                }
            }
    )

    assert "at least 3" in response.json()['detail'][0]['msg']
    assert response.status_code == 422

def test_too_short_password(client):
    response = client.post(
        url="/users/register",
        json={
            "username": "testuser2",
            "password": "3",
            "name": {
                "fname": "testFirstname",
                "sname": "testSurname"
                }
            }
    )

    assert "at least 8" in response.json()['detail'][0]['msg']
    assert response.status_code == 422

def test_too_long_password(client):
    response = client.post(
        url="/users/register",
        json={
            "username": "testuser2",
            "password": "Aa" * 65,
            "name": {
                "fname": "testFirstname",
                "sname": "testSurname"
                }
            }
    )

    assert "at most 128" in response.json()['detail'][0]['msg']
    assert response.status_code == 422

def test_missing_number_password(client):
    response = client.post(
        url="/users/register",
        json={
            "username": "testuser2",
            "password": "testPassword",
            "name": {
                "fname": "testFirstname",
                "sname": "testSurname"
                }
            }
    )

    assert "must contain at least 1 number" in response.json()['detail'][0]['msg']
    assert response.status_code == 422

def test_missing_uppercase_letter_password(client):
    response = client.post(
        url="/users/register",
        json={
            "username": "testuser3",
            "password": "testpassword2",
            "name": {
                "fname": "testFirstname",
                "sname": "testSurname"
                }
            }
    )

    assert "must contain at least one uppercase" in response.json()['detail'][0]['msg']
    assert response.status_code == 422
    
def test_missing_lowercase_letter_password(client):
    response = client.post(
        url="/users/register",
        json={
            "username": "testuser4",
            "password": "CAPSTEST1",
            "name": {
                "fname": "testFirstname",
                "sname": "testSurname"
                }
            }
    )

    assert "must contain at least one lowercase" in response.json()['detail'][0]['msg']
    assert response.status_code == 422
    
def test_missing_special_character_password(client):
    response = client.post(
        url="/users/register",
        json={
            "username": "testuser4",
            "password": "missingSPECIALchar1",
            "name": {
                "fname": "testFirstname",
                "sname": "testSurname"
                }
            }
    )

    assert "must contain at least one special character" in response.json()['detail'][0]['msg']
    assert response.status_code == 422

def test_missing_space_password(client):
    response = client.post(
        url="/users/register",
        json={
            "username": "testuser4",
            "password": "testW1TH sp@ce",
            "name": {
                "fname": "testFirstname",
                "sname": "testSurname"
                }
            }
    )

    assert response.status_code == 422
    assert "must not contain spaces" in response.json()['detail'][0]['msg']