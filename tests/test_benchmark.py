import pytest

import mutf8.mutf8 as pymutf8
import mutf8.cmutf8 as cmutf8


@pytest.mark.parametrize('group,decoder', (
    ('pymutf8', pymutf8.decode_modified_utf8),
    ('cmutf8', cmutf8.decode_modified_utf8)
))
@pytest.mark.slow
def test_decode(group, decoder, benchmark):
    """Compare the performance of the python and C decoders."""
    benchmark.group = 'MUTF-8 Decoding'
    benchmark.extra_info['group'] = group
    benchmark(decoder, b'\xED\xA0\xBD\xED\xB8\x88')


@pytest.mark.parametrize('group,encoder', (
    ('pymutf8', pymutf8.encode_modified_utf8),
    ('cmutf8', cmutf8.encode_modified_utf8)
))
@pytest.mark.slow
def test_encode(group, encoder, benchmark):
    """Compare the performance of the python and C encoders."""
    benchmark.group = 'MUTF-8 Encoding'
    benchmark.extra_info['group'] = group
    benchmark(encoder, '\U0001F608')
