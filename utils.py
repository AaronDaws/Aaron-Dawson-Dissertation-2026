from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

# regex: matches one or more hex characters
HEX_RE = re.compile(r"^[0-9a-f]+$", re.IGNORECASE) 

# strips whitespace and validates the hexadecimal text
def normalize_hex(text: str, expected_chars: int | None = None) -> str:
    
    cleaned = "".join(text.split()).lower() # remove whitespace and convert to lowercase

    if not HEX_RE.fullmatch(cleaned): # raise error if text contains anything other than hex characters
        raise ValueError("Found non-hex characters!.")
    # check cleaned text matches the expected length
    if expected_chars is not None and len(cleaned) != expected_chars:
        raise ValueError( # raise error if length doesnt match
            f"Expected {expected_chars} hex chars, got {len(cleaned)} !!."
        )

    return cleaned # return the validated string


def hex_to_bytes(hex_string: str) -> bytes: # convert hex to raw bytes
    return bytes.fromhex(hex_string)


def bytes_to_ascii_bits(data: bytes) -> str: # converts raw bytes to an ASCII bitstring for NIST STS ease of use
    return "".join(f"{b:08b}" for b in data)


def sha256_hex(data: bytes) -> str: # not nessesarily needed but returns the SHA-256 
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def save_sequence( #define save routine used by baseline and LLM scripts
    base_dir: Path,
    provider: str,
    model: str,
    run_id: str,
    raw_text: str,
    clean_hex: str,
    metadata: dict[str, Any],
) -> Path:
    # 1 run is saved as raw model output, normalised hex,
    # raw binary and ASCII bitstring for NIST STS

    run_dir = base_dir / provider / model / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    data = hex_to_bytes(clean_hex)

    (run_dir / "raw_output.txt").write_text(raw_text, encoding="utf-8")
    (run_dir / "sequence.hex").write_text(clean_hex, encoding="utf-8")
    (run_dir / "sequence.bin").write_bytes(data)                        # save each representation
    (run_dir / "sequence_bits.txt").write_text(
        bytes_to_ascii_bits(data), encoding="ascii"
    )

    enriched = { # metadata dictionary, adds size and integrity info
        **metadata,
        "n_bytes": len(data),
        "n_bits": len(data) * 8,
        "sha256": sha256_hex(data),
    }
    write_json(run_dir / "metadata.json", enriched) #writes this to metadata.json
    return run_dir