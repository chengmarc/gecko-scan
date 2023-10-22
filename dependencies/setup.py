# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
from setuptools import setup, find_packages

setup(
    name='gsl-dependencies',
    version='1.1',
    packages=find_packages(),
    install_requires=['tk', 'requests', 'pandas', 'bs4', 'colorama']
)