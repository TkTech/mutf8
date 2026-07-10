"""
Benchmarks comparing the pure-Python and C encoders/decoders across realistic
inputs (ASCII, CJK, emoji, mixed) and payload sizes.

Marked ``slow``; run with ``pytest --runslow tests/test_benchmark.py``.
"""
import pytest

import mutf8.mutf8 as pymutf8
import mutf8.cmutf8 as cmutf8

# Short representative units, repeated to hit each target size. Ordered from
# the most common real-world case (ASCII JVM symbols) to the rarest.
_UNITS = {
    "ascii": "java/lang/Object;",           # 1-byte codepoints
    "cjk": "編碼測試字",                       # 3-byte codepoints
    "emoji": "🚀🎉",                          # 6-byte (surrogate pair) codepoints
    "mixed": "café ☕ item#42 shipped 🚚 ",   # 1/2/3/6-byte mix
}

# Target *encoded* sizes: 16b exposes per-call overhead, the rest throughput.
_SIZES = {"16b": 16, "1kb": 1024, "64kb": 64 * 1024}


def _scale(unit, target_bytes):
    reps = max(1, round(target_bytes / len(cmutf8.encode_modified_utf8(unit))))
    return unit * reps


# (content, size) -> decoded str and its MUTF-8 encoding.
STR_CORPORA = {
    (content, size): _scale(unit, nbytes)
    for content, unit in _UNITS.items()
    for size, nbytes in _SIZES.items()
}
BYTES_CORPORA = {
    key: cmutf8.encode_modified_utf8(text) for key, text in STR_CORPORA.items()
}

CORPORA = list(STR_CORPORA)
_CORPUS_IDS = [f"{content}-{size}" for content, size in CORPORA]
_IMPLS = (("py", pymutf8), ("c", cmutf8))
_IMPL_IDS = [name for name, _ in _IMPLS]


@pytest.mark.slow
@pytest.mark.parametrize("corpus", CORPORA, ids=_CORPUS_IDS)
@pytest.mark.parametrize("impl,module", _IMPLS, ids=_IMPL_IDS)
def test_decode(corpus, impl, module, benchmark):
    content, size = corpus
    data = BYTES_CORPORA[corpus]
    benchmark.group = f"decode {content}-{size}"
    benchmark.extra_info.update(impl=impl, encoded_bytes=len(data))
    result = benchmark(module.decode_modified_utf8, data)
    assert result == STR_CORPORA[corpus]


@pytest.mark.slow
@pytest.mark.parametrize("corpus", CORPORA, ids=_CORPUS_IDS)
@pytest.mark.parametrize("impl,module", _IMPLS, ids=_IMPL_IDS)
def test_encode(corpus, impl, module, benchmark):
    content, size = corpus
    text = STR_CORPORA[corpus]
    benchmark.group = f"encode {content}-{size}"
    benchmark.extra_info.update(impl=impl, encoded_bytes=len(BYTES_CORPORA[corpus]))
    result = benchmark(module.encode_modified_utf8, text)
    assert result == BYTES_CORPORA[corpus]
