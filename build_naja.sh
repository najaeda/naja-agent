#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$SCRIPT_DIR"
REPO_DIR="$ROOT_DIR/thirdparty/naja"
BUILD_DIR="$REPO_DIR/build"
INSTALL_DEPS=0
INSTALL_PREFIX="${NAJA_INSTALL:-$BUILD_DIR/install}"

usage() {
  cat <<'EOF'
Usage: build_naja.sh [--install-deps]

  --install-deps   Install system dependencies for the current OS before building.
EOF
}

install_dependencies() {
  case "$(uname -s)" in
    Linux)
      if command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update
        sudo apt-get install -y \
          g++ libboost-dev python3.9-dev capnproto libcapnp-dev libtbb-dev \
          pkg-config bison flex doxygen cmake git
      elif command -v dnf >/dev/null 2>&1; then
        sudo dnf install -y \
          gcc-c++ boost-devel python3-devel capnproto capnproto-devel tbb-devel \
          pkgconf-pkg-config bison flex doxygen cmake git
      else
        echo "Unsupported Linux package manager. Install the dependencies manually." >&2
        exit 1
      fi
      ;;
    Darwin)
      if ! command -v brew >/dev/null 2>&1; then
        echo "Homebrew is required on macOS to install dependencies." >&2
        exit 1
      fi
      brew install cmake doxygen capnp tbb bison flex boost
      echo 'If Homebrew bison/flex are not first in PATH, add:'
      echo 'export PATH="/opt/homebrew/opt/flex/bin:/opt/homebrew/opt/bison/bin:$PATH"'
      ;;
    *)
      echo "Automatic dependency installation is not configured for $(uname -s)." >&2
      exit 1
      ;;
  esac
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --install-deps)
      INSTALL_DEPS=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ "$INSTALL_DEPS" -eq 1 ]]; then
  install_dependencies
fi

cpu_count() {
  if command -v nproc >/dev/null 2>&1; then
    nproc
  elif command -v sysctl >/dev/null 2>&1; then
    sysctl -n hw.ncpu
  else
    echo 1
  fi
}

git -C "$ROOT_DIR" submodule update --init --recursive -- thirdparty/naja

mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX="$INSTALL_PREFIX"
cmake --build . --parallel "$(cpu_count)"

if [[ -n "${NAJA_RUN_TESTS:-}" ]]; then
  ctest --output-on-failure
fi

echo "Build complete: $BUILD_DIR"
echo "Install prefix: $INSTALL_PREFIX"