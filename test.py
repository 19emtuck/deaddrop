import json
import requests

# create a token

r = requests.post("http://localhost:8000/token")
token = r.json()["token"]

r = requests.post(
    f"http://localhost:8000/{token}", data=json.dumps({"test": "testé"})
)
r = requests.post(
    f"http://localhost:8000/{token}", data=json.dumps({"test": "test"})
)
r = requests.post(
    f"http://localhost:8000/{token}", data=json.dumps({"test": "test"})
)
r = requests.post(
    f"http://localhost:8000/{token}", data=json.dumps({"test": "test"})
)
r = requests.post(
    f"http://localhost:8000/{token}", data=json.dumps({"test": "test"})
)
r = requests.get(f"http://localhost:8000/token/{token}/requests")
response = r.json()
for e in response["data"]:
    print(e)
