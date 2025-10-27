import botocore.session
from botocore.awsrequest import AWSRequest
from botocore.httpsession import URLLib3Session
import json

# Your bearer token and endpoint
bearer_token = "ABSKQmVkcm9ja0FQSUtleS1ibjRnLWF0LTk5MjM4MjcwODM3Nzo5OGJaMEsyckdCUUJ6Z09MeWczZGUwSS84cHg4RFpQanlpRjBlUUVDOVpNMjVHSko4MXNlaG1lY1pkcz0="
region = "us-east-1"
model_id = "anthropic.claude-3-haiku:1"
endpoint = f"https://bedrock-runtime.{region}.amazonaws.com/model/{model_id}/invoke"

# Payload for the model
payload = {
    "prompt": "Explain quantum computing in simple terms.",
    "max_tokens_to_sample": 100,
    "temperature": 0.7
}

# Create a raw HTTP request with the bearer token
request = AWSRequest(
    method="POST",
    url=endpoint,
    headers={
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    },
    data=json.dumps(payload)
)

# Send the request
session = URLLib3Session()
response = session.send(request.prepare())

# Print the response
print(response.text)
