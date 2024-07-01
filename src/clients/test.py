from models.account import Account


class TestClient:
    account: Account

    def __init__(self, account: Account):
        self.account = account

    def schedule(self, image_path, caption):
        print(f"Received in schedule args: {image_path}, {caption}")
        print(f"Provided account_id\n")
        print(self.account.id)
        print(f"Provided config:\n")
        print(self.account)

        return False
