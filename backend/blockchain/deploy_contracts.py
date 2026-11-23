"""Deployment helper placeholder.

For a normal PC execution, deployment is handled by Hardhat scripts in the
root scripts/ directory. This Python module exists so the backend architecture
has a clear deployment service boundary.
"""
from __future__ import annotations

import subprocess
from pathlib import Path


def deploy_with_hardhat(project_root: str | Path = ".") -> int:
    return subprocess.call(["npm", "run", "deploy"], cwd=str(project_root))
