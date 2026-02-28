"""
_ncdb_accel_build.py — cffi ABI build script for ncdb_accel.c

Compiles ncdb_accel.c into a shared library (_ncdb_accel.so) that can be
loaded at runtime via cffi's dlopen() without any install-time compilation
step.

Usage::

    python -m ucis.ncdb._accel._ncdb_accel_build

The resulting .so is placed next to this file so that __init__.py can find
it with a relative path.

Prerequisites:
    pip install cffi        (usually already installed)
    gcc or clang on PATH    (standard on Linux/macOS)

Troubleshooting:
    - If gcc is not found, install build-essential (Debian/Ubuntu) or
      equivalent.
    - On macOS with Apple Silicon, ensure the Xcode command-line tools are
      installed: ``xcode-select --install``.
    - Pass CFLAGS / CC environment variables to override compiler flags.
"""

import os
import sys
import cffi

# Path to this directory (where the .so will be written)
_HERE = os.path.dirname(os.path.abspath(__file__))
_C_SOURCE = os.path.join(_HERE, "ncdb_accel.c")
_SO_NAME = "_ncdb_accel"

CDEF = r"""
int  ncdb_encode_varints(const uint64_t *values, size_t count,
                         uint8_t *out_buf, size_t out_cap);
int  ncdb_decode_varints(const uint8_t *data, size_t data_len,
                         size_t offset, size_t count,
                         uint64_t *out_values);
void ncdb_add_uint32_arrays(const uint32_t *a, const uint32_t *b,
                            size_t count, uint32_t *out);
"""


def build():
    ffi = cffi.FFI()
    ffi.cdef(CDEF)
    with open(_C_SOURCE) as f:
        source = f.read()
    ffi.set_source(
        _SO_NAME,
        source,
        extra_compile_args=["-O2", "-march=native"],
    )
    # Build into _HERE so the .so lives alongside __init__.py
    ffi.compile(tmpdir=_HERE, verbose=True)
    print(f"Built {_SO_NAME}.so in {_HERE}")


if __name__ == "__main__":
    build()
