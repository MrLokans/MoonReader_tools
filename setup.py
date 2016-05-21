from setuptools import setup

setup(
    name="moonreader_tools",
    version='0.8.3',
    description="Set of class and utilities to parse MoonReader+ book-related files.",
    url='MoonReader_tools',
    author='MrLokans',
    license='MIT',
    packages=['moonreader_tools'],
    entry_points={
        'console_scripts': [
            'moonreader_tools = moonreader_tools.main:main'
        ]
    },
    test_suite="tests.test_all",
    zip_safe=False
)
