#!/bin/bash

isort strict_mock tests
mypy strict_mock tests
flake8 strict_mock tests
