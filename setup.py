#!/usr/bin/env python

from setuptools import setup

setup(
    author_email="luke@lukeross.name",
    author="Luke Ross",
    description="Meld3-like templating using lxml",
    install_requires=["lxml"],
    license="BSD",
    name="lxmlmeld",
    url="https://github.com/lukeross/lxmlmeld",
    packages=["lxmlmeld"],
    version="0.3",
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
