import requests
import json

# Use the inference profile instead of direct model ID
endpoint = "https://bedrock-runtime.us-east-1.amazonaws.com/model/us.anthropic.claude-3-5-sonnet-20241022-v2:0/invoke"


payload = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 100,
    "temperature": 0.7,
    "messages": [
        {
            "role": "user",
            "content": "Explain quantum computing in simple terms."
        }
    ]
}

headers = {
    "Authorization": f"Bearer {bearer_token}",
    "Content-Type": "application/json"
}

try:
    response = requests.post(
        endpoint,
        headers=headers,
        data=json.dumps(payload)
    )
    response.raise_for_status()
    data = response.json()
    print("Response from Bedrock:", data)
except requests.exceptions.RequestException as error:
    print("Error calling Bedrock:", error)
    if hasattr(error.response, 'text'):
        print("Response body:", error.response.text)
