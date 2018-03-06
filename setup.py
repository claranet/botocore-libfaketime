#!/usr/bin/env python

from setuptools import setup

setup(
    name='botocore-libfaketime',
    version='0.0.1',
    description='Patches botocore to work with libfaketime',
    author='Raymond Butcher',
    author_email='ray.butcher@claranet.uk',
    url='https://github.com/claranet/python-botocore-libfaketime',
    license='MIT License',
    packages=(
        'botocore_libfaketime',
    ),
    install_requires=(
        'botocore',
    ),
)
