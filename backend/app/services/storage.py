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

    def save_file(self, file: BinaryIO, filename: str) -> str:
        """Save file to local storage"""
        # Create date-based subdirectory
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
    """S3 storage (future implementation)"""

    def __init__(self, bucket_name: str, region: str):
        self.bucket_name = bucket_name
        self.region = region
        # TODO: Initialize boto3 client

    def save_file(self, file: BinaryIO, filename: str) -> str:
        """Save file to S3"""
        # TODO: Implement S3 upload
        raise NotImplementedError("S3 storage not yet implemented")

    def delete_file(self, file_path: str) -> bool:
        """Delete from S3"""
        # TODO: Implement S3 delete
        raise NotImplementedError("S3 storage not yet implemented")

    def get_file_url(self, file_path: str) -> str:
        """Get S3 URL"""
        # TODO: Return S3 URL or presigned URL
        raise NotImplementedError("S3 storage not yet implemented")


# Factory function
def get_storage_service(storage_type: str = "local") -> StorageService:
    """Get storage service instance"""
    if storage_type == "local":
        return LocalStorage()
    elif storage_type == "s3":
        # TODO: Get S3 config from settings
        raise NotImplementedError("S3 storage not yet implemented")
    else:
        raise ValueError(f"Unknown storage type: {storage_type}")