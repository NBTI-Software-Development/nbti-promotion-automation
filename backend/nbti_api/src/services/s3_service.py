"""
AWS S3 File Storage Service
Handles file uploads and downloads to/from AWS S3.
"""

import os
import boto3
from botocore.exceptions import ClientError
from typing import Optional, BinaryIO
from werkzeug.utils import secure_filename
import uuid


class S3Service:
    """Service for interacting with AWS S3."""
    
    def __init__(self):
        """Initialize S3 client."""
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.getenv('AWS_S3_BUCKET', 'nbti-promotion-files')
    
    def upload_file(self, file: BinaryIO, folder: str = 'uploads', 
                   filename: Optional[str] = None) -> Optional[str]:
        """
        Upload a file to S3.
        
        Args:
            file: File object to upload
            folder: S3 folder/prefix
            filename: Optional custom filename (will be sanitized)
        
        Returns:
            S3 key (path) of uploaded file, or None if failed
        """
        try:
            # Generate unique filename if not provided
            if filename:
                filename = secure_filename(filename)
            else:
                filename = f"{uuid.uuid4()}.file"
            
            # Construct S3 key
            s3_key = f"{folder}/{filename}"
            
            # Upload file
            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                s3_key,
                ExtraArgs={'ACL': 'private'}  # Private by default
            )
            
            return s3_key
        
        except ClientError as e:
            print(f"Error uploading file to S3: {e}")
            return None
    
    def download_file(self, s3_key: str, local_path: str) -> bool:
        """
        Download a file from S3 to local path.
        
        Args:
            s3_key: S3 key (path) of file
            local_path: Local file path to save to
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.s3_client.download_file(
                self.bucket_name,
                s3_key,
                local_path
            )
            return True
        
        except ClientError as e:
            print(f"Error downloading file from S3: {e}")
            return False
    
    def get_file_url(self, s3_key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate a presigned URL for accessing a file.
        
        Args:
            s3_key: S3 key (path) of file
            expiration: URL expiration time in seconds (default 1 hour)
        
        Returns:
            Presigned URL, or None if failed
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            return url
        
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None
    
    def delete_file(self, s3_key: str) -> bool:
        """
        Delete a file from S3.
        
        Args:
            s3_key: S3 key (path) of file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
        
        except ClientError as e:
            print(f"Error deleting file from S3: {e}")
            return False
    
    def list_files(self, prefix: str = '', max_keys: int = 1000) -> list:
        """
        List files in S3 bucket with given prefix.
        
        Args:
            prefix: S3 key prefix (folder)
            max_keys: Maximum number of keys to return
        
        Returns:
            List of file keys
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            else:
                return []
        
        except ClientError as e:
            print(f"Error listing files from S3: {e}")
            return []
    
    def file_exists(self, s3_key: str) -> bool:
        """
        Check if a file exists in S3.
        
        Args:
            s3_key: S3 key (path) of file
        
        Returns:
            True if file exists, False otherwise
        """
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
        
        except ClientError:
            return False


# Create singleton instance
s3_service = S3Service()


def upload_pms_evidence(file: BinaryIO, evaluation_id: int, filename: str) -> Optional[str]:
    """
    Upload PMS evidence file.
    
    Args:
        file: File object
        evaluation_id: PMS evaluation ID
        filename: Original filename
    
    Returns:
        S3 key of uploaded file
    """
    folder = f"pms/evaluations/{evaluation_id}/evidence"
    return s3_service.upload_file(file, folder, filename)


def upload_appeal_document(file: BinaryIO, appeal_id: int, filename: str) -> Optional[str]:
    """
    Upload appeal supporting document.
    
    Args:
        file: File object
        appeal_id: Appeal ID
        filename: Original filename
    
    Returns:
        S3 key of uploaded file
    """
    folder = f"pms/appeals/{appeal_id}/documents"
    return s3_service.upload_file(file, folder, filename)


def upload_user_document(file: BinaryIO, user_id: int, doc_type: str, filename: str) -> Optional[str]:
    """
    Upload user document (qualification, certificate, etc.).
    
    Args:
        file: File object
        user_id: User ID
        doc_type: Document type (qualification, certificate, etc.)
        filename: Original filename
    
    Returns:
        S3 key of uploaded file
    """
    folder = f"users/{user_id}/{doc_type}"
    return s3_service.upload_file(file, folder, filename)

