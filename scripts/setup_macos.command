#!/bin/zsh
set -e
cd "${0:A:h}/.."

PYTHON_BIN=""
for candidate in python3.13 python3.12 python3.11 python3; do
  if command -v "$candidate" >/dev/null 2>&1; then
    PYTHON_BIN="$candidate"
    break
  fi
done

if [[ -z "$PYTHON_BIN" ]]; then
  echo "Python 3 is required. Install it from https://www.python.org/downloads/macos/"
  exit 1
fi

if ! "$PYTHON_BIN" -c 'import tkinter; raise SystemExit(0 if tkinter.TkVersion >= 8.6 else 1)' >/dev/null 2>&1; then
  echo "A usable Python was not found. PhxPict requires Tk 8.6 or newer."
  echo "Install a current Python from https://www.python.org/downloads/macos/ and retry."
  exit 1
fi

"$PYTHON_BIN" -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[visual]"

echo "Checking the local visual model (the first run downloads its weights)..."
python - <<'PY'
from phxpict.providers import LocalCLIPTagProvider
provider = LocalCLIPTagProvider()
provider._load_classifier()
print("PhxPict visual model is cached and ready.")
PY

echo "Running verification tests..."
python -m unittest discover -s tests -v
echo "Setup complete. Launching PhxPict..."
phxpict
