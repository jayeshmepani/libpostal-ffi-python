import ctypes

from ..exceptions import DependencyMissingError
from ..runtime.paths import get_binary_dir, get_bundled_binary_dir
from ..runtime.platform import get_library_name


def load_libpostal() -> ctypes.CDLL:
    """Loads the libpostal shared library into ctypes."""
    lib_name = get_library_name()

    # 1. Check bundled library first
    bundled_lib_path = get_bundled_binary_dir() / lib_name
    if bundled_lib_path.exists():
        try:
            return ctypes.cdll.LoadLibrary(str(bundled_lib_path))
        except OSError as e:
            raise DependencyMissingError from None(
                f"Failed to load bundled library {bundled_lib_path}: {e}"
            )

    # 2. Check auto-downloaded library
    bin_dir = get_binary_dir()
    lib_path = bin_dir / lib_name

    if not lib_path.exists():
        # Maybe it's installed system-wide?
        try:
            return ctypes.cdll.LoadLibrary(lib_name)
        except OSError:
            pass
        raise DependencyMissingError from None(
            f"Could not find {lib_name} in {bin_dir}, bundled {bundled_lib_path}, or system paths. Run initialization first."
        )

    try:
        # Load the library using ctypes
        return ctypes.cdll.LoadLibrary(str(lib_path))
    except OSError as e:
        raise DependencyMissingError from None(f"Failed to load shared library {lib_path}: {e}")
