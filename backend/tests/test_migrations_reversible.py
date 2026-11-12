"""Verifies reversible forward and backward Alembic migrations on a fresh isolated database."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT = BACKEND_DIR.parent


def test_reversible_alembic_migrations():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = Path(tmpdir) / "fresh_migration_test.db"
        env = os.environ.copy()
        env["DATABASE_URL"] = f"sqlite:///{test_db.as_posix()}"

        # 1. Forward to HEAD
        cmd_head = [sys.executable, "-m", "alembic", "upgrade", "head"]
        p1 = subprocess.run(cmd_head, cwd=str(BACKEND_DIR), env=env, capture_output=True, text=True)
        assert p1.returncode == 0, f"Alembic upgrade head failed:\n{p1.stderr}"

        # 2. Backward to BASE
        cmd_base = [sys.executable, "-m", "alembic", "downgrade", "base"]
        p2 = subprocess.run(cmd_base, cwd=str(BACKEND_DIR), env=env, capture_output=True, text=True)
        assert p2.returncode == 0, f"Alembic downgrade base failed:\n{p2.stderr}"

        # 3. Forward to HEAD again
        p3 = subprocess.run(cmd_head, cwd=str(BACKEND_DIR), env=env, capture_output=True, text=True)
        assert p3.returncode == 0, f"Second Alembic upgrade head failed:\n{p3.stderr}"

        print(
            "PASS: Forward and backward Alembic migrations upgrade head -> downgrade base -> upgrade head verified successfully."
        )


if __name__ == "__main__":
    test_reversible_alembic_migrations()
