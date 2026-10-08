"""W8-007 safe, actionable projection of typed project-save failures.

The projection intentionally contains no project text, file path or OS exception.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PersistenceStage(StrEnum):
    PREPARE = "prepare"
    TEMP_CREATE = "temp_create"
    TEMP_WRITE = "temp_write"
    TEMP_SYNC = "temp_sync"
    BACKUP_CREATE = "backup_create"
    BACKUP_COPY = "backup_copy"
    BACKUP_REPLACE = "backup_replace"
    SOURCE_REPLACE = "source_replace"
    CLEANUP = "cleanup"


class PersistenceError(RuntimeError):
    """Disk failure; never concatenate private paths or raw operating-system errors."""

    def __init__(self, stage: PersistenceStage) -> None:
        self.stage = stage
        super().__init__(f"project save failed at {stage.value}")


@dataclass(frozen=True, slots=True)
class PersistenceFailureProjection:
    stage: PersistenceStage
    title: str
    detail: str
    next_action: str
    retryable: bool


def persistence_error_projection(error: PersistenceError) -> PersistenceFailureProjection:
    if error.stage is PersistenceStage.PREPARE:
        action = "Periksa folder tujuan dan izin menulis, lalu coba Simpan lagi."
    elif error.stage in {PersistenceStage.BACKUP_CREATE, PersistenceStage.BACKUP_COPY}:
        action = "Periksa ruang penyimpanan dan izin folder backup, lalu ulangi Simpan."
    elif error.stage is PersistenceStage.BACKUP_REPLACE:
        action = "Periksa akses file backup (.bak), lalu ulangi Simpan."
    elif error.stage is PersistenceStage.CLEANUP:
        action = "Periksa izin folder dan sisa file sementara sebelum mencoba lagi."
    else:
        action = "Periksa ruang penyimpanan/izin folder, lalu ulangi Simpan."
    return PersistenceFailureProjection(
        stage=error.stage,
        title="Proyek belum berhasil disimpan",
        detail="Operasi penyimpanan dibatalkan karena kegagalan penyimpanan.",
        next_action=action,
        retryable=True,
    )
