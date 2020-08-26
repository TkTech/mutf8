# mutf-8

This package contains simple pure-python as well as C encoders and decoders for
the MUTF-8 character encoding. In most cases, you can also parse the even-rarer
CESU-8.

These days, you'll most likely encounter MUTF-8 when working on files or
protocols related to the JVM. Strings in a Java `.class` file are encoded using
MUTF-8, strings passed by the JNI, as well as strings exported by the object
serializer.

This library was extracted from [Lawu][], a Python library for working with JVM
class files.


[Lawu]: https://github.com/tktech/lawu
