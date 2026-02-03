import boto3
import os
import json
from dotenv import load_dotenv

load_dotenv()

def list_all():
    client_b = boto3.client(
        service_name="bedrock",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    
    print("--- MODELS ---")
    resp_m = client_b.list_foundation_models(byOutputModality='TEXT')
    for m in resp_m.get('modelSummaries', []):
        if 'anthropic' in m['modelId'].lower() and 'sonnet' in m['modelId'].lower():
            print(f"Model ID: {m['modelId']}")
            
    print("\n--- PROFILES ---")
    try:
        resp_p = client_b.list_inference_profiles()
        for p in resp_p.get('inferenceProfileSummaries', []):
            if 'anthropic' in p['inferenceProfileId'].lower():
                print(f"Profile ID: {p['inferenceProfileId']} ({p['inferenceProfileName']})")
    except Exception as e:
        print(f"Err: {e}")

if __name__ == "__main__":
    list_all()
