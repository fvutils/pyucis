/*
 * ncdb_accel.c — C acceleration for NCDB varint encoding/decoding
 * and element-wise uint32 array addition.
 *
 * Callable via cffi (ABI mode).  No external library dependencies.
 * All functions operate on caller-provided buffers; no heap allocation.
 *
 * Build via _ncdb_accel_build.py:
 *   python -m ucis.ncdb._accel._ncdb_accel_build
 */

#include <stdint.h>
#include <stddef.h>
#include <string.h>

/* ── ncdb_encode_varints ──────────────────────────────────────────────────
 *
 * Encode 'count' unsigned 64-bit integers from 'values' as LEB128 varints
 * into 'out_buf'.  'out_cap' is the capacity of out_buf in bytes.
 *
 * Returns the number of bytes written, or -1 if out_buf would overflow.
 */
int ncdb_encode_varints(const uint64_t *values, size_t count,
                        uint8_t *out_buf, size_t out_cap)
{
    size_t pos = 0;
    for (size_t i = 0; i < count; i++) {
        uint64_t v = values[i];
        do {
            if (pos >= out_cap) return -1;
            uint8_t byte = v & 0x7F;
            v >>= 7;
            if (v != 0) byte |= 0x80;
            out_buf[pos++] = byte;
        } while (v != 0);
    }
    return (int)pos;
}


/* ── ncdb_decode_varints ──────────────────────────────────────────────────
 *
 * Decode 'count' unsigned LEB128 varints from 'data' starting at byte
 * 'offset'.  Decoded values are written into 'out_values' (uint64_t[count]).
 *
 * Returns the new offset (byte position after the last decoded varint),
 * or -1 if the buffer is too short.
 */
int ncdb_decode_varints(const uint8_t *data, size_t data_len,
                        size_t offset, size_t count,
                        uint64_t *out_values)
{
    for (size_t i = 0; i < count; i++) {
        uint64_t result = 0;
        int shift = 0;
        for (;;) {
            if (offset >= data_len) return -1;
            uint8_t byte = data[offset++];
            result |= (uint64_t)(byte & 0x7F) << shift;
            shift += 7;
            if (!(byte & 0x80)) break;
        }
        out_values[i] = result;
    }
    return (int)offset;
}


/* ── ncdb_add_uint32_arrays ───────────────────────────────────────────────
 *
 * Element-wise addition: out[i] = a[i] + b[i] for i in [0, count).
 * 'out' may alias 'a' or 'b' (safe: only reads before writing same slot).
 * Overflow wraps modulo 2^32.
 */
void ncdb_add_uint32_arrays(const uint32_t *a, const uint32_t *b,
                            size_t count, uint32_t *out)
{
    for (size_t i = 0; i < count; i++) {
        out[i] = a[i] + b[i];
    }
}
