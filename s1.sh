#! /usr/bin/env bash

WHAT=./env
export VENV="$WHAT"

[ -d "${VENV}" ] || {
    echo "FATAL: no env found at: '${VENV}'" >&2
    exit 101
}

PIP="${VENV}/bin/pip3"
PYTHON="${VENV}/bin/python3"
ACTIVATE="${VENV}/bin/activate"
[ -f "${ACTIVATE}" ] || {
    echo "FATAL: no activate found at: '${ACTIVATE}'" >&2
    exit 101
}
source "${ACTIVATE}"

$PYTHON main.py
