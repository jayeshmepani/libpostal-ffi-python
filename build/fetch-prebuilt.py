import urllib.request
import tarfile
import zipfile
import os
import sys
from pathlib import Path

POSTALKIT_VERSION = "v0.1.0"
REPO_URL = f"https://github.com/jayeshmepani/libpostal-ffi-python/releases/download/{POSTALKIT_VERSION}"

TARGETS = {
    'linux-x64': 'libpostal-linux-x64.tar.gz',
    'linux-arm64': 'libpostal-linux-arm64.tar.gz',
    'macos-x64': 'libpostal-macos-x64.tar.gz',
    'macos-arm64': 'libpostal-macos-arm64.tar.gz',
    'windows-x64': 'libpostal-windows-x64.zip',
}

def fetch_prebuilt():
    libs_dir = Path(__file__).parent.parent / "postalkit" / "libs"
    
    for target, filename in TARGETS.items():
        target_dir = libs_dir / target
        target_dir.mkdir(parents=True, exist_ok=True)
        
        url = f"{REPO_URL}/{filename}"
        dest = target_dir / filename
        
        print(f"Downloading {url}...")
        try:
            urllib.request.urlretrieve(url, dest)
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            continue
            
        print(f"Extracting {dest}...")
        if filename.endswith('.zip'):
            with zipfile.ZipFile(dest, 'r') as zip_ref:
                zip_ref.extractall(target_dir)
        else:
            with tarfile.open(dest, "r:gz") as tar:
                tar.extractall(path=target_dir)
                
        os.remove(dest)
        print(f"Successfully setup {target}")

if __name__ == "__main__":
    fetch_prebuilt()
