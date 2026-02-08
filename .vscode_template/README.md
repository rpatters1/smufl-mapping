# VS Code Templates

These templates provide starter VS Code configs for macOS, Linux, and Windows.
They default to building with generated headers enabled
(`-DSMUFL_MAPPING_USE_PREGENERATED_HEADERS=OFF`).

## Setup

1. Pick the template folder for your OS:
   - `macos/`
   - `linux/`
   - `windows/`
2. Copy the files into your workspace `.vscode/` directory:

```bash
cp .vscode_template/<os>/*.json .vscode/
```

3. Adjust paths and debugger settings as needed for your machine.

Notes:
- The `configure` task sets the CMake generator and the SMuFL mapping option.
- The `build` task depends on `configure`.
- The `CTest` launch config runs tests from the build directory.
- On Windows, the launch config assumes a `Release` configuration.
