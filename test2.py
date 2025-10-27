import boto3
from botocore.exceptions import ClientError

# Create a Bedrock runtime client
bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')

# Define the model ID
model_id = 'us.anthropic.claude-sonnet-4-5-20250929-v1:0'

try:
    # Invoke the model using converse API
    response = bedrock.converse(
        modelId=model_id,
        messages=[
            {
                "role": "user",
                "content": [
                    {"text": "Explain quantum computing in simple terms."}
                ]
            }
        ],
        inferenceConfig={
            "maxTokens": 100,
            "temperature": 0.7
        }
    )
    
    # Extract and print the response
    response_text = response['output']['message']['content'][0]['text']
    print(response_text)
    
    # Optional: Print full response for debugging
    # print("\nFull response:")
    # print(json.dumps(response, indent=2, default=str))
    
except ClientError as e:
    print(f"Error invoking model: {e}")