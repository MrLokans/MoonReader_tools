from setuptools import setup, find_packages

setup(
    name="moonreader_tools",
    version='0.8.7',
    description=("Set of class and utilities to parse"
                 "MoonReader+ book-related files.",
                 "It is capable to reading, creating handy object"
                 "representation and writing notes and statistics files")[0],
    url='https://github.com/MrLokans/MoonReader_tools/',
    author='MrLokans',
    license='MIT',
    packages=find_packages(exclude=["tests"]),
    entry_points={
        'console_scripts': [
            'moon_tools = moonreader_tools.main:main'
        ]
    },
    install_requires=[
        'dropbox',
    ],
    test_suite="tests.test_all",
    zip_safe=False
)
