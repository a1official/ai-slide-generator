import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def list_profiles():
    client = boto3.client(
        service_name="bedrock",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    
    try:
        response = client.list_inference_profiles()
        print("INFERENCE PROFILES:")
        for p in response.get('inferenceProfileSummaries', []):
            print(f"- {p['inferenceProfileName']} ({p['inferenceProfileId']}) Status: {p['status']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_profiles()
