from __future__ import annotations

from dataclasses import dataclass
from typing import Set


ALLOWED_MIME_TYPES: Set[str] = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "text/plain",
}

MAX_DOCUMENT_SIZE_BYTES = 10 * 1024 * 1024


@dataclass(frozen=True)
class DocumentValidationResult:
    valid: bool
    reason_code: str


def validate_document_metadata(mime_type: str, size_bytes: int, checksum_sha256: str) -> DocumentValidationResult:
    if mime_type not in ALLOWED_MIME_TYPES:
        return DocumentValidationResult(False, "unsupported_mime_type")

    if size_bytes <= 0:
        return DocumentValidationResult(False, "invalid_size")

    if size_bytes > MAX_DOCUMENT_SIZE_BYTES:
        return DocumentValidationResult(False, "document_too_large")

    if not checksum_sha256 or len(checksum_sha256.strip()) < 6:
        return DocumentValidationResult(False, "invalid_checksum")

    return DocumentValidationResult(True, "document_valid")
