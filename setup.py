from setuptools import setup, find_packages

from main       import APPLICATION_DESCRIPTION, APPLICATION_NAME, VERSION


with open("README.md") as f:
    long_description = f.read()

setup(  
    name = APPLICATION_NAME,
    version = VERSION,
    description = APPLICATION_DESCRIPTION,
    long_description = long_description,
    long_description_content_type='text/markdown',
    author = "Chad Reynolds",
    author_email = "cjreynol13@aol.com",
    url = "https://github.com/Cjreynol/pypaint",
    project_urls = {
        "Source" : "https://github.com/Cjreynol/pypaint"
        },
    license = "MIT",
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Artistic Software",
        "Topic :: Multimedia :: Graphics :: Editors"
        ],
    keywords = "drawing collaboration paint",
    install_requires = [
        "chadlib>=0.2.13"
    ],
    python_requires = ">=3",
    py_modules = ["main"],
    packages = find_packages(),
    test_suite = "tests"
)
