class TestClient:
    def __init__(self, account_id, config):
        self.account_id = account_id
        self.config = config

    def schedule(self, image_path, caption):
        print(f"Received in schedule args: {image_path}, {caption}")
        print(f"Provided account_id\n")
        print(self.account_id)
        print(f"Provided config:\n")
        print(self.config)

        return False
