import platform


def get_os() -> str:
    """Returns a normalized OS name."""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    if system == "windows":
        return "windows"
    return "linux"


def get_arch() -> str:
    """Returns a normalized architecture name."""
    arch = platform.machine().lower()
    if arch in ["x86_64", "amd64"]:
        return "x64"
    if arch in ["arm64", "aarch64"]:
        return "arm64"
    if arch in ["x86", "i386", "i686"]:
        return "x86"
    return arch


def get_library_name() -> str:
    """Returns the expected shared library file name for the current OS."""
    os_name = get_os()
    if os_name == "macos":
        return "libpostal.dylib"
    if os_name == "windows":
        return "postal.dll"
    return "libpostal.so"


def get_platform_identifier() -> str:
    """Returns an identifier like 'linux-x86_64'."""
    return f"{get_os()}-{get_arch()}"
