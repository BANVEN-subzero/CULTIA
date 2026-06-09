
import requests

url = "http://localhost:5000/api/chat"
data = {"message": "Tell me about the Mankon people"}
response = requests.post(url, json=data)

print("Status Code:", response.status_code)
print("Response JSON:", response.json())
