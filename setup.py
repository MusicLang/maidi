from setuptools import setup, find_packages
import setuptools

setup(
    name='maidi',
    version='0.1',
    install_requires=open("requirements.txt", "r").read().splitlines(),
    packages=setuptools.find_packages(include='*'),
    package_data={'maidi': ['examples/*.mid', 'metadata/*.pkl']},
    include_package_data=True,
)
