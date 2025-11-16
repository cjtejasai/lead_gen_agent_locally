#!/usr/bin/env python3
"""
Simple script to create S3 bucket for Lyncsea
Run with: python create_s3_bucket.py

Set AWS credentials in environment or .env file:
  AWS_ACCESS_KEY_ID=your_key
  AWS_SECRET_ACCESS_KEY=your_secret
"""

import boto3
import os
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BUCKET_NAME = os.getenv("AWS_BUCKET_NAME", "lyncsea-storage")
REGION = os.getenv("AWS_REGION", "eu-north-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
    print("Error: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY must be set in .env or environment")
    exit(1)


def create_bucket():
    """Create S3 bucket with proper configuration"""
    try:
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            region_name=REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )

        # Create bucket
        print(f"Creating bucket: {BUCKET_NAME} in region: {REGION}")

        if REGION == 'us-east-1':
            # us-east-1 doesn't need LocationConstraint
            s3_client.create_bucket(Bucket=BUCKET_NAME)
        else:
            s3_client.create_bucket(
                Bucket=BUCKET_NAME,
                CreateBucketConfiguration={'LocationConstraint': REGION}
            )

        print(f"✓ Bucket '{BUCKET_NAME}' created successfully!")

        # Block public access (security best practice)
        print("\nConfiguring security settings...")
        s3_client.put_public_access_block(
            Bucket=BUCKET_NAME,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
        print("✓ Public access blocked (files are private)")

        # Enable versioning (optional, good for backups)
        print("\nEnabling versioning...")
        s3_client.put_bucket_versioning(
            Bucket=BUCKET_NAME,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        print("✓ Versioning enabled")

        # Skip lifecycle rules - keep all recordings indefinitely
        print("\n⊗ Skipping lifecycle rules (recordings will be kept indefinitely)")

        # Enable default encryption
        print("\nEnabling encryption...")
        s3_client.put_bucket_encryption(
            Bucket=BUCKET_NAME,
            ServerSideEncryptionConfiguration={
                'Rules': [{
                    'ApplyServerSideEncryptionByDefault': {
                        'SSEAlgorithm': 'AES256'
                    }
                }]
            }
        )
        print("✓ Encryption enabled (AES-256)")

        print("\n" + "="*60)
        print("SUCCESS! S3 bucket is ready to use")
        print("="*60)
        print(f"\nBucket Name: {BUCKET_NAME}")
        print(f"Region: {REGION}")
        print(f"ARN: arn:aws:s3:::{BUCKET_NAME}")
        print("\nNext steps:")
        print("1. Add to backend/.env:")
        print(f"   STORAGE_TYPE=s3")
        print(f"   AWS_BUCKET_NAME={BUCKET_NAME}")
        print(f"   AWS_REGION={REGION}")
        print(f"   AWS_ACCESS_KEY_ID={AWS_ACCESS_KEY_ID}")
        print(f"   AWS_SECRET_ACCESS_KEY={AWS_SECRET_ACCESS_KEY}")
        print("\n2. Install boto3: pip install boto3")
        print("3. Restart backend")

    except ClientError as e:
        error_code = e.response['Error']['Code']

        if error_code == 'BucketAlreadyExists':
            print(f"✗ Bucket '{BUCKET_NAME}' already exists globally (S3 names are unique)")
            print("  Try a different name like: lyncsea-storage-prod-2025")
        elif error_code == 'BucketAlreadyOwnedByYou':
            print(f"✓ Bucket '{BUCKET_NAME}' already exists and is owned by you")
            print("  You can use it as-is!")
        else:
            print(f"✗ Error creating bucket: {e}")
            return False

    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

    return True


if __name__ == "__main__":
    print("Lyncsea S3 Bucket Setup")
    print("=" * 60)
    create_bucket()