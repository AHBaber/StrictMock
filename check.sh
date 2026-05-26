#!/bin/bash

sh lint.sh

pytest --cov=strict_mock --cov-report term-missing
