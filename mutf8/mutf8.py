def decode_modified_utf8(s: bytes) -> str:
    """
    Decodes a bytestring containing modified UTF-8 as defined in section
    4.4.7 of the JVM specification.

    :param s: bytestring to be converted.
    :returns: A unicode representation of the original string.
    """
    s_out = []
    s_len = len(s)
    s_ix = 0

    while s_ix < s_len:
        b1 = s[s_ix]
        s_ix += 1

        if b1 == 0:
            raise UnicodeDecodeError(
                'mutf-8',
                s,
                s_ix - 1,
                s_ix,
                'Embedded NULL byte in input.'
            )
        if b1 < 0x80:
            # ASCII/one-byte codepoint.
            s_out.append(chr(b1))
        elif (b1 & 0xE0) == 0xC0:
            # Two-byte codepoint.
            if s_ix >= s_len:
                raise UnicodeDecodeError(
                        'mutf-8',
                        s,
                        s_ix - 1,
                        s_ix,
                        '2-byte codepoint started, but input too short to'
                        ' finish.'
                    )

            s_out.append(
                chr(
                    (b1 & 0x1F) << 0x06 |
                    (s[s_ix] & 0x3F)
                )
            )
            s_ix += 1
        elif (b1 & 0xF0) == 0xE0:
            # Three-byte codepoint.
            if s_ix + 1 >= s_len:
                raise UnicodeDecodeError(
                        'mutf-8',
                        s,
                        s_ix - 1,
                        s_ix,
                        '3-byte or 6-byte codepoint started, but input too'
                        ' short to finish.'
                    )

            b2 = s[s_ix]
            b3 = s[s_ix + 1]

            if (b1 == 0xED and (b2 & 0xF0) == 0xA0 and s_ix + 4 < s_len
                    and s[s_ix + 2] == 0xED and (s[s_ix + 3] & 0xF0) == 0xB0):
                # Six-byte codepoint: a supplementary character written as a
                # UTF-16 surrogate pair, each half encoded as its own 3-byte
                # sequence. Only take this branch once we've confirmed a low
                # surrogate actually follows; otherwise `b1 b2 b3` is a lone
                # (unpaired) surrogate and is decoded as a normal 3-byte
                # codepoint below.
                b5 = s[s_ix + 3]
                b6 = s[s_ix + 4]
                s_out.append(
                    chr(
                        0x10000 +
                        ((b2 & 0x0F) << 0x10 |
                         (b3 & 0x3F) << 0x0A |
                         (b5 & 0x0F) << 0x06 |
                         (b6 & 0x3F))
                    )
                )
                s_ix += 5
                continue

            # Regular three-byte codepoint. This also covers lone/unpaired
            # surrogates, each of which is encoded as a single 3-byte sequence.
            s_out.append(
                chr(
                    (b1 & 0x0F) << 0x0C |
                    (b2 & 0x3F) << 0x06 |
                    (b3 & 0x3F)
                )
            )
            s_ix += 2
        else:
            raise RuntimeError

    return u''.join(s_out)


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
            # Six-byte codepoint: a supplementary character written as a
            # UTF-16 surrogate pair, each half encoded as its own 3-byte
            # sequence. The codepoint is first offset by 0x10000 as required
            # by the surrogate-pair algorithm.
            c -= 0x10000
            final_string.extend([
                0xED,
                0xA0 | ((c >> 0x10) & 0x0F),
                0x80 | ((c >> 0x0A) & 0x3F),
                0xED,
                0xB0 | ((c >> 0x06) & 0x0F),
                0x80 | (c & 0x3F)
            ])

    return bytes(final_string)
