#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Install gh CLI
if ! command -v gh &>/dev/null; then
    echo "Installing gh CLI..."
    if command -v apt-get &>/dev/null && command -v sudo &>/dev/null; then
        (type -p wget >/dev/null || (sudo apt-get update && sudo apt-get install wget -y))
        sudo mkdir -p -m 755 /etc/apt/keyrings
        out=$(mktemp)
        wget -nv -O "$out" https://cli.github.com/packages/githubcli-archive-keyring.gpg
        cat "$out" | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null
        sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
        sudo apt-get update
        sudo apt-get install gh -y
        rm -f "$out"
    elif command -v apt-get &>/dev/null; then
        # No sudo (e.g. running as root in a container)
        (type -p wget >/dev/null || (apt-get update && apt-get install wget -y))
        mkdir -p -m 755 /etc/apt/keyrings
        out=$(mktemp)
        wget -nv -O "$out" https://cli.github.com/packages/githubcli-archive-keyring.gpg
        cat "$out" | tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null
        chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null
        apt-get update
        apt-get install gh -y
        rm -f "$out"
    elif command -v conda &>/dev/null; then
        conda install -y -c conda-forge gh
    else
        echo "Warning: Could not install gh CLI. No supported package manager found."
        echo "Install manually: https://github.com/cli/cli#installation"
    fi
else
    echo "gh CLI already installed."
fi

# Install uv if not present
if ! command -v uv &>/dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Make uv available in current session
    export PATH="$HOME/.local/bin:$PATH"
fi

# Create venv and install dependencies
echo "Creating virtual environment..."
uv venv .venv
echo "Installing dependencies..."
uv pip install -r requirements.txt --python .venv/bin/python

echo "Setup complete. Activate the venv with: source .venv/bin/activate"
