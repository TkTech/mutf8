#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>
#include <stdio.h>

static const char *DECODING_ERRORS[] = {
    "mutf-8 does not allow NULL bytes.",
    "Incomplete two-byte codepoint.",
    "Incomplete three-byte codepoint.",
    "Incomplete six-byte codepoint.",
    NULL
};

static PyObject*
decode_modified_utf8(PyObject *self, PyObject *args) {
    Py_buffer view;

    if (!PyArg_ParseTuple(args, "y*", &view)) {
        return NULL;
    }

    // MUTF-8 input.
    uint8_t *buf = (uint8_t*)view.buf;
    // Array of temporary UCS-4 codepoints.
    // There's no point using PyUnicode_new and _WriteChar, because
    // it requires us to have iterated the string to get the maximum unicode
    // codepoint and count anyways.
    uint32_t *cp_out = malloc(view.len);
    // # of codepoints we found & current index into cp_out.
    Py_ssize_t cp_count = 0;
    int error = -1;

    for (Py_ssize_t ix = 0; ix < view.len; ix++) {
        Py_UCS4 x = buf[ix];
        if (x == 0) {
            error = 0;
            break;
        } else if (x >> 7 == 0x00) {
            // ASCII/one-byte codepoint.
            x &= 0x7F;
        } else if (x >> 5 == 0x06) {
            // Two-byte codepoint.
            if (ix + 1 >= view.len) {
                error = 1;
                break;
            }
            x = (
                (buf[ix + 0] & 0x1F) << 0x06 |
                (buf[ix + 1] & 0x3F)
            );
            ix++;
        } else if (x == 0xED) {
            // Six-byte codepoint.
            if (ix + 5 >= view.len) {
                error = 3;
                break;
            }
            x = (
                0x10000 |
                (buf[ix + 1] & 0x0F) << 0x10 |
                (buf[ix + 2] & 0x3F) << 0x0A |
                (buf[ix + 4] & 0x0F) << 0x06 |
                (buf[ix + 5] & 0x3F)
            );
            ix += 5;
        } else if (x >> 4 == 0x0E) {
            // Three-byte codepoint.
            if (ix + 2 >= view.len) {
                error = 2;
                break;
            }
            x = (
                (buf[ix + 0] & 0x0F) << 0x0C |
                (buf[ix + 1] & 0x3F) << 0x06 |
                (buf[ix + 2] & 0x3F)
            );
            ix += 2;
        }
        cp_out[cp_count++] = x;
    }

    if (error != -1) {
        PyObject *unicode_error = PyObject_CallFunction(
            PyExc_UnicodeDecodeError,
            "sy#nns",
            "utf-8",
            "",
            0,
            0,
            1,
            DECODING_ERRORS[error]
        );
        PyErr_SetObject(PyExc_UnicodeDecodeError, unicode_error);
        Py_XDECREF(unicode_error);
        free(cp_out);
        PyBuffer_Release(&view);
        return NULL;
    }

    PyObject *out = PyUnicode_FromKindAndData(
        PyUnicode_4BYTE_KIND,
        cp_out,
        cp_count
    );

    free(cp_out);
    PyBuffer_Release(&view);
    return out;
}

static PyObject*
encode_modified_utf8(PyObject *self, PyObject *args) {
    PyObject *src = NULL;

    if (!PyArg_ParseTuple(args, "U", &src)) {
        return NULL;
    }

    void *data = PyUnicode_DATA(src);
    Py_ssize_t length = PyUnicode_GET_LENGTH(src);
    int kind = PyUnicode_KIND(src);
    // There's no case in which the encoded version will be more than
    // twice the size of the decoded version.
    char *byte_out = malloc(length * 2);
    Py_ssize_t byte_count = 0;

    for (Py_ssize_t i = 0; i < length; i++) {
        Py_UCS4 cp = PyUnicode_READ(kind, data, i);
        if (cp == 0x00) {
            // NULL byte encoding shortcircuit.
            byte_out[byte_count++] = 0xC0;
            byte_out[byte_count++] = 0x80;
        } else if (cp <= 0x7F) {
            // ASCII
            byte_out[byte_count++] = cp;
        } else if (cp <= 0x7FF) {
            // Two-byte codepoint.
            byte_out[byte_count++] = (0xC0 | (0x1F & (cp >> 0x06)));
            byte_out[byte_count++] = (0x80 | (0x3F & cp));
        } else if (cp <= 0xFFFF) {
            // Three-byte codepoint
            byte_out[byte_count++] = (0xE0 | (0x0F & (cp >> 0x0C)));
            byte_out[byte_count++] = (0x80 | (0x3F & (cp >> 0x06)));
            byte_out[byte_count++] = (0x80 | (0x3F & cp));
        } else {
            // "Two-times-three" byte codepoint.
            byte_out[byte_count++] = 0xED;
            byte_out[byte_count++] = 0xA0 | ((cp >> 0x10) & 0x0F);
            byte_out[byte_count++] = 0x80 | ((cp >> 0x0A) & 0x3F);
            byte_out[byte_count++] = 0xED;
            byte_out[byte_count++] = 0xB0 | ((cp >> 0x06) & 0x0F);
            byte_out[byte_count++] = 0x80 | (cp & 0x3F);
        }
    }

    PyObject *out = PyBytes_FromStringAndSize(byte_out, byte_count);
    free(byte_out);
    return out;
}

static PyMethodDef module_methods[] = {
    {
        "decode_modified_utf8",
        decode_modified_utf8,
        METH_VARARGS,
        "Decodes a bytestring containing MUTF-8 as defined in section\n"
        "4.4.7 of the JVM specification.\n\n"
        ":param s: A byte/buffer-like to be converted.\n"
        ":returns: A unicode representation of the original string."
    },
    {
        "encode_modified_utf8",
        encode_modified_utf8,
        METH_VARARGS,
        "Encodes a unicode string as MUTF-8 as defined in section\n"
        "4.4.7 of the JVM specification.\n\n"
        ":param u: Unicode string to be converted.\n"
        ":returns: The encoded string as a `bytes` object."
    },
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef cmutf8_module = {
    PyModuleDef_HEAD_INIT,
    "mutf8.cmutf8",
    "Encoders and decoders for the MUTF-8 encoding.",
    -1,
    module_methods
};

PyMODINIT_FUNC
PyInit_cmutf8(void) {
    PyObject *m;

    m = PyModule_Create(&cmutf8_module);
    if (m == NULL)
        return NULL;

    return m;
}
