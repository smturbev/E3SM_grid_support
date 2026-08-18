#!/ascldap/users/smturbe/.conda/envs/e3sm-unified_1.11/bin/python
"""
Install the local E3SM_grid_support package in editable mode
using the Python interpreter running this script.
"""

import sys
import subprocess
from pathlib import Path
import argparse

def main():
    p = argparse.ArgumentParser(description="Install local package in editable mode")
    p.add_argument(
        "path",
        nargs="?",
        default="/home/smturbe/codes/E3SM_grid_support",
        help="Path to package to install (default: %(default)s)",
    )
    p.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress pip stdout/stderr (shows only on error)",
    )
    args = p.parse_args()

    pkg_path = Path(args.path).expanduser().resolve()
    if not pkg_path.exists():
        print(f"ERROR: path does not exist: {pkg_path}", file=sys.stderr)
        return 2

    cmd = [sys.executable, "-m", "pip", "install", "-e", str(pkg_path)]
    print("Running:", " ".join(map(str, cmd)))

    try:
        if args.quiet:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                print("pip failed:", result.stderr, file=sys.stderr)
                return result.returncode
        else:
            subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        print("pip install failed with exit code", e.returncode, file=sys.stderr)
        return e.returncode

    # Verify import (optional)
    try:
        import importlib, importlib.util
        spec = importlib.util.find_spec("taos")
        print("taos spec:", spec)
        if spec is None:
            print("WARNING: 'taos' not found after install", file=sys.stderr)
            return 3
        taos = importlib.import_module("taos")
        print("Installed taos at:", getattr(taos, "__file__", "<builtin>"))
    except Exception as e:
        print("Import check failed:", e, file=sys.stderr)
        return 4

    return 0

if __name__ == "__main__":
    sys.exit(main())