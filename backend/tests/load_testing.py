from locust import HttpUser, task, between, events
import random
import string

class URLShortenerUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Действие при запуске каждого нового пользователя"""
        random_url = f"https://example.com/{''.join(random.choices(string.ascii_lowercase, k=10))}"
        self.target_url = random_url
        self.created_slug = None

    @task(3) 
    def shorten_url(self):
        """Тестируем эндпоинт создания короткой ссылки"""
        payload = {"url": self.target_url}
        with self.client.post("/api/shorten", json=payload, catch_response=True) as response:
            if response.status_code == 201:
                self.created_slug = response.json()["data"]["slug"]
            elif response.status_code == 409:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task(6)
    def redirect_to_url(self):
        """Тестируем редирект по уже созданному slug"""
        if self.created_slug:
            with self.client.get(f"/api/{self.created_slug}", allow_redirects=False, catch_response=True) as response:
                if response.status_code == 302:
                    response.success()
                else:
                    response.failure(f"Expected 302, got {response.status_code}")