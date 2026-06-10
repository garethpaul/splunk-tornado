#!/usr/bin/env python

# Importing setuptools adds some features like "setup.py develop", but
# it's optional so swallow the error if it's not there.
try:
    from setuptools import setup
    HAS_SETUPTOOLS = True
except ImportError:
    from distutils.core import setup
    HAS_SETUPTOOLS = False

version = "0.1"

setup_kwargs = dict(
    name="splunktornado",
    version=version,
    packages = ["splunktornado"],
    author="Carl S. Yestrau Jr.",
    author_email="spam@featureblend.com",
    url="https://github.com/garethpaul/splunk-tornado",
    download_url="https://github.com/garethpaul/splunk-tornado/archive/%s.tar.gz" % version,
    description="Implementation of Splunk authentication scheme for Tornado"
)

if HAS_SETUPTOOLS:
    setup_kwargs["install_requires"] = ["lxml>=6.1.1,<7", "tornado>=6.5.6,<7"]

setup(**setup_kwargs)
