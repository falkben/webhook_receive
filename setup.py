from setuptools import find_packages, setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="webhook_receive",
    author="Benjamin Falk",
    packages=find_packages(),
    install_requires=requirements,
)
