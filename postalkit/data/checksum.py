import hashlib
from pathlib import Path

def verify_checksum(file_path: Path, expected_hash: str) -> bool:
    """
    Verifies the SHA256 checksum of a file against an expected hash.
    
    Args:
        file_path (Path): Path to the file.
        expected_hash (str): The expected SHA256 hash.
        
    Returns:
        bool: True if the checksum matches, False otherwise.
    """
    if not file_path.exists():
        return False
        
    sha256_hash = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        # Read and update hash in chunks to prevent memory overload for large files
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
            
    return sha256_hash.hexdigest() == expected_hash
