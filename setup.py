from setuptools import setup, find_packages

setup(
    name="StrictMock",
    version="0.6.5",
    description="Highly Deterministic Mocking",
    license="BSD-3-Clause",
    packages=find_packages(include=["strict_mock", "strict_mock.*"]),  # Specify the package folder
    install_requires=[],
    extras_require={
        "testing": [
            "pytest",
        ],
    },
)
