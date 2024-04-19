import boto3
import json

# Define AWS credentials and region
s3 = boto3.client('s3', region_name='ap-south-1')
bucket_name = 'faceattendbucket'

# Define JSON data to upload
persons_data = {
    "persons": [
        {
            "name": "Sushant",
            "email": "sushant@example.com",
            "department": "ASET",
            "id": 1
        },
        {
            "name": "Sachin",
            "email": "sachin@example.com",
            "department": "ASET",
            "id": 2
        },
        {
            "name": "Modi",
            "email": "pm@example.com",
            "department": "ADMIN",
            "id": 3
        },
    ]
}

# Convert Python dictionary to JSON string
persons_json = json.dumps(persons_data)

# Define bucket name and file name
file_name = 'persons_data.json'

# Upload JSON file to S3
s3.put_object(Bucket=bucket_name, Key=file_name, Body=persons_json)

print(f"JSON file '{file_name}' uploaded successfully to S3 bucket '{bucket_name}'.")
