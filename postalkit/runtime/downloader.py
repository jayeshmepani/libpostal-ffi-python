import os
import tarfile
from pathlib import Path

import httpx
from tqdm import tqdm

from ..exceptions import DependencyMissingError


def download_file(url: str, dest_path: Path, extract: bool = False, desc: str = "Downloading"):
    """Downloads a file from a URL to a destination path, optionally extracting it."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # Simple check if it is already there (for the archive itself,
    # or skipped if extraction is managed externally)
    if dest_path.exists():
        return

    try:
        with httpx.stream("GET", url, follow_redirects=True) as response:
            response.raise_for_status()
            total_size = int(response.headers.get("content-length", 0))

            with (
                open(dest_path, "wb") as f,
                tqdm(
                    desc=desc,
                    total=total_size,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                ) as bar,
            ):
                for chunk in response.iter_bytes(chunk_size=8192):
                    f.write(chunk)
                    bar.update(len(chunk))
    except Exception as e:
        if dest_path.exists():
            os.remove(dest_path)
        raise DependencyMissingError(f"Failed to download {url}: {e}") from None

    if extract and str(dest_path).endswith(".tar.gz"):
        _extract_tar_gz(dest_path, dest_path.parent)


def _extract_tar_gz(tar_path: Path, extract_path: Path):
    print(f"Extracting {tar_path.name}...")
    try:
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=extract_path)
        os.remove(tar_path)
    except Exception as e:
        raise DependencyMissingError(f"Failed to extract {tar_path}: {e}") from None
