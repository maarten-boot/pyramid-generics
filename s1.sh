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

for i in setuptools black pylama pyramid pyramid_jinja2 sqlalchemy
do
    $PIP list 2>/dev/null | grep -i -q "^${i} " || {
        $PIP install "${i}"
    }
done

echo start the app
$PYTHON main.py
