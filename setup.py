#!/usr/bin/env python
# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (c) 2018 BayLibre
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from setuptools import setup, find_packages

setup(
    name='RegiceSTM32',
    packages=find_packages(),
    author='Alexandre Bailon',
    author_email='abailon@baylibre.com',
    description='Provide some functions to manage plugins and packages.',
    url='https://github.com/BayLibre/regice-stm32', 
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 1 - Planning",
        "License :: MIT",
        "Natural Language :: English",
        "Operating System :: GNU/Linux",
        "Programming Language :: Python :: 3.6",
    ],
    install_requires=['LibRegice', 'RegiceClock', 'RegicePkg'],
    dependency_links=[
        'git+https://github.com/BayLibre/libregice.git#egg=LibRegice',
        'git+https://github.com/BayLibre/regice-clock.git#egg=RegiceClock',
        'git+https://github.com/BayLibre/regice-common.git#egg=RegiceCommon',
    ],
    package_data={'RegiceSTM32': ['stm32/*.svd']},
    include_package_data=True,
    entry_points={
        'regice': [
                'is_compatible_with = stm32.STM32F407:is_compatible_with',
        ]
    },
)
