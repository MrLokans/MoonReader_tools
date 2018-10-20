import re
from setuptools import setup, find_packages

version = ""

# I actually took it from requests library
with open("moonreader_tools/__init__.py", "r") as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
    ).group(1)

if not version:
    raise ValueError("No version specified.")

setup(
    name="moonreader_tools",
    version=version,
    description=(
        "Set of class and utilities to parse" "MoonReader+ book-related files.",
        "It is capable to reading, creating handy object"
        "representation and writing notes and statistics files",
    )[0],
    url="https://github.com/MrLokans/MoonReader_tools/",
    download_url="https://github.com/MrLokans/MoonReader_tools/tarball/{}".format(
        version
    ),
    author="MrLokans",
    author_email="mrlokans@gmail.com",
    license="MIT",
    packages=find_packages(exclude=["tests"]),
    entry_points={"console_scripts": ["moon_tools = moonreader_tools.main:main"]},
    install_requires=["dropbox"],
    classifiers=(
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
    ),
    test_suite="tests.test_all",
    zip_safe=False,
)
