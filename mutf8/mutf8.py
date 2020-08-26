def decode_modified_utf8(s: bytes) -> str:
    """
    Decodes a bytestring containing modified UTF-8 as defined in section
    4.4.7 of the JVM specification.

    :param s: bytestring to be converted.
    :returns: A unicode representation of the original string.
    """
    s = bytearray(s)
    buff = []
    ix = 0
    length = len(s)

    while ix < length:
        x = s[ix]

        if x == 0:
            raise UnicodeDecodeError(
                'mutf-8',
                s,
                ix - 1,
                ix - 1,
                'mutf-8 does not allow NULL bytes.',
            )
        elif x & 0b10000000 == 0b00000000:
            # ASCII
            x = x & 0x7F
            ix += 1
        elif x & 0b11100000 == 0b11000000:
            # Two-byte codepoint.
            if ix + 1 >= length:
                raise UnicodeDecodeError(
                    'mutf-8',
                    s,
                    ix - 1,
                    ix - 1,
                    'Incomplete two-byte codepoint.',
                )

            x = (
                (s[ix + 0] & 0b00011111) << 0x06 |
                (s[ix + 1] & 0b00111111)
            )

            ix += 2
        elif x == 0b11101101:
            # Six-byte codepoint.
            if ix + 5 >= length:
                raise UnicodeDecodeError(
                    'mutf-8',
                    s,
                    ix - 1,
                    ix - 1,
                    'Incomplete six-byte codepoint.'
                )

            x = (
                0x10000 |
                (s[ix + 1] & 0b00001111) << 0x10 |
                (s[ix + 2] & 0b00111111) << 0x0A |
                (s[ix + 4] & 0b00001111) << 0x06 |
                (s[ix + 5] & 0b00111111)
            )

            ix += 6
        elif x >> 4 == 0b1110:
            # Three-byte codepoint.
            if ix + 2 >= length:
                raise UnicodeDecodeError(
                    'mutf-8',
                    s,
                    ix - 1,
                    ix - 1,
                    'Incomplete three-byte codepoint.'
                )

            x = (
                (s[ix + 0] & 0b00001111) << 0x0C |
                (s[ix + 1] & 0b00111111) << 0x06 |
                (s[ix + 2] & 0b00111111)
            )

            ix += 3

        buff.append(x)
    return u''.join(chr(b) for b in buff)


def encode_modified_utf8(u: str) -> bytes:
    """
    Encodes a unicode string as modified UTF-8 as defined in section 4.4.7
    of the JVM specification.

    :param u: unicode string to be converted.
    :returns: A decoded bytearray.
    """
    final_string = bytearray()

    for c in (ord(char) for char in u):
        if c == 0x00:
            # NULL byte encoding shortcircuit.
            final_string.extend([0xC0, 0x80])
        elif c <= 0x7F:
            # ASCII
            final_string.append(c)
        elif c <= 0x7FF:
            # Two-byte codepoint.
            final_string.extend([
                (0xC0 | (0x1F & (c >> 0x06))),
                (0x80 | (0x3F & c))
            ])
        elif c <= 0xFFFF:
            # Three-byte codepoint.
            final_string.extend([
                (0xE0 | (0x0F & (c >> 0x0C))),
                (0x80 | (0x3F & (c >> 0x06))),
                (0x80 | (0x3F & c))
            ])
        else:
            # Six-byte codepoint.
            final_string.extend([
                0xED,
                0xA0 | ((c >> 0x10) & 0x0F),
                0x80 | ((c >> 0x0A) & 0x3f),
                0xED,
                0xb0 | ((c >> 0x06) & 0x0f),
                0x80 | (c & 0x3f)
            ])

    return bytes(final_string)
