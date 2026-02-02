import boto3
import os
import json
from dotenv import load_dotenv

load_dotenv()

def check_models():
    print("Checking AWS Bedrock Model Access...")
    print(f"Region: {os.getenv('AWS_REGION', 'us-east-1')}")
    
    try:
        client = boto3.client(
            service_name="bedrock",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        
        response = client.list_foundation_models()
        models = response.get('modelSummaries', [])
        
        print("\nFound models from Anthropic:")
        for m in models:
            if 'anthropic' in m['modelId'].lower():
                print(f"- {m['modelId']} (Status: {m.get('modelLifecycle', {}).get('status', 'Unknown')})")
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    check_models()
