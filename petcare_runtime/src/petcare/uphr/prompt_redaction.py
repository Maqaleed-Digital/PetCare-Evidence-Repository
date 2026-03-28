from __future__ import annotations

import re
from dataclasses import dataclass


EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
# Matches E.164-style numbers starting with + (e.g. +966500000000)
PHONE_PATTERN = re.compile(r"\+\d[\d\s-]{7,}\d")
# Matches pure contiguous digit sequences of 10-20 digits (microchip IDs)
MICROCHIP_PATTERN = re.compile(r"\b\d{10,20}\b")


@dataclass(frozen=True)
class PromptRedactionResult:
    redacted_text: str
    applied: bool


def redact_prompt_safe_text(raw_text: str) -> PromptRedactionResult:
    redacted = raw_text
    redacted = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", redacted)
    redacted = PHONE_PATTERN.sub("[REDACTED_PHONE]", redacted)
    redacted = MICROCHIP_PATTERN.sub("[REDACTED_ID]", redacted)
    return PromptRedactionResult(redacted_text=redacted, applied=redacted != raw_text)
