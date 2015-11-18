from setuptools import setup, find_packages

import os

here = os.path.abspath(os.path.dirname(__file__))

about = {}
# read about values
with open(os.path.join(here, 'pythonioc', '__about__.py'), 'r') as f:
    exec(f.read(), about)

with open(os.path.join(here, "README")) as f:
    long_description = f.read()

setup(

    name=about["__title__"],
    version=about["__version__"],
    description=about["__summary__"],
    long_description=long_description,

    license=about["__license__"],
    url=about["__uri__"],

    author=about["__author__"],
    author_email=about["__email__"],

    package_dir={'pythonioc': 'pythonioc'},
    packages=find_packages(),

    install_requires = ['future']
)
