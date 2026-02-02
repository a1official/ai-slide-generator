import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def list_arns():
    client = boto3.client(
        service_name="bedrock",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    
    print("MODELS & ARNS:")
    resp = client.list_foundation_models()
    for m in resp.get('modelSummaries', []):
        if 'anthropic' in m['modelId'].lower() and 'sonnet' in m['modelId'].lower() and '3-5' in m['modelId']:
            print(f"ID: {m['modelId']}")
            print(f"ARN: {m['modelArn']}")
    
    print("\nPROFILES & ARNS:")
    resp_p = client.list_inference_profiles()
    for p in resp_p.get('inferenceProfileSummaries', []):
        if 'anthropic' in p['inferenceProfileId'].lower() and '3-5' in p['inferenceProfileId']:
            print(f"ID: {p['inferenceProfileId']}")
            print(f"ARN: {p['inferenceProfileArn']}")

if __name__ == "__main__":
    list_arns()
