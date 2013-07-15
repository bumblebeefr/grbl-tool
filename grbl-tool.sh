#!/bin/bash
cd "$(dirname "$0")"
./local.virtualenv/bin/python grbl-tool.py $@
