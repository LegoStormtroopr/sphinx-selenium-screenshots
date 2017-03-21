import os
from setuptools import setup, find_packages

VERSION = '0.0.1b'

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='sphinx-selenium-screenshots',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    license='TBD Licence',
    description='Code to make screenshots of webservers for sphinx',
    long_description=README,
    url='https://github.com/LegoStormtroopr/sphinx-selenium-screenshots',
    author='Samuel Spencer',
    author_email='sam@aristotlemetadata.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires = [
        "selenium",
        'Pillow',
    ],

)
