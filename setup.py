
#!/usr/bin/env python 
# coding=utf-8
        
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    with open('README.rst', 'r') as fp:
        readme = fp.read()
except :
    readme = ''
try:
    with open('README.md', 'r') as fp:
        readme = fp.read()
except :
    pass

try:
    with open('HISTORY.rst', 'r') as fp:
        history = fp.read()
except :
    history = ''
        

setup(
    name = 'lizhifm',
    version = '0.0.6',
    description = 'Would you like lizhi FM ? Now, Record it.',
    long_description = readme + history,
    author = 'Cole Smith',
    author_email = 'uniquecolesmith@gmail.com',
    url = '',
    packages = ['lizhifm'],
    package_dir = {"lizhifm": "src"},
    include_package_data = True,
    install_requires = ['requests', 'downloadhelper', 'prettytable', ],
    license = "Apache 2.0",
    zip_safe = False,
    classifiers = ('Development Status :: 4 - Beta', 'Intended Audience :: Developers', 'Natural Language :: English', 'License :: OSI Approved :: Apache Software License', 'Programming Language :: Python', 'Programming Language :: Python :: 2.6', 'Programming Language :: Python :: 2.7', 'Programming Language :: Python :: 3', 'Programming Language :: Python :: 3.3', 'Programming Language :: Python :: 3.4'),
    entry_points = {"console_scripts": ["lizhifm = lizhifm:main"]},

)
