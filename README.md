# BondYield-Py

Compact educational demo comparing bond-yield convergence methods.

This project uses a standard C++ numerical core exposed to Python with pybind11,
with a Python/PySide6 GUI.

## Build and run

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install .
bond-yield
