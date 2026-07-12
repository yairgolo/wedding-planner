from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
archive_base = BACKUP_DIR / f"wedding-planner-backup-{stamp}"

temp_dir = BACKUP_DIR / f"tmp-{stamp}"
temp_dir.mkdir()

for name in ("instance", "uploads"):
    source = ROOT / name
    if source.exists():
        shutil.copytree(source, temp_dir / name)

archive = shutil.make_archive(str(archive_base), "zip", temp_dir)
shutil.rmtree(temp_dir)
print(f"Backup created: {archive}")
