import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "wddasylumclaims",
    version = "0.0.30",
    author = "Ben Knight",
    author_email = "benknight135@gmail.com",
    description = ("Asylum Seekers Claims scrapping of data",
                        "from web and analysis of outcomes"),
    license = "License :: OSI Approved :: GPL3",
    keywords = "wdd asylum seekers claims webscrape wddasylumclaims",
    url = "https://github.com/benknight135/wdd-asylum-claims",
    packages=['wddasylumclaims','wddasylumclaims/DbAsylumClaims'],
    install_requires=['requests','bs4','pandas','feather-format','numpy','argparse','pypiwin32','regex','pyodbc'],
    package_data={
        'wddasylumclaims': ['data'],
    },
    include_package_data=True,
    data_files=[('Lib\\site-packages\\wddasylumclaims\\data', 
        [
            'data/keywords.csv',
        ])],
    entry_points={
        'console_scripts': [
            'wddasylumclaims = wddasylumclaims.__main__:main',
            'convertfeather = wddasylumclaims.FeatherConvert:main'
        ],
    },
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)