#! /bin/sh
cd "$(dirname "$0")"

virtualenv local.virtualenv
./local.virtualenv/bin/pip install -r librequired.txt
