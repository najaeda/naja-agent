# naja-mcp

## Setup

This repository wraps the upstream [Naja](https://github.com/najaeda/naja) project in an MCP server.
The server expects the Python package from the `thirdparty/naja` submodule to be available in your environment.

The quickest path is to build the vendored Naja sources with the provided helper script:

```bash
./build_naja.sh
```

If you want the script to install the common system dependencies for your platform first, run:

```bash
./build_naja.sh --install-deps
```

By default the build uses `thirdparty/naja/build/` and installs into `$NAJA_INSTALL` if that environment variable is set.
If `NAJA_INSTALL` is not set, the script uses a local install prefix inside the build directory.

On Ubuntu, the upstream Naja project expects these packages:

```bash
sudo apt-get install g++ libboost-dev python3.9-dev capnproto libcapnp-dev libtbb-dev pkg-config bison flex doxygen
```

Using nix-shell:

```bash
nix-shell -p cmake boost python3 doxygen capnproto bison flex pkg-config tbb_2021_8
```

On macOS with Homebrew:

```bash
brew install cmake doxygen capnp tbb bison flex boost
```

Make sure the Homebrew versions of `bison` and `flex` take precedence over the macOS defaults:

```bash
export PATH="/opt/homebrew/opt/flex/bin:/opt/homebrew/opt/bison/bin:$PATH"
```

If you want to build Naja manually instead of using the helper script, the upstream flow is:

```bash
export NAJA_INSTALL=<path_to_installation_dir>
mkdir build
cd build
cmake <path_to_naja_sources_dir> -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=$NAJA_INSTALL
make
make test
make install
```

For documentation:

```bash
cd build
make docs
make install
```

The MCP server entry point is `server.py`.
