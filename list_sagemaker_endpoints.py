import boto3
import os
from dotenv import load_dotenv

load_dotenv()

sagemaker = boto3.client(
    "sagemaker",
    region_name=os.getenv("AWS_REGION", "us-east-1"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

print(f"Listing SageMaker endpoints in region: {os.getenv('AWS_REGION', 'us-east-1')}...")

try:
    response = sagemaker.list_endpoints()
    endpoints = response.get("Endpoints", [])
    if not endpoints:
        print("No endpoints found.")
    for ep in endpoints:
        print(f"- {ep['EndpointName']} ({ep['EndpointStatus']})")
except Exception as e:
    print(f"❌ Error: {e}")
