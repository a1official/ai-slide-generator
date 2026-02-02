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

endpoint_name = os.getenv("SAGEMAKER_ENDPOINT_NAME", "wav2lip-endpoint")

print(f"Checking SageMaker endpoint: {endpoint_name}...")

try:
    response = sagemaker.describe_endpoint(EndpointName=endpoint_name)
    status = response["EndpointStatus"]
    print(f"Status: {status}")
    if status == "InService":
        print("✅ The avatar generator (Wav2Lip) is successfully running on SageMaker!")
    else:
        print(f"⚠️ The endpoint exists but its status is: {status}")
except Exception as e:
    print(f"❌ Error or endpoint not found: {e}")
