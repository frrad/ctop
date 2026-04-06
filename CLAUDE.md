# ctop

## Setup

This project uses `uv` for Python environment management. Run `./setup.sh` to set up the project (also runs automatically via SessionStart hook).

Always use the `.venv` virtual environment: `source .venv/bin/activate` before running Python scripts.

## Dependencies

Python dependencies are in `requirements.txt`. Install with:

```
uv pip install -r requirements.txt --python .venv/bin/python
```
