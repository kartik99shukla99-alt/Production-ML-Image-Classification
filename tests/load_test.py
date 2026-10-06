from pathlib import Path

from locust import HttpUser, between, task


IMAGE_PATH = Path(__file__).parent / "test_images" / "test.jpg"


class ImageClassificationUser(HttpUser):
    wait_time = between(0.5, 1)

    @task
    def classify_image(self):
        with IMAGE_PATH.open("rb") as image:
            with self.client.post(
                "/v1/predictions",
                files={
                    "file": (
                        "test.jpg",
                        image,
                        "image/jpeg",
                    )
                },
                name="/v1/predictions",
                catch_response=True,
            ) as response:
                if response.status_code != 202:
                    response.failure(
                        f"Unexpected status: {response.status_code}"
                    )
