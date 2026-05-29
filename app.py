import json
import logging
from pathlib import Path

from lto_backup.config.backup_config import BackupConfig
from lto_backup.infrastructure.catalog.json_catalog_serializer import JsonCatalogSerializer
from lto_backup.infrastructure.filesystem.sha256_file_hasher import Sha256FileHasher
from lto_backup.infrastructure.simulator.simulator_tape_drive import SimulatorTapeDrive
from lto_backup.services.verification_service import VerificationService
from lto_backup.wiring.container import build_backup_service

# --- configure logging ---
_log_cfg_path = Path(__file__).parent / "logging.json"
_log_level_str = "INFO"
if _log_cfg_path.exists():
    with _log_cfg_path.open() as _f:
        _log_level_str = json.load(_f).get("log_level", "INFO")

logging.basicConfig(
    level=getattr(logging, _log_level_str.upper(), logging.INFO),
    format="%(asctime)s %(levelname)-8s %(name)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

source = Path.home() / "Downloads"
tapes  = Path.home() / "remp/tape-output"

tapes.mkdir(parents=True, exist_ok=True)

config = BackupConfig(
    source_root=source,
    tapes_root=tapes,
    tape_nominal_capacity_bytes=10_000_000_000,   # 18 TB (LTO-9)
    max_container_size_bytes=1_000_000_000,         # 100 GB containers
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