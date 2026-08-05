import os
import hashlib
from pathlib import Path
from datetime import datetime

class StorageManager:
    """
    Handles secure saving of downloaded files and checksum generation.
    """
    def __init__(self, base_storage_dir: str = "storage"):
        self.base_storage_dir = Path(base_storage_dir)

    def generate_checksum(self, file_content: bytes) -> str:
        return hashlib.sha256(file_content).hexdigest()

    def save_file(self, marketplace_id: str, filename: str, file_content: bytes) -> str:
        """
        Saves the file to storage/{marketplace}/{YYYY}/{MM}/{filename}
        Returns the relative storage path.
        """
        now = datetime.utcnow()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        
        # Build path
        directory = self.base_storage_dir / marketplace_id.lower() / year / month
        
        # Create directory if it doesn't exist
        directory.mkdir(parents=True, exist_ok=True)
        
        # We append a timestamp to the filename to avoid collisions 
        # even if the same filename is uploaded twice in the same month.
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(filename)
        safe_filename = f"{name}_{timestamp}{ext}"
        
        full_path = directory / safe_filename
        
        with open(full_path, "wb") as f:
            f.write(file_content)
            
        return str(full_path)
