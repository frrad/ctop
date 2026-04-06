#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Use sudo if available and not already root
run() {
    if [ "$(id -u)" -eq 0 ]; then
        "$@"
    elif command -v sudo &>/dev/null; then
        sudo "$@"
    else
        echo "Error: need root or sudo to run: $*" >&2
        return 1
    fi
}

# Install gh CLI
if ! command -v gh &>/dev/null; then
    echo "Installing gh CLI..."
    if command -v apt-get &>/dev/null; then
        run apt-get update
        run apt-get install -y gh
    else
        echo "Warning: Could not install gh CLI (apt-get not found)."
        echo "Install manually: https://github.com/cli/cli#installation"
    fi
else
    echo "gh CLI already installed."
fi

# Install uv if not present
if ! command -v uv &>/dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Create venv and install dependencies
echo "Creating virtual environment..."
uv venv .venv
echo "Installing dependencies..."
uv pip install -r requirements.txt --python .venv/bin/python

echo "Setup complete. Activate the venv with: source .venv/bin/activate"
