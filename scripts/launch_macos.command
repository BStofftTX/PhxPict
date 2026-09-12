#!/bin/zsh
set -e
cd "${0:A:h}/.."

if [[ ! -x .venv/bin/phxpict ]]; then
  echo "PhxPict is not installed yet. Run scripts/setup_macos.command first."
  exit 1
fi

source .venv/bin/activate
phxpict
