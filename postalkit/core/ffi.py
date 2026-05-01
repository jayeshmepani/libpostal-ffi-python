import ctypes
import os
from ..runtime.loader import load_libpostal
from ..data.manager import ensure_all_assets, ensure_models
from ..exceptions import InitializationError

# Global state
_lib = None
_is_initialized = False

# --- Constants & Defines ---

# Token Types
LIBPOSTAL_TOKEN_TYPE_END = 0
LIBPOSTAL_TOKEN_TYPE_WORD = 1
LIBPOSTAL_TOKEN_TYPE_ABBREVIATION = 2
LIBPOSTAL_TOKEN_TYPE_IDEOGRAPHIC_CHAR = 3
LIBPOSTAL_TOKEN_TYPE_HANGUL_SYLLABLE = 4
LIBPOSTAL_TOKEN_TYPE_ACRONYM = 5
LIBPOSTAL_TOKEN_TYPE_PHRASE = 10
LIBPOSTAL_TOKEN_TYPE_EMAIL = 20
LIBPOSTAL_TOKEN_TYPE_URL = 21
LIBPOSTAL_TOKEN_TYPE_US_PHONE = 22
LIBPOSTAL_TOKEN_TYPE_INTL_PHONE = 23
LIBPOSTAL_TOKEN_TYPE_NUMERIC = 50
LIBPOSTAL_TOKEN_TYPE_ORDINAL = 51
LIBPOSTAL_TOKEN_TYPE_ROMAN_NUMERAL = 52
LIBPOSTAL_TOKEN_TYPE_IDEOGRAPHIC_NUMBER = 53
LIBPOSTAL_TOKEN_TYPE_PERIOD = 100
LIBPOSTAL_TOKEN_TYPE_EXCLAMATION = 101
LIBPOSTAL_TOKEN_TYPE_QUESTION_MARK = 102
LIBPOSTAL_TOKEN_TYPE_COMMA = 103
LIBPOSTAL_TOKEN_TYPE_COLON = 104
LIBPOSTAL_TOKEN_TYPE_SEMICOLON = 105
LIBPOSTAL_TOKEN_TYPE_PLUS = 106
LIBPOSTAL_TOKEN_TYPE_AMPERSAND = 107
LIBPOSTAL_TOKEN_TYPE_AT_SIGN = 108
LIBPOSTAL_TOKEN_TYPE_POUND = 109
LIBPOSTAL_TOKEN_TYPE_ELLIPSIS = 110
LIBPOSTAL_TOKEN_TYPE_DASH = 111
LIBPOSTAL_TOKEN_TYPE_BREAKING_DASH = 112
LIBPOSTAL_TOKEN_TYPE_HYPHEN = 113
LIBPOSTAL_TOKEN_TYPE_PUNCT_OPEN = 114
LIBPOSTAL_TOKEN_TYPE_PUNCT_CLOSE = 115
LIBPOSTAL_TOKEN_TYPE_DOUBLE_QUOTE = 119
LIBPOSTAL_TOKEN_TYPE_SINGLE_QUOTE = 120
LIBPOSTAL_TOKEN_TYPE_OPEN_QUOTE = 121
LIBPOSTAL_TOKEN_TYPE_CLOSE_QUOTE = 122
LIBPOSTAL_TOKEN_TYPE_SLASH = 124
LIBPOSTAL_TOKEN_TYPE_BACKSLASH = 125
LIBPOSTAL_TOKEN_TYPE_GREATER_THAN = 126
LIBPOSTAL_TOKEN_TYPE_LESS_THAN = 127
LIBPOSTAL_TOKEN_TYPE_OTHER = 200
LIBPOSTAL_TOKEN_TYPE_WHITESPACE = 300
LIBPOSTAL_TOKEN_TYPE_NEWLINE = 301
LIBPOSTAL_TOKEN_TYPE_INVALID_CHAR = 500

# Address Components
LIBPOSTAL_ADDRESS_NONE = 0
LIBPOSTAL_ADDRESS_ANY = (1 << 0)
LIBPOSTAL_ADDRESS_NAME = (1 << 1)
LIBPOSTAL_ADDRESS_HOUSE_NUMBER = (1 << 2)
LIBPOSTAL_ADDRESS_STREET = (1 << 3)
LIBPOSTAL_ADDRESS_UNIT = (1 << 4)
LIBPOSTAL_ADDRESS_LEVEL = (1 << 5)
LIBPOSTAL_ADDRESS_STAIRCASE = (1 << 6)
LIBPOSTAL_ADDRESS_ENTRANCE = (1 << 7)
LIBPOSTAL_ADDRESS_CATEGORY = (1 << 8)
LIBPOSTAL_ADDRESS_NEAR = (1 << 9)
LIBPOSTAL_ADDRESS_TOPONYM = (1 << 13)
LIBPOSTAL_ADDRESS_POSTAL_CODE = (1 << 14)
LIBPOSTAL_ADDRESS_PO_BOX = (1 << 15)
LIBPOSTAL_ADDRESS_ALL = ((1 << 16) - 1)

# Normalize String Options
LIBPOSTAL_NORMALIZE_STRING_LATIN_ASCII = 1 << 0
LIBPOSTAL_NORMALIZE_STRING_TRANSLITERATE = 1 << 1
LIBPOSTAL_NORMALIZE_STRING_STRIP_ACCENTS = 1 << 2
LIBPOSTAL_NORMALIZE_STRING_DECOMPOSE = 1 << 3
LIBPOSTAL_NORMALIZE_STRING_LOWERCASE = 1 << 4
LIBPOSTAL_NORMALIZE_STRING_TRIM = 1 << 5
LIBPOSTAL_NORMALIZE_STRING_REPLACE_HYPHENS = 1 << 6
LIBPOSTAL_NORMALIZE_STRING_COMPOSE = 1 << 7
LIBPOSTAL_NORMALIZE_STRING_SIMPLE_LATIN_ASCII = 1 << 8
LIBPOSTAL_NORMALIZE_STRING_REPLACE_NUMEX = 1 << 9

# Normalize Token Options
LIBPOSTAL_NORMALIZE_TOKEN_REPLACE_HYPHENS = 1 << 0
LIBPOSTAL_NORMALIZE_TOKEN_DELETE_HYPHENS = 1 << 1
LIBPOSTAL_NORMALIZE_TOKEN_DELETE_FINAL_PERIOD = 1 << 2
LIBPOSTAL_NORMALIZE_TOKEN_DELETE_ACRONYM_PERIODS = 1 << 3
LIBPOSTAL_NORMALIZE_TOKEN_DROP_ENGLISH_POSSESSIVES = 1 << 4
LIBPOSTAL_NORMALIZE_TOKEN_DELETE_OTHER_APOSTROPHE = 1 << 5
LIBPOSTAL_NORMALIZE_TOKEN_SPLIT_ALPHA_FROM_NUMERIC = 1 << 6
LIBPOSTAL_NORMALIZE_TOKEN_REPLACE_DIGITS = 1 << 7
LIBPOSTAL_NORMALIZE_TOKEN_REPLACE_NUMERIC_TOKEN_LETTERS = 1 << 8
LIBPOSTAL_NORMALIZE_TOKEN_REPLACE_NUMERIC_HYPHENS = 1 << 9

LIBPOSTAL_NORMALIZE_DEFAULT_STRING_OPTIONS = (
    LIBPOSTAL_NORMALIZE_STRING_LATIN_ASCII | LIBPOSTAL_NORMALIZE_STRING_COMPOSE |
    LIBPOSTAL_NORMALIZE_STRING_TRIM | LIBPOSTAL_NORMALIZE_STRING_REPLACE_HYPHENS |
    LIBPOSTAL_NORMALIZE_STRING_STRIP_ACCENTS | LIBPOSTAL_NORMALIZE_STRING_LOWERCASE
)
LIBPOSTAL_NORMALIZE_DEFAULT_TOKEN_OPTIONS = (
    LIBPOSTAL_NORMALIZE_TOKEN_REPLACE_HYPHENS | LIBPOSTAL_NORMALIZE_TOKEN_DELETE_FINAL_PERIOD |
    LIBPOSTAL_NORMALIZE_TOKEN_DELETE_ACRONYM_PERIODS |
    LIBPOSTAL_NORMALIZE_TOKEN_DROP_ENGLISH_POSSESSIVES |
    LIBPOSTAL_NORMALIZE_TOKEN_DELETE_OTHER_APOSTROPHE
)
LIBPOSTAL_NORMALIZE_TOKEN_OPTIONS_DROP_PERIODS = (
    LIBPOSTAL_NORMALIZE_TOKEN_DELETE_FINAL_PERIOD | LIBPOSTAL_NORMALIZE_TOKEN_DELETE_ACRONYM_PERIODS
)
LIBPOSTAL_NORMALIZE_DEFAULT_TOKEN_OPTIONS_NUMERIC = (
    LIBPOSTAL_NORMALIZE_DEFAULT_TOKEN_OPTIONS | LIBPOSTAL_NORMALIZE_TOKEN_SPLIT_ALPHA_FROM_NUMERIC
)

# Duplicate Status
LIBPOSTAL_NULL_DUPLICATE_STATUS = -1
LIBPOSTAL_NON_DUPLICATE = 0
LIBPOSTAL_POSSIBLE_DUPLICATE_NEEDS_REVIEW = 3
LIBPOSTAL_LIKELY_DUPLICATE = 6
LIBPOSTAL_EXACT_DUPLICATE = 9

# --- Structs ---


class libpostal_normalize_options_t(ctypes.Structure):  # noqa: N801
    _fields_ = [
        ("languages", ctypes.POINTER(ctypes.c_char_p)),
        ("num_languages", ctypes.c_size_t),
        ("address_components", ctypes.c_uint16),
        ("latin_ascii", ctypes.c_bool),
        ("transliterate", ctypes.c_bool),
        ("strip_accents", ctypes.c_bool),
        ("decompose", ctypes.c_bool),
        ("lowercase", ctypes.c_bool),
        ("trim_string", ctypes.c_bool),
        ("drop_parentheticals", ctypes.c_bool),
        ("replace_numeric_hyphens", ctypes.c_bool),
        ("delete_numeric_hyphens", ctypes.c_bool),
        ("split_alpha_from_numeric", ctypes.c_bool),
        ("replace_word_hyphens", ctypes.c_bool),
        ("delete_word_hyphens", ctypes.c_bool),
        ("delete_final_periods", ctypes.c_bool),
        ("delete_acronym_periods", ctypes.c_bool),
        ("drop_english_possessives", ctypes.c_bool),
        ("delete_apostrophes", ctypes.c_bool),
        ("expand_numex", ctypes.c_bool),
        ("roman_numerals", ctypes.c_bool),
    ]


class libpostal_address_parser_response_t(ctypes.Structure):  # noqa: N801
    _fields_ = [
        ("num_components", ctypes.c_size_t),
        ("components", ctypes.POINTER(ctypes.c_char_p)),
        ("labels", ctypes.POINTER(ctypes.c_char_p)),
    ]


class libpostal_address_parser_options_t(ctypes.Structure):  # noqa: N801
    _fields_ = [
        ("language", ctypes.c_char_p),
        ("country", ctypes.c_char_p),
    ]


class libpostal_language_classifier_response_t(ctypes.Structure):  # noqa: N801
    _fields_ = [
        ("num_languages", ctypes.c_size_t),
        ("languages", ctypes.POINTER(ctypes.c_char_p)),
        ("probs", ctypes.POINTER(ctypes.c_double)),
    ]


class libpostal_near_dupe_hash_options_t(ctypes.Structure):  # noqa: N801
    _fields_ = [
        ("with_name", ctypes.c_bool),
        ("with_address", ctypes.c_bool),
        ("with_unit", ctypes.c_bool),
        ("with_city_or_equivalent", ctypes.c_bool),
        ("with_small_containing_boundaries", ctypes.c_bool),
        ("with_postal_code", ctypes.c_bool),
        ("with_latlon", ctypes.c_bool),
        ("latitude", ctypes.c_double),
        ("longitude", ctypes.c_double),
        ("geohash_precision", ctypes.c_uint32),
        ("name_and_address_keys", ctypes.c_bool),
        ("name_only_keys", ctypes.c_bool),
        ("address_only_keys", ctypes.c_bool),
    ]


class libpostal_duplicate_options_t(ctypes.Structure):  # noqa: N801
    _fields_ = [
        ("num_languages", ctypes.c_size_t),
        ("languages", ctypes.POINTER(ctypes.c_char_p)),
    ]


class libpostal_fuzzy_duplicate_options_t(ctypes.Structure):  # noqa: N801
    _fields_ = [
        ("num_languages", ctypes.c_size_t),
        ("languages", ctypes.POINTER(ctypes.c_char_p)),
        ("needs_review_threshold", ctypes.c_double),
        ("likely_dupe_threshold", ctypes.c_double),
    ]


class libpostal_fuzzy_duplicate_status_t(ctypes.Structure):  # noqa: N801
    _fields_ = [
        ("status", ctypes.c_int),
        ("similarity", ctypes.c_double),
    ]


class libpostal_token_t(ctypes.Structure):  # noqa: N801
    _fields_ = [
        ("offset", ctypes.c_size_t),
        ("len", ctypes.c_size_t),
        ("type", ctypes.c_uint16),
    ]


class libpostal_normalized_token_t(ctypes.Structure):  # noqa: N801
    _fields_ = [
        ("str", ctypes.c_char_p),
        ("token", libpostal_token_t),
    ]


def _setup_ffi_signatures(lib):
    """Configures argument and return types for the C functions."""
    lib.libpostal_setup.restype = ctypes.c_bool
    lib.libpostal_setup_datadir.argtypes = [ctypes.c_char_p]
    lib.libpostal_setup_datadir.restype = ctypes.c_bool

    lib.libpostal_setup_parser.restype = ctypes.c_bool
    lib.libpostal_setup_parser_datadir.argtypes = [ctypes.c_char_p]
    lib.libpostal_setup_parser_datadir.restype = ctypes.c_bool

    lib.libpostal_setup_language_classifier.restype = ctypes.c_bool
    lib.libpostal_setup_language_classifier_datadir.argtypes = [ctypes.c_char_p]
    lib.libpostal_setup_language_classifier_datadir.restype = ctypes.c_bool

    lib.libpostal_teardown.restype = None
    lib.libpostal_teardown_parser.restype = None
    lib.libpostal_teardown_language_classifier.restype = None

    lib.libpostal_get_default_options.restype = libpostal_normalize_options_t
    lib.libpostal_expand_address.argtypes = [
        ctypes.c_char_p, libpostal_normalize_options_t, ctypes.POINTER(ctypes.c_size_t)
    ]
    lib.libpostal_expand_address.restype = ctypes.POINTER(ctypes.c_char_p)
    lib.libpostal_expand_address_root.argtypes = [
        ctypes.c_char_p, libpostal_normalize_options_t, ctypes.POINTER(ctypes.c_size_t)
    ]
    lib.libpostal_expand_address_root.restype = ctypes.POINTER(ctypes.c_char_p)
    lib.libpostal_expansion_array_destroy.argtypes = [
        ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t
    ]
    lib.libpostal_expansion_array_destroy.restype = None

    lib.libpostal_get_address_parser_default_options.restype = libpostal_address_parser_options_t
    lib.libpostal_parse_address.argtypes = [
        ctypes.c_char_p, libpostal_address_parser_options_t
    ]
    lib.libpostal_parse_address.restype = ctypes.POINTER(libpostal_address_parser_response_t)
    lib.libpostal_address_parser_response_destroy.argtypes = [
        ctypes.POINTER(libpostal_address_parser_response_t)
    ]
    lib.libpostal_address_parser_response_destroy.restype = None
    lib.libpostal_parser_print_features.argtypes = [ctypes.c_bool]
    lib.libpostal_parser_print_features.restype = ctypes.c_bool

    lib.libpostal_classify_language.argtypes = [ctypes.c_char_p]
    lib.libpostal_classify_language.restype = ctypes.POINTER(libpostal_language_classifier_response_t)
    lib.libpostal_language_classifier_response_destroy.argtypes = [
        ctypes.POINTER(libpostal_language_classifier_response_t)
    ]
    lib.libpostal_language_classifier_response_destroy.restype = None

    lib.libpostal_get_near_dupe_hash_default_options.restype = libpostal_near_dupe_hash_options_t
    lib.libpostal_near_dupe_name_hashes.argtypes = [
        ctypes.c_char_p, libpostal_normalize_options_t, ctypes.POINTER(ctypes.c_size_t)
    ]
    lib.libpostal_near_dupe_name_hashes.restype = ctypes.POINTER(ctypes.c_char_p)
    lib.libpostal_near_dupe_hashes.argtypes = [
        ctypes.c_size_t, ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(ctypes.c_char_p),
        libpostal_near_dupe_hash_options_t, ctypes.POINTER(ctypes.c_size_t)
    ]
    lib.libpostal_near_dupe_hashes.restype = ctypes.POINTER(ctypes.c_char_p)
    lib.libpostal_near_dupe_hashes_languages.argtypes = [
        ctypes.c_size_t, ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(ctypes.c_char_p),
        libpostal_near_dupe_hash_options_t, ctypes.c_size_t, ctypes.POINTER(ctypes.c_char_p),
        ctypes.POINTER(ctypes.c_size_t)
    ]
    lib.libpostal_near_dupe_hashes_languages.restype = ctypes.POINTER(ctypes.c_char_p)
    lib.libpostal_place_languages.argtypes = [
        ctypes.c_size_t, ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(ctypes.c_char_p),
        ctypes.POINTER(ctypes.c_size_t)
    ]
    lib.libpostal_place_languages.restype = ctypes.POINTER(ctypes.c_char_p)

    lib.libpostal_get_default_duplicate_options.restype = libpostal_duplicate_options_t
    lib.libpostal_get_duplicate_options_with_languages.argtypes = [
        ctypes.c_size_t, ctypes.POINTER(ctypes.c_char_p)
    ]
    lib.libpostal_get_duplicate_options_with_languages.restype = libpostal_duplicate_options_t

    dup_funcs = [
        lib.libpostal_is_name_duplicate, lib.libpostal_is_street_duplicate,
        lib.libpostal_is_house_number_duplicate, lib.libpostal_is_po_box_duplicate,
        lib.libpostal_is_unit_duplicate, lib.libpostal_is_floor_duplicate,
        lib.libpostal_is_postal_code_duplicate
    ]
    for func in dup_funcs:
        func.argtypes = [ctypes.c_char_p, ctypes.c_char_p, libpostal_duplicate_options_t]
        func.restype = ctypes.c_int

    lib.libpostal_is_toponym_duplicate.argtypes = [
        ctypes.c_size_t, ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(ctypes.c_char_p),
        ctypes.c_size_t, ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(ctypes.c_char_p),
        libpostal_duplicate_options_t
    ]
    lib.libpostal_is_toponym_duplicate.restype = ctypes.c_int

    lib.libpostal_get_default_fuzzy_duplicate_options.restype = libpostal_fuzzy_duplicate_options_t
    lib.libpostal_get_default_fuzzy_duplicate_options_with_languages.argtypes = [
        ctypes.c_size_t, ctypes.POINTER(ctypes.c_char_p)
    ]
    lib.libpostal_get_default_fuzzy_duplicate_options_with_languages.restype = (
        libpostal_fuzzy_duplicate_options_t
    )

    fuzzy_funcs = [lib.libpostal_is_name_duplicate_fuzzy, lib.libpostal_is_street_duplicate_fuzzy]
    for func in fuzzy_funcs:
        func.argtypes = [
            ctypes.c_size_t, ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(ctypes.c_double),
            ctypes.c_size_t, ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(ctypes.c_double),
            libpostal_fuzzy_duplicate_options_t
        ]
        func.restype = libpostal_fuzzy_duplicate_status_t

    lib.libpostal_tokenize.argtypes = [
        ctypes.c_char_p, ctypes.c_bool, ctypes.POINTER(ctypes.c_size_t)
    ]
    lib.libpostal_tokenize.restype = ctypes.POINTER(libpostal_token_t)

    lib.libpostal_normalize_string_languages.argtypes = [
        ctypes.c_char_p, ctypes.c_uint64, ctypes.c_size_t, ctypes.POINTER(ctypes.c_char_p)
    ]
    lib.libpostal_normalize_string_languages.restype = ctypes.c_char_p
    lib.libpostal_normalize_string.argtypes = [ctypes.c_char_p, ctypes.c_uint64]
    lib.libpostal_normalize_string.restype = ctypes.c_char_p

    lib.libpostal_normalized_tokens.argtypes = [
        ctypes.c_char_p, ctypes.c_uint64, ctypes.c_uint64, ctypes.c_bool,
        ctypes.POINTER(ctypes.c_size_t)
    ]
    lib.libpostal_normalized_tokens.restype = ctypes.POINTER(libpostal_normalized_token_t)
    lib.libpostal_normalized_tokens_languages.argtypes = [
        ctypes.c_char_p, ctypes.c_uint64, ctypes.c_uint64, ctypes.c_bool, ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(ctypes.c_size_t)
    ]
    lib.libpostal_normalized_tokens_languages.restype = ctypes.POINTER(libpostal_normalized_token_t)


def initialize():
    """Initializes the libpostal library and models."""
    global _lib, _is_initialized
    if _is_initialized:
        return

    ensure_all_assets()
    model_dir = str(ensure_models()).encode("utf-8")

    try:
        _lib = load_libpostal()
        _setup_ffi_signatures(_lib)

        if not _lib.libpostal_setup_datadir(model_dir):
            raise InitializationError("libpostal_setup_datadir failed") from None
        if not _lib.libpostal_setup_language_classifier_datadir(model_dir):
            raise InitializationError(
                "libpostal_setup_language_classifier_datadir failed"
            ) from None
        if not _lib.libpostal_setup_parser_datadir(model_dir):
            raise InitializationError("libpostal_setup_parser_datadir failed") from None

        _is_initialized = True
    except AttributeError as e:
        raise InitializationError(f"Library loaded but missing symbols: {e}") from None


def get_lib() -> ctypes.CDLL:
    if not _is_initialized:
        initialize()
    return _lib

# --- Direct 1:1 FFI Wrappers ---


def libpostal_setup() -> bool:
    return get_lib().libpostal_setup()


def libpostal_setup_datadir(datadir: bytes) -> bool:
    return get_lib().libpostal_setup_datadir(datadir)


def libpostal_teardown() -> None:
    return get_lib().libpostal_teardown()


def libpostal_setup_parser() -> bool:
    return get_lib().libpostal_setup_parser()


def libpostal_setup_parser_datadir(datadir: bytes) -> bool:
    return get_lib().libpostal_setup_parser_datadir(datadir)


def libpostal_teardown_parser() -> None:
    return get_lib().libpostal_teardown_parser()


def libpostal_setup_language_classifier() -> bool:
    return get_lib().libpostal_setup_language_classifier()


def libpostal_setup_language_classifier_datadir(datadir: bytes) -> bool:
    return get_lib().libpostal_setup_language_classifier_datadir(datadir)


def libpostal_teardown_language_classifier() -> None:
    return get_lib().libpostal_teardown_language_classifier()


def libpostal_get_default_options() -> libpostal_normalize_options_t:
    return get_lib().libpostal_get_default_options()


def libpostal_expand_address(
    input_str: bytes, options: libpostal_normalize_options_t, n: ctypes.POINTER(ctypes.c_size_t)
) -> ctypes.POINTER(ctypes.c_char_p):
    return get_lib().libpostal_expand_address(input_str, options, n)


def libpostal_expand_address_root(
    input_str: bytes, options: libpostal_normalize_options_t, n: ctypes.POINTER(ctypes.c_size_t)
) -> ctypes.POINTER(ctypes.c_char_p):
    return get_lib().libpostal_expand_address_root(input_str, options, n)


def libpostal_expansion_array_destroy(expansions: ctypes.POINTER(ctypes.c_char_p), n: int) -> None:
    return get_lib().libpostal_expansion_array_destroy(expansions, n)


def libpostal_get_address_parser_default_options() -> libpostal_address_parser_options_t:
    return get_lib().libpostal_get_address_parser_default_options()


def libpostal_parse_address(
    address: bytes, options: libpostal_address_parser_options_t
) -> ctypes.POINTER(libpostal_address_parser_response_t):
    return get_lib().libpostal_parse_address(address, options)


def libpostal_address_parser_response_destroy(
    self_ptr: ctypes.POINTER(libpostal_address_parser_response_t)
) -> None:
    return get_lib().libpostal_address_parser_response_destroy(self_ptr)


def libpostal_parser_print_features(print_features: bool) -> bool:
    return get_lib().libpostal_parser_print_features(print_features)


def libpostal_classify_language(
    address: bytes
) -> ctypes.POINTER(libpostal_language_classifier_response_t):
    return get_lib().libpostal_classify_language(address)


def libpostal_language_classifier_response_destroy(
    self_ptr: ctypes.POINTER(libpostal_language_classifier_response_t)
) -> None:
    return get_lib().libpostal_language_classifier_response_destroy(self_ptr)


def libpostal_get_near_dupe_hash_default_options() -> libpostal_near_dupe_hash_options_t:
    return get_lib().libpostal_get_near_dupe_hash_default_options()


def libpostal_near_dupe_name_hashes(
    name: bytes, normalize_options: libpostal_normalize_options_t,
    num_hashes: ctypes.POINTER(ctypes.c_size_t)
) -> ctypes.POINTER(ctypes.c_char_p):
    return get_lib().libpostal_near_dupe_name_hashes(name, normalize_options, num_hashes)


def libpostal_near_dupe_hashes(
    num_components: int, labels: ctypes.POINTER(ctypes.c_char_p),
    values: ctypes.POINTER(ctypes.c_char_p), options: libpostal_near_dupe_hash_options_t,
    num_hashes: ctypes.POINTER(ctypes.c_size_t)
) -> ctypes.POINTER(ctypes.c_char_p):
    return get_lib().libpostal_near_dupe_hashes(
        num_components, labels, values, options, num_hashes
    )


def libpostal_near_dupe_hashes_languages(
    num_components: int, labels: ctypes.POINTER(ctypes.c_char_p),
    values: ctypes.POINTER(ctypes.c_char_p), options: libpostal_near_dupe_hash_options_t,
    num_languages: int, languages: ctypes.POINTER(ctypes.c_char_p),
    num_hashes: ctypes.POINTER(ctypes.c_size_t)
) -> ctypes.POINTER(ctypes.c_char_p):
    return get_lib().libpostal_near_dupe_hashes_languages(
        num_components, labels, values, options, num_languages, languages, num_hashes
    )


def libpostal_place_languages(
    num_components: int, labels: ctypes.POINTER(ctypes.c_char_p),
    values: ctypes.POINTER(ctypes.c_char_p), num_languages: ctypes.POINTER(ctypes.c_size_t)
) -> ctypes.POINTER(ctypes.c_char_p):
    return get_lib().libpostal_place_languages(num_components, labels, values, num_languages)


def libpostal_get_default_duplicate_options() -> libpostal_duplicate_options_t:
    return get_lib().libpostal_get_default_duplicate_options()


def libpostal_get_duplicate_options_with_languages(
    num_languages: int, languages: ctypes.POINTER(ctypes.c_char_p)
) -> libpostal_duplicate_options_t:
    return get_lib().libpostal_get_duplicate_options_with_languages(num_languages, languages)


def libpostal_is_name_duplicate(
    value1: bytes, value2: bytes, options: libpostal_duplicate_options_t
) -> int:
    return get_lib().libpostal_is_name_duplicate(value1, value2, options)


def libpostal_is_street_duplicate(
    value1: bytes, value2: bytes, options: libpostal_duplicate_options_t
) -> int:
    return get_lib().libpostal_is_street_duplicate(value1, value2, options)


def libpostal_is_house_number_duplicate(
    value1: bytes, value2: bytes, options: libpostal_duplicate_options_t
) -> int:
    return get_lib().libpostal_is_house_number_duplicate(value1, value2, options)


def libpostal_is_po_box_duplicate(
    value1: bytes, value2: bytes, options: libpostal_duplicate_options_t
) -> int:
    return get_lib().libpostal_is_po_box_duplicate(value1, value2, options)


def libpostal_is_unit_duplicate(
    value1: bytes, value2: bytes, options: libpostal_duplicate_options_t
) -> int:
    return get_lib().libpostal_is_unit_duplicate(value1, value2, options)


def libpostal_is_floor_duplicate(
    value1: bytes, value2: bytes, options: libpostal_duplicate_options_t
) -> int:
    return get_lib().libpostal_is_floor_duplicate(value1, value2, options)


def libpostal_is_postal_code_duplicate(
    value1: bytes, value2: bytes, options: libpostal_duplicate_options_t
) -> int:
    return get_lib().libpostal_is_postal_code_duplicate(value1, value2, options)


def libpostal_is_toponym_duplicate(
    num_components1: int, labels1: ctypes.POINTER(ctypes.c_char_p),
    values1: ctypes.POINTER(ctypes.c_char_p), num_components2: int,
    labels2: ctypes.POINTER(ctypes.c_char_p), values2: ctypes.POINTER(ctypes.c_char_p),
    options: libpostal_duplicate_options_t
) -> int:
    return get_lib().libpostal_is_toponym_duplicate(
        num_components1, labels1, values1, num_components2, labels2, values2, options
    )


def libpostal_get_default_fuzzy_duplicate_options() -> libpostal_fuzzy_duplicate_options_t:
    return get_lib().libpostal_get_default_fuzzy_duplicate_options()


def libpostal_get_default_fuzzy_duplicate_options_with_languages(
    num_languages: int, languages: ctypes.POINTER(ctypes.c_char_p)
) -> libpostal_fuzzy_duplicate_options_t:
    return get_lib().libpostal_get_default_fuzzy_duplicate_options_with_languages(
        num_languages, languages
    )


def libpostal_is_name_duplicate_fuzzy(
    num_tokens1: int, tokens1: ctypes.POINTER(ctypes.c_char_p),
    token_scores1: ctypes.POINTER(ctypes.c_double), num_tokens2: int,
    tokens2: ctypes.POINTER(ctypes.c_char_p), token_scores2: ctypes.POINTER(ctypes.c_double),
    options: libpostal_fuzzy_duplicate_options_t
) -> libpostal_fuzzy_duplicate_status_t:
    return get_lib().libpostal_is_name_duplicate_fuzzy(
        num_tokens1, tokens1, token_scores1, num_tokens2, tokens2, token_scores2, options
    )


def libpostal_is_street_duplicate_fuzzy(
    num_tokens1: int, tokens1: ctypes.POINTER(ctypes.c_char_p),
    token_scores1: ctypes.POINTER(ctypes.c_double), num_tokens2: int,
    tokens2: ctypes.POINTER(ctypes.c_char_p), token_scores2: ctypes.POINTER(ctypes.c_double),
    options: libpostal_fuzzy_duplicate_options_t
) -> libpostal_fuzzy_duplicate_status_t:
    return get_lib().libpostal_is_street_duplicate_fuzzy(
        num_tokens1, tokens1, token_scores1, num_tokens2, tokens2, token_scores2, options
    )


def libpostal_tokenize(
    input_str: bytes, whitespace: bool, n: ctypes.POINTER(ctypes.c_size_t)
) -> ctypes.POINTER(libpostal_token_t):
    return get_lib().libpostal_tokenize(input_str, whitespace, n)


def libpostal_normalize_string_languages(
    input_str: bytes, options: int, num_languages: int, languages: ctypes.POINTER(ctypes.c_char_p)
) -> bytes:
    return get_lib().libpostal_normalize_string_languages(input_str, options, num_languages, languages)


def libpostal_normalize_string(input_str: bytes, options: int) -> bytes:
    return get_lib().libpostal_normalize_string(input_str, options)


def libpostal_normalized_tokens(
    input_str: bytes, string_options: int, token_options: int, whitespace: bool,
    n: ctypes.POINTER(ctypes.c_size_t)
) -> ctypes.POINTER(libpostal_normalized_token_t):
    return get_lib().libpostal_normalized_tokens(input_str, string_options, token_options, whitespace, n)


def libpostal_normalized_tokens_languages(
    input_str: bytes, string_options: int, token_options: int, whitespace: bool,
    num_languages: int, languages: ctypes.POINTER(ctypes.c_char_p), n: ctypes.POINTER(ctypes.c_size_t)
) -> ctypes.POINTER(libpostal_normalized_token_t):
    return get_lib().libpostal_normalized_tokens_languages(
        input_str, string_options, token_options, whitespace, num_languages, languages, n
    )
