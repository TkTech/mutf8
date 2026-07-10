![CI](https://github.com/TkTech/mutf8/actions/workflows/release.yml/badge.svg)

# mutf-8

This package contains simple pure-python as well as C encoders and decoders for
the MUTF-8 character encoding.

These days, you'll most likely encounter MUTF-8 when working on files or
protocols related to the JVM. Strings in a Java `.class` file are encoded using
MUTF-8, strings passed by the JNI, as well as strings exported by the object
serializer.

This library was extracted from [Lawu][], a Python library for working with JVM
class files.

## Installation

Prebuilt binary packages are available for most platforms and Python versions.
Install the package from PyPi:

```
pip install mutf8
```

## Usage

Encoding and decoding is simple:

```python
from mutf8 import encode_modified_utf8, decode_modified_utf8

unicode = decode_modified_utf8(byte_like_object)
bytes = encode_modified_utf8(unicode)
```

This module *does not* register itself globally as a codec, since importing
should be side-effect-free.

## Benchmarks

The C extension is dramatically faster than the pure-Python fallback — from
~10× on tiny strings (where per-call overhead dominates) to several hundred
times on realistic payloads, and over 1000× when encoding large ASCII.

<!-- BENCHMARK START -->

### MUTF-8 Decoding

| Input | C | Python | Speedup |
|-------|---|--------|--------:|
| ASCII (16 B) | 81.5 ± 26 ns | 1.04 ± 0.18 µs | 13× |
| ASCII (1 KB) | 185 ± 38 ns | 65.7 ± 8.5 µs | 356× |
| ASCII (64 KB) | 5.58 ± 0.66 µs | 4.35 ± 0.23 ms | 780× |
| CJK (16 B) | 127 ± 15 ns | 1.33 ± 0.15 µs | 10× |
| CJK (1 KB) | 681 ± 117 ns | 99.3 ± 9.4 µs | 146× |
| CJK (64 KB) | 31.8 ± 3.3 µs | 6.28 ± 0.063 ms | 198× |
| Emoji (16 B) | 100 ± 21 ns | 882 ± 122 ns | 9× |
| Emoji (1 KB) | 538 ± 119 ns | 79.6 ± 6.9 µs | 148× |
| Emoji (64 KB) | 26.2 ± 4.1 µs | 5.32 ± 0.13 ms | 203× |
| Mixed (16 B) | 118 ± 27 ns | 2.17 ± 0.16 µs | 18× |
| Mixed (1 KB) | 860 ± 162 ns | 76.7 ± 9.2 µs | 89× |
| Mixed (64 KB) | 38 ± 5 µs | 5.3 ± 0.48 ms | 139× |

### MUTF-8 Encoding

| Input | C | Python | Speedup |
|-------|---|--------|--------:|
| ASCII (16 B) | 70.5 ± 5.8 ns | 1.23 ± 0.15 µs | 18× |
| ASCII (1 KB) | 109 ± 16 ns | 49 ± 6.2 µs | 449× |
| ASCII (64 KB) | 1.55 ± 0.27 µs | 2.93 ± 0.19 ms | 1889× |
| CJK (16 B) | 81.4 ± 12 ns | 2.02 ± 0.26 µs | 25× |
| CJK (1 KB) | 624 ± 127 ns | 108 ± 16 µs | 173× |
| CJK (64 KB) | 32.5 ± 2.9 µs | 6.8 ± 0.24 ms | 209× |
| Emoji (16 B) | 73 ± 10 ns | 1.17 ± 0.12 µs | 16× |
| Emoji (1 KB) | 621 ± 76 ns | 67 ± 8.5 µs | 108× |
| Emoji (64 KB) | 33.3 ± 6 µs | 3.98 ± 0.12 ms | 119× |
| Mixed (16 B) | 108 ± 97 ns | 2.48 ± 0.35 µs | 23× |
| Mixed (1 KB) | 1.39 ± 0.29 µs | 63.3 ± 3.5 µs | 45× |
| Mixed (64 KB) | 81.2 ± 14 µs | 3.91 ± 0.093 ms | 48× |

<!-- BENCHMARK END -->

## C Extension

The C extension is optional. If a binary package is not available, or a C
compiler is not present, the pure-python version will be used instead. If you
want to ensure you're using the C version, import it directly:

```python
from mutf8.cmutf8 import decode_modified_utf8

decode_modified_utf(b'\xED\xA1\x80\xED\xB0\x80')
```

[Lawu]: https://github.com/tktech/lawu
