import postalkit
from postalkit.runtime.platform import get_arch, get_os, get_platform_identifier


def test_platform_identifier():
    os_name = get_os()
    arch = get_arch()
    ident = get_platform_identifier()
    assert ident == f"{os_name}-{arch}"


def test_ffi_exports():
    """Ensure all expected C functions and structs are exported."""
    expected_exports = [
        "libpostal_setup",
        "libpostal_parse_address",
        "libpostal_expand_address",
        "libpostal_normalize_options_t",
        "libpostal_address_parser_options_t",
        "libpostal_address_parser_response_t",
        "LIBPOSTAL_ADDRESS_NONE",
        "LIBPOSTAL_NORMALIZE_DEFAULT_STRING_OPTIONS",
        "LIBPOSTAL_LIKELY_DUPLICATE",
    ]

    for exp in expected_exports:
        assert hasattr(postalkit, exp), f"Missing {exp} in postalkit module"
