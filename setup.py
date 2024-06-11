from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
requirements = (this_directory / "requirements.txt").read_text().splitlines()

setup(
    name='maidi',
    version='0.8',
    author="Florian GARDIN",
    author_email="fgardin.pro@gmail.com",
    description="A python package for symbolic AI music inference",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    packages=find_packages(include='*'),
    package_data={'maidi': ['examples/*.mid', 'metadata/*.pkl']},
    include_package_data=True,
)