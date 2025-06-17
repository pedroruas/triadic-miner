from setuptools import setup, find_packages

setup(
    name="triadic_miner",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pandas==1.5.3",
        "tqdm==4.64.1",
        "concepts==0.9.2",
        "pyyed==1.5.0",
    ],
)