import os
from setuptools import setup, find_packages

from eve_mlp import __version__

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = ""  # open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    #'PyYAML',
    #'BeautifulSoup4',
    'requests',

    # testing
    #'nose',
    #'coverage',
    #'unittest2',
    #'mock',
]

setup(
    name='eve-mlp',
    version=__version__,
    description='Mobile Launch Platform for EVE Online',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Programming Language :: Python",
    ],
    author='Shish',
    author_email='shish+mlp@shishnet.org',
    url='https://github.com/shish/eve-mlp',
    keywords='eve-online',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='eve_mlp',
    install_requires=requires,
    entry_points="""\
    [console_scripts]
    eve-mlp = eve_mlp.cli:main
    eve-gmlp = eve_mlp.gui:main
    """,
)
