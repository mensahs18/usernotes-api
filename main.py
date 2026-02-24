from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return { "message": "Hello, Users!\n", "users" : "There are users here. Access /users to view them." }

@app.get("/users")
def get_users():
    return {0: "User1", 1 : "User2", 2: "User3"}

@app.get("/users/{user_id}")
def read_users(user_id: int = None, q: str = None):
    users : dict [int : str] = get_users()

    if user_id is not None:
        try:
            return {user_id: users[user_id]}
        except KeyError:
            return "There is no user by that id."

    return users