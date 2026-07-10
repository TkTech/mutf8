def test_issue_1(encoder, decoder):
    """
    Ensure we do not regress on https://github.com/TkTech/mutf8/issues/1.

    Two issues found here:

        1. Python-based decoder could hit an infinite loop, since it didn't
           *always* increment s_ix on an iteration.
        2. C & Python decoders would incorrectly decode the `sample` below,
           because the logic for surrogate pair decoding made the incorrect
           assumption that we could short-circuit when b1 == 0xED.
    """

    # b'[\xea\xb0\x80 \xeb\x82\x98 \xeb\x8b\xa4 \xeb\x9d\xbc \xeb\xa7\x88
    # \xeb\xb0\x94  \xec\x82\xac  \xec\x95\x84\xec\x9e\x90  \xec\xb0\xa8
    # \xec\xb9\xb4 \xed\x83\x80 \xed\x8c\x8c \xed\x95\x98]'
    sample = (
        u'[\uAC00 \uB098 \uB2E4 \uB77C \uB9C8 \uBC14  \uC0AC  \uC544'
        u'\uC790  \uCC28 \uCE74 \uD0C0 \uD30C \uD558]'
    )

    encoded = encoder(sample)
    decoded = decoder(encoded)

    assert sample == decoded


def test_issue_3(encoder, decoder):
    """
    Underallocation due to an incorrect assumption on the maximum expansion
    of an encoded string.
    """
    str = '黑人抬棺組裝包'
    assert decoder(encoder(str)) == str


# Supplementary characters and their *correct* MUTF-8 encoding, cross-checked
# against Java's DataOutputStream.writeUTF, Android/DEX and Rust's
# residua-mutf8. See https://github.com/TkTech/mutf8/issues/5 and /issues/6.
ISSUE_5_6_VECTORS = (
    ('\U00010000', b'\xed\xa0\x80\xed\xb0\x80'),
    ('\U00020000', b'\xed\xa1\x80\xed\xb0\x80'),
    ('\U00040000', b'\xed\xa3\x80\xed\xb0\x80'),
    ('\U00080000', b'\xed\xa7\x80\xed\xb0\x80'),
    ('\U00100000', b'\xed\xaf\x80\xed\xb0\x80'),
    ('\U0010FFFF', b'\xed\xaf\xbf\xed\xbf\xbf'),
    ('\U00010401', b'\xed\xa0\x81\xed\xb0\x81'),   # residua-mutf8 example
    ('\U0001F4CB', b'\xed\xa0\xbd\xed\xb3\x8b'),   # 📋
    ('\U0001F3F9', b'\xed\xa0\xbc\xed\xbf\xb9'),   # 🏹
    ('\U0001F41F', b'\xed\xa0\xbd\xed\xb0\x9f'),   # 🐟
)


def test_issue_5_and_6(encoder, decoder):
    """
    Supplementary characters (> U+FFFF) must be encoded as a UTF-16 surrogate
    pair after subtracting 0x10000, matching Java/Android/CESU-8. Previously
    the 0x10000 offset was omitted on encode (and compensated with a bitwise
    OR on decode), producing non-standard bytes and losing data for plane 16.

    https://github.com/TkTech/mutf8/issues/5
    https://github.com/TkTech/mutf8/issues/6
    """
    for text, expected in ISSUE_5_6_VECTORS:
        assert encoder(text) == expected, hex(ord(text))
        # Decoding standard MUTF-8 must recover the original codepoint.
        assert decoder(expected) == text, hex(ord(text))
        # And a full round-trip must be lossless across the whole range.
        assert decoder(encoder(text)) == text, hex(ord(text))


def test_issue_4(decoder, encoder):
    """
    A lone (unpaired) high surrogate is legal in a Java string and is encoded
    as a single 3-byte sequence (0xED 0xA0-0xAF ...). The decoder must not
    assume every 0xED 0xAx sequence begins a six-byte pair; when no low
    surrogate follows (including at end-of-input) it must decode a 3-byte
    lone surrogate instead of raising "input too short".

    https://github.com/TkTech/mutf8/issues/4
    """
    # A lone high surrogate at end-of-input (previously raised spuriously).
    assert decoder(b'\xed\xa1\x80') == '\ud840'
    # A lone low surrogate, likewise.
    assert decoder(b'\xed\xb0\x80') == '\udc00'
    # A high surrogate followed by non-surrogate data, not a pair.
    assert decoder(b'\xed\xa1\x80AB') == '\ud840AB'
    # Two high surrogates in a row: each is its own 3-byte codepoint.
    assert decoder(b'\xed\xa1\x80\xed\xa1\x80') == '\ud840\ud840'
    # Lone surrogates must survive a round-trip.
    for cp in (0xD800, 0xD840, 0xDBFF, 0xDC00, 0xDFFF):
        assert decoder(encoder(chr(cp))) == chr(cp), hex(cp)
