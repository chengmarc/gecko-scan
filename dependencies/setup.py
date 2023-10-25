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
    install_requires=['tk==8.6.12', 'requests==2.31.0', 'pandas==2.1.0', 'bs4==0.0.1', 'colorama==0.4.6']
)