#!/usr/bin/env python

from setuptools import setup

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    author_email="luke@lukeross.name",
    author="Luke Ross",
    description="Meld3-like templating using lxml",
    install_requires=["lxml"],
    license="BSD",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    name="lxmlmeld",
    url="http://lukeross.name/projects/lxmlmeld",
    packages=["lxmlmeld"],
    version="0.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
        "Topic :: Text Processing :: Markup :: HTML"
    ],
    keywords="meld3 pymeld"
)
