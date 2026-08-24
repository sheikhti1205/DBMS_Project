#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1

assume_yes=0

for argument in "$@"; do
    case "$argument" in
        -y|--yes)
            assume_yes=1
            ;;
        -h|--help)
            echo "Usage: ./setup_linux.sh [--yes]"
            echo "  --yes  Approve required installations without prompting."
            exit 0
            ;;
        *)
            echo "Unknown option: $argument" >&2
            echo "Use --help to see the available options." >&2
            exit 2
            ;;
    esac
done

confirm_install() {
    prompt=$1

    if [ "$assume_yes" -eq 1 ]; then
        return 0
    fi

    if [ ! -t 0 ]; then
        echo "$prompt" >&2
        echo "Setup cannot ask for approval in this terminal. Run it interactively or add --yes." >&2
        return 1
    fi

    printf "%s [y/N]: " "$prompt"
    IFS= read -r answer || return 1
    case "$answer" in
        y|Y|yes|YES|Yes)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

run_as_root() {
    if [ "$(id -u)" -eq 0 ]; then
        "$@"
    elif command -v sudo >/dev/null 2>&1; then
        sudo "$@"
    else
        echo "Administrator access is required to install system packages." >&2
        echo "Install Python 3.10 or newer with venv and pip, then run setup again." >&2
        return 1
    fi
}

install_system_python() {
    if command -v apt-get >/dev/null 2>&1; then
        packages="python3 python3-venv python3-pip ca-certificates"
        manager="apt"
    elif command -v dnf >/dev/null 2>&1; then
        packages="python3 python3-pip ca-certificates"
        manager="dnf"
    elif command -v microdnf >/dev/null 2>&1; then
        packages="python3 python3-pip ca-certificates"
        manager="microdnf"
    elif command -v yum >/dev/null 2>&1; then
        packages="python3 python3-pip ca-certificates"
        manager="yum"
    elif command -v pacman >/dev/null 2>&1; then
        packages="python python-pip ca-certificates"
        manager="pacman"
    elif command -v zypper >/dev/null 2>&1; then
        packages="python3 python3-pip ca-certificates"
        manager="zypper"
    elif command -v apk >/dev/null 2>&1; then
        packages="python3 py3-pip ca-certificates"
        manager="apk"
    elif command -v brew >/dev/null 2>&1; then
        packages="python@3.12"
        manager="brew"
    else
        echo "No supported package manager was found." >&2
        echo "Install Python 3.10 or newer with venv and pip, then run setup again." >&2
        return 1
    fi

    echo "Python, venv, and pip are required."
    echo "Package manager: $manager"
    echo "Packages: $packages"
    if ! confirm_install "Install these system packages now?"; then
        echo "System package installation was not approved. No system packages were changed." >&2
        return 1
    fi

    case "$manager" in
        apt)
            run_as_root apt-get update
            run_as_root apt-get install -y python3 python3-venv python3-pip ca-certificates
            ;;
        dnf)
            run_as_root dnf install -y python3 python3-pip ca-certificates
            ;;
        microdnf)
            run_as_root microdnf install -y python3 python3-pip ca-certificates
            ;;
        yum)
            run_as_root yum install -y python3 python3-pip ca-certificates
            ;;
        pacman)
            run_as_root pacman -Sy --needed --noconfirm python python-pip ca-certificates
            ;;
        zypper)
            run_as_root zypper --non-interactive install python3 python3-pip ca-certificates
            ;;
        apk)
            run_as_root apk add python3 py3-pip ca-certificates
            ;;
        brew)
            brew install python@3.12
            ;;
    esac
}

find_python() {
    for candidate in python3 python; do
        if command -v "$candidate" >/dev/null 2>&1 \
            && "$candidate" -c 'import sqlite3, sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
            printf "%s\n" "$candidate"
            return 0
        fi
    done
    return 1
}

system_python=$(find_python || true)
if [ -z "$system_python" ]; then
    echo "A usable Python 3.10 or newer installation was not found."
    install_system_python || exit 1
    system_python=$(find_python || true)
fi

if [ -z "$system_python" ]; then
    echo "Python was installed, but Python 3.10 or newer with SQLite support is still unavailable." >&2
    exit 1
fi

cache_root=${XDG_CACHE_HOME:-"$HOME/.cache"}
environment=${BYTEFORGE_ENV:-"$cache_root/byteforge-dbms/venv"}
python="$environment/bin/python"

if [ ! -x "$python" ] \
    || ! "$python" -c 'import sqlite3, sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
    echo "Preparing the ByteForge Python environment."
    if ! "$system_python" -m venv --clear "$environment"; then
        echo "The Python environment could not be created with the current system packages."
        install_system_python || exit 1
        system_python=$(find_python || true)
        if [ -z "$system_python" ] || ! "$system_python" -m venv --clear "$environment"; then
            echo "The Python environment still could not be created." >&2
            exit 1
        fi
    fi
fi

if ! "$python" -m pip --version >/dev/null 2>&1; then
    echo "Preparing pip in the private environment."
    if ! "$python" -m ensurepip --upgrade; then
        echo "pip could not be prepared in the private environment." >&2
        exit 1
    fi
fi

requirements_ready() {
    "$python" -c 'from importlib.metadata import version
from pathlib import Path
lines = (line.strip() for line in Path("requirements.txt").read_text(encoding="utf-8").splitlines())
required = [line.split("==", 1) for line in lines if line and not line.startswith("#")]
ready = required and all(version(name.strip()) == expected.strip() for name, expected in required)
raise SystemExit(0 if ready else 1)' >/dev/null 2>&1
}

if ! requirements_ready; then
    echo "The private environment needs the packages listed in requirements.txt."
    if ! confirm_install "Install the project packages now?"; then
        echo "Project package installation was not approved. The database was not changed." >&2
        exit 1
    fi

    echo "Installing the project packages."
    if ! "$python" -m pip install --disable-pip-version-check --quiet -r requirements.txt; then
        echo "Required Python packages could not be installed. Check the internet connection and try again." >&2
        exit 1
    fi
else
    echo "Required project packages are already available."
fi

echo "Preparing the database."
"$python" -m schema.scripts.setup.build_database --replace

echo "Checking the database."
"$python" -m schema.scripts.setup.verify_database

echo "Opening the sample queries."
"$python" -m schema.scripts.queries.demo_database

echo
echo "ByteForge is ready."
