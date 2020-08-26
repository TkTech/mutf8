import pytest

import mutf8.mutf8 as pymutf8
import mutf8.cmutf8 as cmutf8


def test_decode_encode_utf8():
    """
    Test encoding and decoding of Modified UTF8 (MUTF-8), a CESU-8 variant with
    modified 0x00 encoding.
    """
    pairs = (
        # Embedded NULL
        (b'\x31\xC0\x80\x32', '1\x002'),
        # "two-times-three" codepoint.
        (b'\xED\xA0\xBD\xED\xB8\x88', '\U0001F608'),
        # 2-byte codepoint.
        (b'\xC2\xB6', '\u00B6'),
        # 3-byte codepoint.
        (b'\xE2\x82\xA3', '\u20A3')
    )

    for original, decoded in pairs:
        assert pymutf8.decode_modified_utf8(original) == decoded
        assert pymutf8.encode_modified_utf8(decoded) == original

        assert cmutf8.decode_modified_utf8(original) == decoded
        assert cmutf8.encode_modified_utf8(decoded) == original


@pytest.mark.parametrize('decoder', [
    pymutf8.decode_modified_utf8,
    cmutf8.decode_modified_utf8
])
def test_decode_bad_mutf8(decoder):
    """Ensure we do the right thing when we encounter invalid MUTF-8."""
    # There should never be a null byte in a MUTF-8 string. It's the
    # entire point of using MUTF-8.
    with pytest.raises(UnicodeDecodeError) as excinfo:
        decoder(b'\x00')

    assert 'NULL bytes' in excinfo.value.reason

    # Start of a two-byte codepoint without the sibling.
    with pytest.raises(UnicodeDecodeError) as excinfo:
        decoder(b'\xC2')

    assert 'two-byte' in excinfo.value.reason

    # Start of a six-byte codepoint without the sibling.
    with pytest.raises(UnicodeDecodeError) as excinfo:
        decoder(b'\xED')

    assert 'six-byte' in excinfo.value.reason

    # Start of a three-byte codepoint without the sibling.
    with pytest.raises(UnicodeDecodeError) as excinfo:
        decoder(b'\xE2')

    assert 'three-byte' in excinfo.value.reason
