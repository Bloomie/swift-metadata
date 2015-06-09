from setuptools import setup, find_packages
from swiftmetadata._version import __version__

name = 'swiftmetadata'

setup(
    name=name,
    version=__version__,
    description='package providing metadata support for Openstack Swift',
    classifiers=['Programming Language :: Python'],
    keywords='openstack swift metadata',
    author='itkey',
    packages=find_packages(),
    entry_points={
        'paste.filter_factory': [
            'swiftmetadata=swiftmetadata.middleware:filter_factory',
        ],
    },
)      
