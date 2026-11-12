"""CraftLens 2.0 Database Backup and Restore Utility.

Supports:
- Safe online backup of SQLite database (via sqlite3 backup API) and PostgreSQL (via pg_dump).
- SHA-256 checksum manifest generation for immutable integrity verification.
- Point-in-time restore from verified backup archive.
- Automated verification drill (--drill) verifying backup creation and restore integrity.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings  # noqa: E402


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def backup_database(destination_dir: Path | None = None) -> Path:
    dest = destination_dir or (ROOT / "backups")
    dest.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")

    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite:///"):
        raw_path = db_url.replace("sqlite:///", "")
        src = (BACKEND_DIR / raw_path).resolve() if not os.path.isabs(raw_path) else Path(raw_path)
        if not src.exists():
            raise FileNotFoundError(f"Source SQLite database not found: {src}")

        backup_file = dest / f"craftlens_backup_{ts}.db"

        # Online SQLite backup API ensures safe point-in-time consistency even during active writes
        src_conn = sqlite3.connect(str(src))
        dst_conn = sqlite3.connect(str(backup_file))
        try:
            src_conn.backup(dst_conn)
        finally:
            dst_conn.close()
            src_conn.close()

        checksum = _sha256_file(backup_file)
        manifest = {
            "version": "2.0.0",
            "created_at": datetime.now(UTC).isoformat(),
            "engine": "sqlite",
            "source_file": str(src),
            "backup_file": backup_file.name,
            "bytes": backup_file.stat().st_size,
            "sha256": checksum,
        }
        manifest_path = dest / f"craftlens_backup_{ts}.manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return manifest_path
    else:
        # PostgreSQL dump hook
        backup_file = dest / f"craftlens_pg_dump_{ts}.sql"
        cmd = f"pg_dump {db_url} -f {backup_file}"
        res = os.system(cmd)
        if res != 0 or not backup_file.exists():
            raise RuntimeError(f"pg_dump failed with exit code {res}")
        checksum = _sha256_file(backup_file)
        manifest = {
            "version": "2.0.0",
            "created_at": datetime.now(UTC).isoformat(),
            "engine": "postgresql",
            "backup_file": backup_file.name,
            "bytes": backup_file.stat().st_size,
            "sha256": checksum,
        }
        manifest_path = dest / f"craftlens_backup_{ts}.manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return manifest_path


def restore_database(manifest_path: Path, target_path: Path | None = None) -> bool:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    backup_file = manifest_path.parent / manifest["backup_file"]
    if not backup_file.exists():
        raise FileNotFoundError(f"Backup file missing: {backup_file}")

    actual_hash = _sha256_file(backup_file)
    if actual_hash != manifest["sha256"]:
        raise ValueError(f"Integrity check failed! Expected {manifest['sha256']} but got {actual_hash}")

    if manifest["engine"] == "sqlite":
        dest = target_path or Path(manifest["source_file"])
        # Verify backup sqlite readability before replacing
        test_conn = sqlite3.connect(str(backup_file))
        cursor = test_conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        row = cursor.fetchone()
        test_conn.close()
        if not row or row[0] != "ok":
            raise ValueError(f"SQLite PRAGMA integrity_check failed on backup: {row}")

        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(backup_file, dest)
        return True
    else:
        db_url = settings.DATABASE_URL
        res = os.system(f"psql {db_url} -f {backup_file}")
        return res == 0


def run_verification_drill() -> bool:
    print("[DRILL] Starting database backup and restore verification drill...")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_backup_dir = Path(tmpdir) / "backups"
        manifest_path = backup_database(tmp_backup_dir)
        print(f"[DRILL] Backup created: {manifest_path.name}")

        restore_target = Path(tmpdir) / "restored_test.db"
        ok = restore_database(manifest_path, target_path=restore_target)
        assert ok, "Restore returned False"
        assert restore_target.exists(), "Restored target file does not exist"

        # Verify restored DB readability & table counts
        conn = sqlite3.connect(str(restore_target))
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
        table_count = cur.fetchone()[0]
        conn.close()
        print(f"[DRILL] Restored DB verified. Valid tables: {table_count}")
        assert table_count >= 10, f"Expected >= 10 tables, found {table_count}"

    print("[DRILL] PASS: Backup, checksum verification, and restore drill passed with zero errors.")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="CraftLens Database Backup & Restore")
    parser.add_argument("--backup", action="store_true", help="Create point-in-time database backup")
    parser.add_argument("--restore", type=Path, help="Restore from manifest.json file")
    parser.add_argument("--target", type=Path, help="Optional restore destination path")
    parser.add_argument("--drill", action="store_true", help="Run automated backup & restore verification drill")
    args = parser.parse_args()

    if args.drill:
        success = run_verification_drill()
        sys.exit(0 if success else 1)
    elif args.backup:
        out = backup_database()
        print(f"Backup manifest written: {out}")
    elif args.restore:
        ok = restore_database(args.restore, args.target)
        print("Restore successful." if ok else "Restore failed.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
