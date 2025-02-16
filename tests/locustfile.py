from locust import HttpUser, TaskSet, task, between

class MerchTaskSet(TaskSet):
    token = None

    def on_start(self):
        # authenticate user
        response = self.client.post("/api/auth", json={"username": "locustUser", "password": "locustPass"})
        if response.status_code == 200:
            self.token = response.json()["token"]

    @task
    def buy_merch(self):
        if not self.token:
            return
     #buying pen for 10 coins
        self.client.get("/api/buy/pen", headers={"Authorization": f"Bearer {self.token}"})

    @task
    def send_coin(self):
        # sending 5 coins to another user
        if not self.token:
            return
        self.client.post("/api/sendCoin", json={"toUser": "anotherUser", "amount": 5}, headers={"Authorization": f"Bearer {self.token}"})


class MerchLoadTest(HttpUser):
    tasks = [MerchTaskSet]
    wait_time = between(1, 3)