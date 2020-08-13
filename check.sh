#!/bin/bash

# Simple helper script to do some static checking of the code.

mypy --strict extract.py environment.py record.py serialize.py
pycodestyle --exclude measurements-scripts/,source.py,sink.py .
