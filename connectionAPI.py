import requests

class Connection:
    def __init__(self):
        self.token = "Your Token here"
        self.URL = "https://api.notion.com/v1/pages"

    def insert(self, data):
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json", "Notion-Version": "2021-05-13"}
        resp = requests.post(self.URL, headers=headers, data=data)

        if resp.status_code != 200:
            print("[ERROR] Status Code not 200... Aborting")
            print(resp.text)
            exit(1)
        else:
            print("[RESULT] API returned SUCCESS!")