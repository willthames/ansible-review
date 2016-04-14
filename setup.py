import os
from setuptools import find_packages
from setuptools import setup
import sys


sys.path.insert(0, os.path.abspath('lib'))

exec(open('lib/ansiblereview/version.py').read())

setup(
    name='ansible-review',
    version=__version__,
    description=('reviews ansible playbooks, roles and inventory and suggests improvements'),
    keywords='ansible, code review',
    author='Will Thames',
    author_email='will@thames.id.au',
    url='https://github.com/willthames/ansible-review',
    package_dir={'': 'lib'},
    packages=find_packages('lib'),
    zip_safe=False,
    install_requires=['ansible-lint>=3.0.0rc5', 'pyyaml', 'appdirs', 'Fabric'],
    scripts=['bin/ansible-review'],
    license='MIT',
    test_suite="test"
)
