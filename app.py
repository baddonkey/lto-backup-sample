import json
import logging
from pathlib import Path

from lto_backup.config.backup_config import BackupConfig
from lto_backup.infrastructure.catalog.json_catalog_serializer import JsonCatalogSerializer
from lto_backup.infrastructure.filesystem.sha256_file_hasher import Sha256FileHasher
from lto_backup.infrastructure.simulator.simulator_tape_drive import SimulatorTapeDrive
from lto_backup.services.report_service import ReportService
from lto_backup.services.verification_service import VerificationService
from lto_backup.wiring.container import build_backup_service

# --- configure logging ---
_log_cfg_path = Path(__file__).parent / "logging.json"
_log_cfg = {}
if _log_cfg_path.exists():
    with _log_cfg_path.open() as _f:
        _log_cfg = json.load(_f)

logging.basicConfig(
    level=getattr(logging, _log_cfg.get("log_level", "INFO").upper(), logging.INFO),
    format=_log_cfg.get("format"),
    datefmt=_log_cfg.get("datefmt"),
)

source = Path.home() / "Downloads"
tapes  = Path.home() / "temp/tape-output"
reports = Path.home() / "temp/tape-reports"

tapes.mkdir(parents=True, exist_ok=True)

config = BackupConfig(
    source_root=source,
    tapes_root=tapes,
    tape_nominal_capacity_bytes=10_000_000_000,   
    max_container_size_bytes=1_000_000_000,
)

# --- backup ---
catalog = build_backup_service(config).run(config)
print(f"Backup complete: {len(catalog.tapes)} tape(s), {len(catalog.source_files)} file(s)")

# --- verify ---
verifier = VerificationService(
    SimulatorTapeDrive(tapes, config.tape_nominal_capacity_bytes),
    JsonCatalogSerializer(),
    Sha256FileHasher(),
)
errors = verifier.verify(catalog)
if errors:
    for e in errors:
        print("CORRUPT:", e)
else:
    print("All tapes verified clean.")

# --- report ---
report_path = ReportService().generate(catalog, errors, reports)
print(f"Report written to: {report_path}")