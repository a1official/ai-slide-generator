import boto3
import os
import json
from dotenv import load_dotenv

load_dotenv()

def probe_models():
    print("PROBING AWS BEDROCK...")
    
    client = boto3.client(
        service_name="bedrock-runtime",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    
    test_ids = [
        "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        "anthropic.claude-3-5-sonnet-20240620-v1:0",
        "us.anthropic.claude-3-5-sonnet-20240620-v1:0",
        "anthropic.claude-3-haiku-20240307-v1:0",
        "us.anthropic.claude-3-haiku-20240307-v1:0",
        "anthropic.claude-3-5-haiku-20241022-v1:0",
        "us.anthropic.claude-3-5-haiku-20241022-v1:0"
    ]
    
    for model_id in test_ids:
        try:
            client.converse(
                modelId=model_id,
                messages=[{"role": "user", "content": [{"text": "hi"}]}],
                inferenceConfig={"maxTokens": 10}
            )
            print(f"SUCCESS: {model_id}")
        except Exception as e:
            err = str(e)
            if "AccessDeniedException" in err:
                print(f"DENIED: {model_id}")
            elif "ValidationException" in err:
                print(f"THROUGHPUT: {model_id}")
            else:
                print(f"ERROR: {model_id} - {err[:30]}")

if __name__ == "__main__":
    probe_models()
