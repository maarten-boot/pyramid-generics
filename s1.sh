#! /usr/bin/env bash

WHAT=./env
export VENV=$WHAT

[ -d "${VENV}" ] || {
    python3 -m venv "${VENV}"
}

PIP="${VENV}/bin/pip3"
PYTHON="${VENV}/bin/python3"

ACTIVATE="${VENV}/bin/activate"
[ -f "${ACTIVATE}" ] || {
    echo "FATAL: no activate found at: '${ACTIVATE}'" >&2
    exit 101
}
source "${ACTIVATE}"
"${PIP}" install --upgrade pip

REQ="requirements-simple.txt"

cat <<! >"${REQ}"
setuptools
black
pylama
mypy
pyramid
pyramid_jinja2
SQLAlchemy
!

$PIP install -r "${REQ}"

$PYTHON main.py
