import requests

response = requests.post(
    "http://localhost:8000/api/v1/query/",
    json={"question": "What's your education background?", "top_k": 8}
)
print(response.json()["answer"])