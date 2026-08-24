#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1

if command -v python3 >/dev/null 2>&1; then
    system_python=python3
elif command -v python >/dev/null 2>&1; then
    system_python=python
else
    echo "Python 3.10 or newer was not found. Install Python, then run this file again." >&2
    exit 1
fi

if ! "$system_python" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)'; then
    echo "The available Python version is too old. Python 3.10 or newer is required." >&2
    exit 1
fi

cache_root=${XDG_CACHE_HOME:-"$HOME/.cache"}
environment="$cache_root/byteforge-dbms/venv"
python="$environment/bin/python"

if [ ! -x "$python" ]; then
    echo "Preparing the ByteForge Python environment."
    if ! "$system_python" -m venv "$environment"; then
        echo "The Python environment could not be created. Install the venv package for this Python version, then try again." >&2
        exit 1
    fi
fi

echo "Checking required Python packages."
if ! "$python" -m pip install --disable-pip-version-check --quiet -r requirements.txt; then
    echo "Required Python packages could not be installed. Check the internet connection and try again." >&2
    exit 1
fi

echo "Preparing the database."
"$python" -m schema.scripts.setup.build_database --replace

echo "Checking the database."
"$python" -m schema.scripts.setup.verify_database

echo "Opening the sample queries."
"$python" -m schema.scripts.queries.demo_database

echo
echo "ByteForge is ready."
