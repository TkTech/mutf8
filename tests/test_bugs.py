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
