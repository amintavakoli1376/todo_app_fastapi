from locust import HttpUser, task, between


class QuickstartUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        response = self.client.post("/users/login",json={
            "username": "amintavakoli",
            "password": "amin1376"
        })
        access_token = response.json()["access_token"]
        self.client.headers = {"Authorization": f"Bearer {access_token}"}


    @task
    def tasks_list(self):
        self.client.get("/tasks")

    @task
    def initial_task(self):
        self.client.get("/initiate-task")

    @task
    def fetch_current_weather(self):
        self.client.get("/fetch-current-weather")

    @task
    def not_found(self):
        self.client.get("/not-found")
