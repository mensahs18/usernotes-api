import logging

from locust import HttpUser, between, task
from locust.exception import StopUser

logger = logging.getLogger(__name__)


class NotesAPIUser(HttpUser):
    wait_time = between(1.9, 2.1)

    def on_start(self) -> None:
        payload = {
            "username": "MyUsername",  # credentials used for logging in.
            "password": "MYP@ssw0rd!",  # consistent with the present note
        }

        with self.client.post(
            "/users/login", data=payload, catch_response=True
        ) as response:
            if response.status_code != 200:
                logger.error(
                    f"Login failed with status code {response.status_code} | {response.text}"
                )
                response.failure(
                    f"Login failed with status {response.status_code}. Details: {response.text}"
                )
                raise StopUser()

            token = response.json().get("access_token")
            self.client.headers.update({"Authorization": f"Bearer {token}"})

    @task(7)
    def get_note(self) -> None:
        self.client.get(
            "/notes/01a05ceb-af1a-7fff-baaa-aaaaaaaaaaaa"
        )  # GET a note ID that is already present in BD

    @task(3)
    def create_note(self) -> None:
        self.client.post(
            "/notes",
            json={
                "title": "Performance Test Note",
                "content": "Focusing on core write bottlenecks.",
            },
        )
