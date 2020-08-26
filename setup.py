import os
import os.path

from setuptools import setup, find_packages, Extension


root = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(root, 'README.md'), 'rb') as readme:
    long_description = readme.read().decode('utf-8')


setup(
    name='mutf8',
    packages=find_packages(),
    version='1.0.1',
    description='Fast MUTF-8 encoder & decoder',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Tyler Kennedy',
    author_email='tk@tkte.ch',
    url='http://github.com/TkTech/mutf8',
    keywords=['mutf-8', 'cesu-8', 'jvm'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
    ],
    extras_require={
        'test': [
            'pytest',
            'pytest-benchmark'
        ]
    },
    ext_modules=[
        Extension(
            'mutf8.cmutf8',
            ['mutf8/cmutf8.c'],
            language='c',
            optional=True
        )
    ]
)
