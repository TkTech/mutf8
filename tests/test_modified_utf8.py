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
        (b'\xE2\x82\xA3', '\u20A3')
    )

    for original, decoded in pairs:
        assert pymutf8.decode_modified_utf8(original) == decoded
        assert pymutf8.encode_modified_utf8(decoded) == original

        assert cmutf8.decode_modified_utf8(original) == decoded
        assert cmutf8.encode_modified_utf8(decoded) == original
