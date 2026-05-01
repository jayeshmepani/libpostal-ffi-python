import os
from pathlib import Path

from platformdirs import user_data_dir

APP_NAME = "postalkit"
APP_AUTHOR = "postalkit"


def get_data_dir() -> Path:
    """Returns the directory where libpostal models and binaries are stored."""
    # Allow overriding via environment variable
    custom_dir = os.environ.get("POSTALKIT_DATA_DIR")
    if custom_dir:
        return Path(custom_dir)
    return Path(user_data_dir(APP_NAME, APP_AUTHOR))


def get_binary_dir() -> Path:
    """Returns the directory where the shared library is stored."""
    return get_data_dir() / "bin"


def get_bundled_binary_dir() -> Path:
    """Returns the directory where the prebuilt shared library is bundled within the package."""
    from .platform import get_platform_identifier

    return Path(__file__).parent.parent / "libs" / get_platform_identifier()


def get_model_dir() -> Path:
    """Returns the directory where the machine learning models are stored."""
    return get_data_dir() / "models"
