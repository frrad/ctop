#!/usr/bin/env bash
set -euo pipefail

# Install gh CLI
if ! command -v gh &>/dev/null; then
    echo "Installing gh CLI..."
    (type -p wget >/dev/null || (sudo apt update && sudo apt-get install wget -y))
    sudo mkdir -p -m 755 /etc/apt/keyrings
    out=$(mktemp)
    wget -nv -O "$out" https://cli.github.com/packages/githubcli-archive-keyring.gpg
    cat "$out" | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null
    sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
    sudo apt update
    sudo apt install gh -y
    rm -f "$out"
else
    echo "gh CLI already installed."
fi

# Install uv if not present
if ! command -v uv &>/dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Create venv and install dependencies
echo "Creating virtual environment..."
uv venv .venv
echo "Installing dependencies..."
uv pip install -r requirements.txt --python .venv/bin/python

echo "Setup complete. Activate the venv with: source .venv/bin/activate"
