from setuptools import find_packages, setup


setup(
    name="blah-de-blah",
    version="0.3.4",
    py_modules=["cli"],
    install_requires=[
        "click>=7.1.2",
        "coolname>=1.1.0",
    ],
    packages=find_packages(exclude=("tests", "docs")),
    include_package_data=True,
)
