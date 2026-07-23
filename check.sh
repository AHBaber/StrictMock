#!/bin/bash

sh lint.sh

python -m unittest
pytest --cov=strict_mock --cov-report term-missing
