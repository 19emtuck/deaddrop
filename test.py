import json
import requests

# create a token

r = requests.get("http://localhost:8000/token")
token = r.json()["token"]

r = requests.post(
    f"http://localhost:8000/drop/{token}", data=json.dumps({"test": "testé"})
)
r = requests.post(
    f"http://localhost:8000/drop/{token}", data=json.dumps({"test": "test"})
)
r = requests.post(
    f"http://localhost:8000/drop/{token}", data=json.dumps({"test": "test"})
)
r = requests.post(
    f"http://localhost:8000/drop/{token}", data=json.dumps({"test": "test"})
)
r = requests.post(
    f"http://localhost:8000/drop/{token}", data=json.dumps({"test": "test"})
)
r = requests.get(f"http://localhost:8000/display/{token}")
response = r.json()
for e in response:
    print(e)
