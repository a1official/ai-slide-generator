import boto3
import os
import json
from dotenv import load_dotenv

load_dotenv()

def debug_last_job():
    client = boto3.client(
        'mediaconvert',
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    
    # Get regional endpoint
    response = client.describe_endpoints(MaxResults=1)
    endpoint = response['Endpoints'][0]['Url']
    
    client = boto3.client(
        'mediaconvert',
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        endpoint_url=endpoint,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    
    # List last 5 jobs
    response = client.list_jobs(MaxResults=5, Order='DESCENDING')
    jobs = response['Jobs']
    
    print(f"Found {len(jobs)} recent jobs.")
    
    for job in jobs:
        print(f"\n--- Job ID: {job['Id']} ---")
        print(f"Status: {job['Status']}")
        
        # Check for OutputGroupDetails
        if 'OutputGroupDetails' in job:
            ogd = job['OutputGroupDetails']
            print(f"OutputGroupDetails Found! Length: {len(ogd)}")
            # Print a clean version of the structure
            for i, group in enumerate(ogd):
                print(f"  Group {i} Details:")
                if 'OutputDetails' in group:
                    for j, output in enumerate(group['OutputDetails']):
                        print(f"    Output {j} OutputFilePaths: {output.get('OutputFilePaths')}")
        else:
            print("OutputGroupDetails NOT FOUND in job summary.")
            
        # If complete, let's get the full job detail
        if job['Status'] == 'COMPLETE':
            full_job = client.get_job(Id=job['Id'])['Job']
            if 'OutputGroupDetails' in full_job:
                print("OutputGroupDetails found in GET_JOB response.")
                print(json.dumps(full_job['OutputGroupDetails'], indent=2))
            else:
                print("OutputGroupDetails NOT FOUND in GET_JOB response either!")
            break

if __name__ == "__main__":
    debug_last_job()
