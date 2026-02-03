import os
import boto3
import tarfile
import sagemaker
from sagemaker.pytorch import PyTorchModel
from pathlib import Path
import traceback
import time

# Configuration
ROLE = "arn:aws:iam::690261714719:role/service-role/AmazonSageMaker-ExecutionRole-20251111T125317"
BUCKET = "ai-video-generator-bucket-2026"
REGION = "us-east-1"
ENDPOINT_NAME = "wav2lip-endpoint"

def create_model_tar():
    print("📦 Packaging Wav2Lip model...")
    wav2lip_dir = Path("./Wav2Lip").absolute()
    tar_path = Path("model.tar.gz").absolute()
    
    # Files to exclude from the tarball
    exclude = [".git", "__pycache__", "results", "temp", "outputs", "venv", ".env"]
    
    with tarfile.open(tar_path, "w:gz") as tar:
        for root, dirs, files in os.walk(wav2lip_dir):
            # Skip excluded dirs
            dirs[:] = [d for d in dirs if d not in exclude]
            
            for file in files:
                if file in exclude: continue
                full_path = Path(root) / file
                # Add to tar with relative path from Wav2Lip
                rel_path = full_path.relative_to(wav2lip_dir)
                tar.add(full_path, arcname=str(rel_path))
                
    print(f"✅ Created {tar_path} ({os.path.getsize(tar_path) / 1024 / 1024:.2f} MB)")
    return tar_path

def deploy():
    # Set region explicitly
    os.environ["AWS_DEFAULT_REGION"] = REGION
    session = sagemaker.Session(default_bucket=BUCKET)
    
    # 1. Create tarball
    tar_path = create_model_tar()
    
    # 2. Upload to S3
    print(f"☁️  Uploading model to S3 bucket: {BUCKET}...")
    s3_path = session.upload_data(path=str(tar_path), bucket=BUCKET, key_prefix="sagemaker/wav2lip")
    print(f"✓ Uploaded to: {s3_path}")
    
    # 3. Create PyTorch Model
    # Note: We specify code/sagemaker_entry.py if we put it in code folder, 
    # but since we packaged sagemaker_entry.py at root of model.tar.gz, we use just sagemaker_entry.py
    print("🚀 Creating SageMaker Model...")
    pytorch_model = PyTorchModel(
        model_data=s3_path,
        role=ROLE,
        entry_point="sagemaker_entry.py",
        framework_version="1.13",
        py_version="py39",
        sagemaker_session=session,
        env={"PYTHONUNBUFFERED": "1"}
    )
    
    # 4. Deploy
    print(f"📡 Deploying to endpoint: {ENDPOINT_NAME}...")
    print("⚠️  Note: This usually takes 5-10 minutes.")
    
    # Check if endpoint already exists
    sm_client = boto3.client("sagemaker", region_name=REGION)
    try:
        sm_client.describe_endpoint(EndpointName=ENDPOINT_NAME)
        print(f"🔄 Endpoint {ENDPOINT_NAME} already exists. Updating...")
        update_existing = True
    except:
        update_existing = False

    predictor = pytorch_model.deploy(
        initial_instance_count=1,
        instance_type="ml.g4dn.xlarge", 
        endpoint_name=ENDPOINT_NAME,
        wait=True
    )
    
    print(f"✅ Deployment complete! Endpoint: {ENDPOINT_NAME}")
    return ENDPOINT_NAME

if __name__ == "__main__":
    try:
        deploy()
    except Exception as e:
        print("\n❌ CRITICAL ERROR DURING DEPLOYMENT:")
        traceback.print_exc()
