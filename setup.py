from setuptools import setup, find_packages

setup(
    name="skrules",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'numpy',
        'scikit-learn',
    ],
    python_requires='>=3.9',
)
