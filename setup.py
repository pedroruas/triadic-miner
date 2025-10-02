from setuptools import setup, find_packages

setup(
    name="triadic_miner",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "concepts==0.9.2",
        "networkx==3.5",
        "numpy==1.26.4",
        "pandas==1.5.3",
        "pyvis==0.3.2",
        "pyyed==1.5.0",
        "tqdm==4.64.1",
    ],
)
