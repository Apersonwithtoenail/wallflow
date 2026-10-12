#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p ~/.local/bin
chmod +x "$DIR/wallflow.py"
ln -sf "$DIR/wallflow.py" ~/.local/bin/wallflow
echo "installed -> ~/.local/bin/wallflow"
