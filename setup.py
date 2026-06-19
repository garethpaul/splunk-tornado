#!/usr/bin/env python

from pathlib import Path

from setuptools import setup

ROOT = Path(__file__).resolve().parent
version = "0.2.0"

setup_kwargs = dict(
    name="splunktornado",
    version=version,
    packages = ["splunktornado"],
    author="Carl S. Yestrau Jr.",
    author_email="spam@featureblend.com",
    url="https://github.com/garethpaul/splunk-tornado",
    download_url="https://github.com/garethpaul/splunk-tornado/archive/%s.tar.gz" % version,
    description="Implementation of Splunk authentication scheme for Tornado",
    long_description=(ROOT / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    install_requires=["lxml>=6.1.1,<7", "tornado>=6.5.7,<7"],
    python_requires=">=3.10",
)

setup(**setup_kwargs)
