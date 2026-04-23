# Prebuilt Libraries

This directory is intended to contain precompiled, prebuilt `libpostal` shared libraries for all target architectures. 

If binaries (`.so`, `.dylib`, `.dll`) are found in this directory structure (e.g., `linux-x64/libpostal.so`), `postalkit` will automatically load them directly from the package instead of attempting to fetch them from GitHub releases. 

You can manually populate these directories using the build scripts in the `../../build/` folder, or rely on the GitHub Actions workflow `build-prebuilt-libs.yml` to compile and commit them automatically.

### Supported Layout:
- `linux-x64/libpostal.so`
- `linux-arm64/libpostal.so`
- `macos-x64/libpostal.dylib`
- `macos-arm64/libpostal.dylib`
- `windows-x64/postal.dll`