"""
Storage service - handles file storage (local for now, S3 later)
Design pattern: Strategy pattern for easy swap between local/S3
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import BinaryIO
import logging

logger = logging.getLogger(__name__)


class StorageService:
    """Base storage interface"""

    def save_file(self, file: BinaryIO, filename: str) -> str:
        """Save file and return path/URL"""
        raise NotImplementedError

    def delete_file(self, file_path: str) -> bool:
        """Delete file"""
        raise NotImplementedError

    def get_file_url(self, file_path: str) -> str:
        """Get accessible URL"""
        raise NotImplementedError


class LocalStorage(StorageService):
    """Local filesystem storage"""

    def __init__(self, base_path: str = None):
        # Default to data/recordings at project root
        if base_path is None:
            project_root = Path(__file__).parent.parent.parent.parent
            base_path = project_root / "data" / "recordings"
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Local storage initialized at: {self.base_path.absolute()}")

    def save_file(self, file: BinaryIO, filename: str, user_id: int = None) -> str:
        """Save file to local storage (optionally with user_id prefix)"""
        # Create path with optional user_id: user_<id>/recordings/YYYY/MM/DD/ or just YYYY/MM/DD/
        if user_id:
            date_dir = f"user_{user_id}/recordings/{datetime.now().strftime('%Y/%m/%d')}"
        else:
            date_dir = datetime.now().strftime("%Y/%m/%d")

        save_dir = self.base_path / date_dir
        save_dir.mkdir(parents=True, exist_ok=True)

        # Save file
        file_path = save_dir / filename
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file, f)

        relative_path = file_path.relative_to(self.base_path)
        logger.info(f"File saved: {relative_path}")
        return str(relative_path)

    def delete_file(self, file_path: str) -> bool:
        """Delete file from local storage"""
        full_path = self.base_path / file_path
        if full_path.exists():
            full_path.unlink()
            logger.info(f"File deleted: {file_path}")
            return True
        return False

    def get_file_url(self, file_path: str) -> str:
        """Get file URL (for local, return path)"""
        return f"/storage/{file_path}"

    def get_full_path(self, file_path: str) -> Path:
        """Get absolute file path"""
        return self.base_path / file_path


class S3Storage(StorageService):
    """S3 storage implementation"""

    def __init__(self, bucket_name: str, region: str, aws_access_key: str = None, aws_secret_key: str = None):
        self.bucket_name = bucket_name
        self.region = region

        try:
            import boto3
            from botocore.exceptions import ClientError
            self.ClientError = ClientError

            # Initialize S3 client
            if aws_access_key and aws_secret_key:
                self.s3_client = boto3.client(
                    's3',
                    region_name=region,
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key
                )
            else:
                # Use default credentials (IAM role, env vars, or config file)
                self.s3_client = boto3.client('s3', region_name=region)

            logger.info(f"S3 storage initialized: bucket={bucket_name}, region={region}")
        except ImportError:
            logger.error("boto3 not installed. Run: pip install boto3")
            raise ImportError("boto3 is required for S3 storage. Install with: pip install boto3")

    def save_file(self, file: BinaryIO, filename: str, user_id: int = None, data_type: str = "recordings") -> str:
        """Save file to S3 with user_id prefix

        Args:
            file: File object to upload
            filename: Name of the file
            user_id: User ID for organizing files
            data_type: Type of data (recordings, events, leads, etc.)
        """
        from datetime import datetime

        # Create S3 key with structure: user_<id>/<data_type>/YYYY/MM/DD/filename
        if user_id:
            date_path = datetime.now().strftime("%Y/%m/%d")
            s3_key = f"user_{user_id}/{data_type}/{date_path}/{filename}"
        else:
            # Fallback without user_id
            date_path = datetime.now().strftime("%Y/%m/%d")
            s3_key = f"{data_type}/{date_path}/{filename}"

        try:
            # Upload to S3
            file.seek(0)  # Reset file pointer
            self.s3_client.upload_fileobj(file, self.bucket_name, s3_key)
            logger.info(f"File uploaded to S3: s3://{self.bucket_name}/{s3_key}")
            return s3_key
        except self.ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            raise Exception(f"Failed to upload to S3: {e}")

    def delete_file(self, file_path: str) -> bool:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_path)
            logger.info(f"File deleted from S3: {file_path}")
            return True
        except self.ClientError as e:
            logger.error(f"S3 delete failed: {e}")
            return False

    def get_file_url(self, file_path: str, expiration: int = 3600) -> str:
        """Get presigned URL for S3 file (valid for 1 hour by default)"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_path},
                ExpiresIn=expiration
            )
            return url
        except self.ClientError as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return f"s3://{self.bucket_name}/{file_path}"

    def get_full_path(self, file_path: str) -> str:
        """Get S3 URI"""
        return f"s3://{self.bucket_name}/{file_path}"


# Factory function
def get_storage_service(storage_type: str = "local") -> StorageService:
    """Get storage service instance"""
    if storage_type == "local":
        return LocalStorage()
    elif storage_type == "s3":
        # Get S3 config from environment/settings
        from app.core.config import settings
        return S3Storage(
            bucket_name=settings.AWS_BUCKET_NAME,
            region=settings.AWS_REGION,
            aws_access_key=settings.AWS_ACCESS_KEY_ID,
            aws_secret_key=settings.AWS_SECRET_ACCESS_KEY
        )
    else:
        raise ValueError(f"Unknown storage type: {storage_type}")