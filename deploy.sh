#!/usr/bin/env bash

set -euo pipefail
FUNCTION_NAME="${1}"
PS1=""
virtualenv venv
source venv/bin/activate
pip install --requirement requirements.txt --target .
deactivate
rm -rf venv
rm -rf *.dist-info
rm -rf __pycache__
zip -r function.zip *
aws lambda update-function-code --function-name "${FUNCTION_NAME}" --zip-file fileb://function.zip
rm function.zip
