# PostalKit


[![PyPI version](https://img.shields.io/pypi/v/postalkit.svg?style=flat-square)](https://pypi.org/project/postalkit/) 
[![Downloads](https://static.pepy.tech/badge/postalkit)](https://pepy.tech/projects/postalkit) 
[![Python Versions](https://img.shields.io/pypi/pyversions/postalkit.svg?style=flat-square)](https://pypi.org/project/postalkit/) 
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](https://opensource.org/licenses/MIT) 
[![Wheel](https://img.shields.io/pypi/wheel/postalkit?style=flat-square)](https://pypi.org/project/postalkit/) 
[![Status](https://img.shields.io/pypi/status/postalkit?style=flat-square)](https://pypi.org/project/postalkit/)  


**Zero-setup, one-command install Python package for libpostal. Designed as a strict 1:1 C-FFI wrapper.**

Parsing international street addresses shouldn't require a Ph.D. in C compilation. `postalkit` provides the ultimate zero-friction environment to run the amazing [libpostal](https://github.com/openvenues/libpostal) C library natively in Python, without abstracting away its raw power. 

Like `FFI` implementations in PHP, this exposes the exact C structs, constants, and functions so that you can port C logic directly to Python.

## ✨ Why PostalKit?

The standard `postal` package requires you to manually compile C code, install `autoconf`, `make`, `pkg-config`, and manually download a ~2GB machine learning model.

**PostalKit handles everything automatically:**
- ✅ **Zero C compilation:** Downloads pre-compiled `libpostal` shared binaries for your OS and architecture.
- ✅ **Auto-downloads models:** Fetches the required libpostal ML models transparently on first use.
- ✅ **Strict 1:1 C Mapping:** Exposes `libpostal_parse_address`, `libpostal_expand_address`, and all `ctypes` structs exactly as defined in `libpostal.h`.
- ✅ **Cross-platform:** Works on Linux (x86_64, arm64), macOS (Intel, Apple Silicon), and Windows.

## 📦 Installation

```bash
pip install postalkit
```

## 🚀 Quickstart

Because this is a **true 1:1 FFI wrapper**, you use the exact function names and C-structs defined in the upstream libpostal C headers. Memory is managed precisely as it is in C.

```python
import ctypes
import postalkit

# 1. Get the C-struct for parser options
options = postalkit.libpostal_get_address_parser_default_options()

# 2. Call the C-function directly (strings must be passed as bytes)
address = b"221B Baker St London"
response_ptr = postalkit.libpostal_parse_address(address, options)

# 3. Access the raw C-arrays
response = response_ptr.contents
for i in range(response.num_components):
    component = response.components[i].decode('utf-8')
    label = response.labels[i].decode('utf-8')
    print(f"{label}: {component}")

# 4. Manually destroy the C pointer to free memory, exactly as in C!
postalkit.libpostal_address_parser_response_destroy(response_ptr)
```

## 🧠 True 1:1 FFI Coverage

This package leaves absolutely nothing behind. It natively exposes:
- **All 46 C functions** (`libpostal_tokenize`, `libpostal_classify_language`, `libpostal_is_name_duplicate_fuzzy`, etc.)
- **All 10 C Structs** (`libpostal_normalize_options_t`, `libpostal_duplicate_options_t`, etc.)
- **All 42 C Constants & Bitwise Flags** (`LIBPOSTAL_ADDRESS_HOUSE_NUMBER`, `LIBPOSTAL_NORMALIZE_TOKEN_DELETE_HYPHENS`, etc.)

You can directly port any libpostal C/C++ tutorial code into Python line-by-line.

## 🛠️ Advanced Usage

**Pre-downloading assets (e.g., for Docker images or CI):**
```python
from postalkit.data.manager import ensure_all_assets
ensure_all_assets()
```

## 📄 License

MIT License. Developed with 💙 by [Jayesh Mepani](https://github.com/jayeshmepani).
