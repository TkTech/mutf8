import pytest

import mutf8.mutf8 as pymutf8
import mutf8.cmutf8 as cmutf8


def _pairs(*args):
    for a, b in args:
        yield chr(a), bytearray(b)


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


@pytest.mark.parametrize('module', [pymutf8, cmutf8])
def test_two_byte(module):
    """
    Test two-byte encoding and decoding.

    Test data taken from py2jdbc.
    """
    pairs = _pairs(
        (0x0080, (0xc2, 0x80)),
        (0x0081, (0xc2, 0x81)),
        (0x0082, (0xc2, 0x82)),
        (0x0084, (0xc2, 0x84)),
        (0x0088, (0xc2, 0x88)),
        (0x0090, (0xc2, 0x90)),
        (0x00a0, (0xc2, 0xa0)),
        (0x00c0, (0xc3, 0x80)),
        (0x0180, (0xc6, 0x80)),
        (0x0280, (0xca, 0x80)),
        (0x0480, (0xd2, 0x80)),
        (0x0481, (0xd2, 0x81)),
        (0x0483, (0xd2, 0x83)),
        (0x0487, (0xd2, 0x87)),
        (0x048f, (0xd2, 0x8f)),
        (0x049f, (0xd2, 0x9f)),
        (0x04af, (0xd2, 0xaf)),
        (0x04bf, (0xd2, 0xbf)),
        (0x04ff, (0xd3, 0xbf)),
        (0x05ff, (0xd7, 0xbf)),
        (0x05ff, (0xd7, 0xbf)),
        (0x07ff, (0xdf, 0xbf))
    )

    for decoded, original in pairs:
        assert module.decode_modified_utf8(original) == decoded
        assert module.encode_modified_utf8(decoded) == original


@pytest.mark.parametrize('module', [pymutf8, cmutf8])
def test_three_byte(module):
    """
    Test three-byte encoding and decoding.

    Test data taken from py2jdbc.
    """
    pairs = _pairs(
        (0x0800, (0xe0, 0xa0, 0x80)),
        (0x0801, (0xe0, 0xa0, 0x81)),
        (0x0802, (0xe0, 0xa0, 0x82)),
        (0x0804, (0xe0, 0xa0, 0x84)),
        (0x0808, (0xe0, 0xa0, 0x88)),
        (0x0810, (0xe0, 0xa0, 0x90)),
        (0x0820, (0xe0, 0xa0, 0xa0)),
        (0x0840, (0xe0, 0xa1, 0x80)),
        (0x0880, (0xe0, 0xa2, 0x80)),
        (0x0900, (0xe0, 0xa4, 0x80)),
        (0x0a00, (0xe0, 0xa8, 0x80)),
        (0x0c00, (0xe0, 0xb0, 0x80)),
        (0x1800, (0xe1, 0xa0, 0x80)),
        (0x2800, (0xe2, 0xa0, 0x80)),
        (0x4800, (0xe4, 0xa0, 0x80)),
        (0x8800, (0xe8, 0xa0, 0x80)),
        (0x8801, (0xe8, 0xa0, 0x81)),
        (0x8803, (0xe8, 0xa0, 0x83)),
        (0x8807, (0xe8, 0xa0, 0x87)),
        (0x880f, (0xe8, 0xa0, 0x8f)),
        (0x881f, (0xe8, 0xa0, 0x9f)),
        (0x883f, (0xe8, 0xa0, 0xbf)),
        (0x887f, (0xe8, 0xa1, 0xbf)),
        (0x88ff, (0xe8, 0xa3, 0xbf)),
        (0x89ff, (0xe8, 0xa7, 0xbf)),
        (0x8bff, (0xe8, 0xaf, 0xbf)),
        (0x8fff, (0xe8, 0xbf, 0xbf)),
        (0x9fff, (0xe9, 0xbf, 0xbf)),
        (0xbfff, (0xeb, 0xbf, 0xbf)),
        (0xffff, (0xef, 0xbf, 0xbf))
    )

    for decoded, original in pairs:
        assert module.decode_modified_utf8(original) == decoded
        assert module.encode_modified_utf8(decoded) == original


@pytest.mark.parametrize('module', [pymutf8])
def test_six_byte(module):
    """
    Test six-byte encoding and decoding.

    Test data taken from py2jdbc.
    """
    pairs = _pairs(
        (0x10000, (0xed, 0xa1, 0x80, 0xed, 0xb0, 0x80)),
        (0x10001, (0xed, 0xa1, 0x80, 0xed, 0xb0, 0x81)),
        (0x10002, (0xed, 0xa1, 0x80, 0xed, 0xb0, 0x82)),
        (0x10004, (0xed, 0xa1, 0x80, 0xed, 0xb0, 0x84)),
        (0x10008, (0xed, 0xa1, 0x80, 0xed, 0xb0, 0x88)),
        (0x10010, (0xed, 0xa1, 0x80, 0xed, 0xb0, 0x90)),
        (0x10020, (0xed, 0xa1, 0x80, 0xed, 0xb0, 0xa0)),
        (0x10040, (0xed, 0xa1, 0x80, 0xed, 0xb1, 0x80)),
        (0x10080, (0xed, 0xa1, 0x80, 0xed, 0xb2, 0x80)),
        (0x10100, (0xed, 0xa1, 0x80, 0xed, 0xb4, 0x80)),
        (0x10200, (0xed, 0xa1, 0x80, 0xed, 0xb8, 0x80)),
        (0x10400, (0xed, 0xa1, 0x81, 0xed, 0xb0, 0x80)),
        (0x10800, (0xed, 0xa1, 0x82, 0xed, 0xb0, 0x80)),
        (0x11000, (0xed, 0xa1, 0x84, 0xed, 0xb0, 0x80)),
        (0x12000, (0xed, 0xa1, 0x88, 0xed, 0xb0, 0x80)),
        (0x14000, (0xed, 0xa1, 0x90, 0xed, 0xb0, 0x80)),
        (0x18000, (0xed, 0xa1, 0xa0, 0xed, 0xb0, 0x80)),
        (0x30000, (0xed, 0xa3, 0x80, 0xed, 0xb0, 0x80)),
        (0x50000, (0xed, 0xa5, 0x80, 0xed, 0xb0, 0x80)),
        (0x90000, (0xed, 0xa9, 0x80, 0xed, 0xb0, 0x80)),
        (0x10003, (0xed, 0xa1, 0x80, 0xed, 0xb0, 0x83)),
        (0x10007, (0xed, 0xa1, 0x80, 0xed, 0xb0, 0x87)),
        (0x1000f, (0xed, 0xa1, 0x80, 0xed, 0xb0, 0x8f)),
        (0x1001f, (0xed, 0xa1, 0x80, 0xed, 0xb0, 0x9f)),
        (0x1003f, (0xed, 0xa1, 0x80, 0xed, 0xb0, 0xbf)),
        (0x1007f, (0xed, 0xa1, 0x80, 0xed, 0xb1, 0xbf)),
        (0x100ff, (0xed, 0xa1, 0x80, 0xed, 0xb3, 0xbf)),
        (0x101ff, (0xed, 0xa1, 0x80, 0xed, 0xb7, 0xbf)),
        (0x103ff, (0xed, 0xa1, 0x80, 0xed, 0xbf, 0xbf)),
        (0x107ff, (0xed, 0xa1, 0x81, 0xed, 0xbf, 0xbf)),
        (0x10fff, (0xed, 0xa1, 0x83, 0xed, 0xbf, 0xbf)),
        (0x11fff, (0xed, 0xa1, 0x87, 0xed, 0xbf, 0xbf)),
        (0x13fff, (0xed, 0xa1, 0x8f, 0xed, 0xbf, 0xbf)),
        (0x17fff, (0xed, 0xa1, 0x9f, 0xed, 0xbf, 0xbf)),
        (0x1ffff, (0xed, 0xa1, 0xbf, 0xed, 0xbf, 0xbf)),
        (0x3ffff, (0xed, 0xa3, 0xbf, 0xed, 0xbf, 0xbf)),
        (0x7ffff, (0xed, 0xa7, 0xbf, 0xed, 0xbf, 0xbf)),
        (0xfffff, (0xed, 0xaf, 0xbf, 0xed, 0xbf, 0xbf))
    )

    for decoded, original in pairs:
        assert module.decode_modified_utf8(original) == decoded
        assert module.encode_modified_utf8(decoded) == original
