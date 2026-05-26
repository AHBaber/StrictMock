from setuptools import setup, find_packages

setup(
    name="StrictMock",
    version="0.2.0",
    description="Highly Deterministic Mocking",
    license="BSD",
    packages=find_packages(include=["strict_mock", "strict_mock.*"]),  # Specify the package folder
    install_requires=[
        "pytest",
    ],
    extras_require={
        "testing": [
            "pytest",
        ],
    },
)
