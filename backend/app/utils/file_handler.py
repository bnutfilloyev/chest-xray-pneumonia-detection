"""
File handling utilities for medical image processing.
HIPAA-compliant file upload and validation for chest X-ray images.
"""
import os
import uuid
import hashlib
import logging
import io
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime, timedelta
from PIL import Image, ImageOps
import magic
from fastapi import UploadFile, HTTPException
import aiofiles

from app.core.config import settings

logger = logging.getLogger(__name__)

# Allowed file types for medical images
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.dicom', '.dcm'}
ALLOWED_MIME_TYPES = {
    'image/jpeg',
    'image/png', 
    'application/dicom',
    'application/octet-stream'  # DICOM files sometimes appear as this
}

# Image size constraints
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MIN_FILE_SIZE = 1024  # 1KB
MAX_IMAGE_DIMENSION = 4096
MIN_IMAGE_DIMENSION = 224


class FileHandler:
    """Secure file handling for medical images."""
    
    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for organization
        self.temp_dir = self.upload_dir / "temp"
        self.processed_dir = self.upload_dir / "processed"
        self.archive_dir = self.upload_dir / "archive"
        
        for directory in [self.temp_dir, self.processed_dir, self.archive_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    async def validate_file(self, file: UploadFile) -> Dict[str, Any]:
        """
        Validate uploaded file for security and medical requirements.
        
        Args:
            file: FastAPI UploadFile object
            
        Returns:
            Dictionary with validation results
            
        Raises:
            HTTPException: If file validation fails
        """
        validation_result = {
            "is_valid": False,
            "filename": file.filename,
            "size": 0,
            "content_type": file.content_type,
            "errors": []
        }
        
        try:
            # Check filename
            if not file.filename:
                validation_result["errors"].append("No filename provided")
                return validation_result
            
            # Check file extension
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                validation_result["errors"].append(
                    f"File type {file_ext} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
                )
                return validation_result
            
            # Read file content for validation
            content = await file.read()
            await file.seek(0)  # Reset file pointer
            
            validation_result["size"] = len(content)
            
            # Check file size
            if len(content) < MIN_FILE_SIZE:
                validation_result["errors"].append(f"File too small. Minimum size: {MIN_FILE_SIZE} bytes")
                return validation_result
            
            if len(content) > MAX_FILE_SIZE:
                validation_result["errors"].append(f"File too large. Maximum size: {MAX_FILE_SIZE} bytes")
                return validation_result
            
            # Validate MIME type using python-magic
            mime_type = magic.from_buffer(content, mime=True)
            if mime_type not in ALLOWED_MIME_TYPES:
                validation_result["errors"].append(f"Invalid MIME type: {mime_type}")
                return validation_result
            
            # Additional validation for image files
            if mime_type.startswith('image/'):
                image_validation = await self._validate_image(content)
                if not image_validation["is_valid"]:
                    validation_result["errors"].extend(image_validation["errors"])
                    return validation_result
                validation_result.update(image_validation)
            
            validation_result["is_valid"] = True
            validation_result["mime_type"] = mime_type
            validation_result["file_hash"] = hashlib.sha256(content).hexdigest()
            
        except Exception as e:
            logger.error(f"File validation error: {e}")
            validation_result["errors"].append(f"Validation error: {str(e)}")
        
        return validation_result
    
    async def _validate_image(self, content: bytes) -> Dict[str, Any]:
        """
        Validate image-specific requirements.
        
        Args:
            content: Image file content
            
        Returns:
            Dictionary with image validation results
        """
        result = {"is_valid": False, "errors": []}
        
        try:
            # Open image with PIL
            image = Image.open(io.BytesIO(content))
            
            # Check image dimensions
            width, height = image.size
            if width < MIN_IMAGE_DIMENSION or height < MIN_IMAGE_DIMENSION:
                result["errors"].append(
                    f"Image dimensions too small. Minimum: {MIN_IMAGE_DIMENSION}x{MIN_IMAGE_DIMENSION}"
                )
                return result
            
            if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
                result["errors"].append(
                    f"Image dimensions too large. Maximum: {MAX_IMAGE_DIMENSION}x{MAX_IMAGE_DIMENSION}"
                )
                return result
            
            # Check if image is readable and not corrupted
            image.verify()
            
            # Reopen for getting additional metadata
            image = Image.open(io.BytesIO(content))
            
            result.update({
                "is_valid": True,
                "width": width,
                "height": height,
                "format": image.format,
                "mode": image.mode
            })
            
        except Exception as e:
            logger.error(f"Image validation error: {e}")
            result["errors"].append(f"Invalid image file: {str(e)}")
        
        return result
    
    async def save_file(self, file: UploadFile, patient_id: int) -> Dict[str, Any]:
        """
        Save uploaded file securely with medical data handling.
        
        Args:
            file: FastAPI UploadFile object
            patient_id: Patient ID for file organization
            
        Returns:
            Dictionary with file information
            
        Raises:
            HTTPException: If file saving fails
        """
        try:
            # Validate file first
            validation = await self.validate_file(file)
            if not validation["is_valid"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"File validation failed: {', '.join(validation['errors'])}"
                )
            
            # Generate secure filename
            file_ext = Path(file.filename).suffix.lower()
            secure_filename = f"{uuid.uuid4().hex}_{patient_id}{file_ext}"
            
            # Create patient-specific directory
            patient_dir = self.processed_dir / f"patient_{patient_id}"
            patient_dir.mkdir(exist_ok=True)
            
            # Full file path
            file_path = patient_dir / secure_filename
            
            # Save file asynchronously
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Generate file metadata
            file_info = {
                "original_filename": file.filename,
                "secure_filename": secure_filename,
                "file_path": str(file_path),
                "relative_path": str(file_path.relative_to(self.upload_dir)),
                "size": validation["size"],
                "mime_type": validation["mime_type"],
                "file_hash": validation["file_hash"],
                "patient_id": patient_id,
                "upload_timestamp": datetime.utcnow(),
                "width": validation.get("width"),
                "height": validation.get("height"),
                "format": validation.get("format")
            }
            
            logger.info(f"File saved successfully: {secure_filename} for patient {patient_id}")
            return file_info
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"File saving error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save file: {str(e)}"
            )
    
    async def delete_file(self, file_path: str) -> bool:
        """
        Securely delete a file.
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            path = Path(file_path)
            if path.exists() and path.is_file():
                # Verify file is within allowed directory
                if not str(path.resolve()).startswith(str(self.upload_dir.resolve())):
                    logger.warning(f"Attempted to delete file outside upload directory: {file_path}")
                    return False
                
                path.unlink()
                logger.info(f"File deleted successfully: {file_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"File deletion error: {e}")
            return False
    
    async def archive_file(self, file_path: str, patient_id: int) -> Optional[str]:
        """
        Archive a file for long-term storage.
        
        Args:
            file_path: Path to file to archive
            patient_id: Patient ID for organization
            
        Returns:
            Archive file path if successful, None otherwise
        """
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                logger.warning(f"Source file not found for archiving: {file_path}")
                return None
            
            # Create archive structure
            archive_patient_dir = self.archive_dir / f"patient_{patient_id}"
            archive_patient_dir.mkdir(exist_ok=True)
            
            # Generate archive filename with timestamp
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            archive_filename = f"{timestamp}_{source_path.name}"
            archive_path = archive_patient_dir / archive_filename
            
            # Copy file to archive
            import shutil
            shutil.copy2(source_path, archive_path)
            
            logger.info(f"File archived successfully: {file_path} -> {archive_path}")
            return str(archive_path)
            
        except Exception as e:
            logger.error(f"File archiving error: {e}")
            return None
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file information or None if file not found
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            stat = path.stat()
            return {
                "filename": path.name,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime),
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "is_file": path.is_file(),
                "extension": path.suffix.lower()
            }
            
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return None
    
    def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """
        Clean up temporary files older than specified age.
        
        Args:
            max_age_hours: Maximum age of files to keep in hours
            
        Returns:
            Number of files cleaned up
        """
        try:
            current_time = datetime.now()
            max_age = timedelta(hours=max_age_hours)
            cleaned_count = 0
            
            for file_path in self.temp_dir.glob("*"):
                if file_path.is_file():
                    file_age = current_time - datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_age > max_age:
                        file_path.unlink()
                        cleaned_count += 1
            
            logger.info(f"Cleaned up {cleaned_count} temporary files")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Temp file cleanup error: {e}")
            return 0


# Global file handler instance
file_handler = FileHandler()


# Convenience wrapper functions for backward compatibility
async def validate_image_file(file: UploadFile) -> Dict[str, Any]:
    """
    Validate an uploaded image file.
    
    Args:
        file: FastAPI UploadFile object
    
    Returns:
        Validation results dictionary
    """
    return await file_handler.validate_file(file)


async def save_uploaded_file(file: UploadFile, patient_id: int) -> Dict[str, Any]:
    """
    Save an uploaded file securely.
    
    Args:
        file: FastAPI UploadFile object
        patient_id: Patient ID for file organization
    
    Returns:
        File save results dictionary
    """
    return await file_handler.save_file(file, patient_id)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    # Remove or replace dangerous characters
    import re
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    return filename[:255]  # Limit length
