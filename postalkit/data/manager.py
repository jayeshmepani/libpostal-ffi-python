import os
from pathlib import Path
from ..runtime.paths import get_binary_dir, get_model_dir
from ..runtime.platform import get_platform_identifier, get_library_name
from ..runtime.downloader import download_file
from ..exceptions import DependencyMissingError
from .checksum import verify_checksum

POSTALKIT_VERSION = "v1.0.0"
BINARIES_BASE_URL = os.environ.get("POSTALKIT_BINARIES_URL", f"https://github.com/jayeshmepani/libpostal-ffi-python/releases/download/{POSTALKIT_VERSION}")
MODEL_DATA_URL = os.environ.get("POSTALKIT_MODEL_URL", "https://s3.amazonaws.com/libpostal/data/libpostal_data.tar.gz")

def _download_and_verify(url: str, tar_path: Path, desc: str):
    """Downloads a file and its .sha256 checksum file, then verifies and extracts."""
    # 1. Download the archive
    download_file(url, tar_path, extract=False, desc=desc)
    
    # 2. Download the checksum
    checksum_url = f"{url}.sha256"
    checksum_path = tar_path.with_suffix(".tar.gz.sha256")
    try:
        download_file(checksum_url, checksum_path, extract=False, desc=f"{desc} Checksum")
        with open(checksum_path, "r") as f:
            # typical format: "hash  filename"
            expected_hash = f.read().strip().split()[0]
            
        if not verify_checksum(tar_path, expected_hash):
            os.remove(tar_path)
            raise DependencyMissingError(f"Checksum verification failed for {tar_path.name}")
    except Exception as e:
        # If the checksum file doesn't exist remotely or fails to download,
        # we strictly fail to prevent compromised or corrupt binaries in production.
        if tar_path.exists():
            os.remove(tar_path)
        if checksum_path.exists():
            os.remove(checksum_path)
        raise DependencyMissingError(f"Failed to fetch or verify checksum for {tar_path.name}: {e}")

    # 3. Extract after verification
    from ..runtime.downloader import _extract_tar_gz
    _extract_tar_gz(tar_path, tar_path.parent)

def ensure_models() -> Path:
    """Ensures libpostal data models are downloaded and returns their path."""
    model_dir = get_model_dir()
    marker_file = model_dir / "data_version"
    
    if not marker_file.exists():
        tar_path = model_dir / "libpostal_data.tar.gz"
        print("PostalKit models not found. Downloading (~2GB)...")
        _download_and_verify(MODEL_DATA_URL, tar_path, "Model Data")
        marker_file.write_text("1")
             
    return model_dir

def ensure_binary() -> Path:
    """Ensures the correct shared library for the platform is downloaded."""
    from ..runtime.paths import get_bundled_binary_dir
    bin_dir = get_binary_dir()
    lib_name = get_library_name()
    platform_id = get_platform_identifier()
    
    # 1. Check bundled library
    bundled_lib_path = get_bundled_binary_dir() / lib_name
    if bundled_lib_path.exists():
        return bundled_lib_path
        
    # 2. Check auto-downloaded library
    lib_path = bin_dir / lib_name
    
    if not lib_path.exists():
        download_url = f"{BINARIES_BASE_URL}/libpostal-{platform_id}.tar.gz"
        tar_path = bin_dir / f"libpostal-{platform_id}.tar.gz"
        print(f"PostalKit binary not found. Downloading for {platform_id}...")
        _download_and_verify(download_url, tar_path, "Binary")
            
    return lib_path

def ensure_all_assets():
    """Download models and binaries if missing."""
    ensure_models()
    ensure_binary()
