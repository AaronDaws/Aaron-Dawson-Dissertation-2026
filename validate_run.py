from __future__ import annotations

import re
from pathlib import Path

from utils import save_sequence

TARGET_BITS = 1000000 # target run length in bits
TARGET_HEX_CHARS = TARGET_BITS // 4  # 250000
LINES_PER_BLOCK = 256 # number of lines per collected block
CHARS_PER_LINE = 64 #number of characters per line
HEX_RE = re.compile(r"^[0-9a-f]+$") #regex that allows only lowercase hexadecimal characters

MANUAL_RAW_DIR = Path("manual_raw") #directory for manually collected block files

OUT_DIR = Path("runs")


def validate_block(path: Path) -> str: #validates one manually collected block file
    text = path.read_text(encoding="utf-8") # read block file
    lines = text.splitlines() # split file into individual lines

    if len(lines) != LINES_PER_BLOCK: # check required number of lines
        raise ValueError( # give erorr check fails ^
            f"{path}:  expected {LINES_PER_BLOCK} lines, got {len(lines)} !!!."
        )

    for i, line in enumerate(lines, start=1): # loop through each line
        if len(line) != CHARS_PER_LINE: # check that line has 64 characters
            raise ValueError(
                f"{path}: line {i} expected {CHARS_PER_LINE} chars, got {len(line)} !."
            )
        if not HEX_RE.fullmatch(line): # make sure only contains lowercase hex
            raise ValueError(
                f"{path}: line {i} contains non-lowercase-hex characters!"
            )

    return "".join(lines) # concatenate all lines that have been validated into a continuous hex string


def process_run(model_name: str, run_dir: Path) -> None: # processes all blocks for each model
    block_files = sorted(run_dir.glob("block_*.txt"))
    if not block_files: # raise error if no block files were found with the naming pattern above ^
        raise ValueError(f"{run_dir}: no block_*.txt files found.")

    blocks: list[str] = [] # list that stores valid hex content
    block_lengths: list[int] = [] # stored the length of each block, used in the metadata of each run

    for block_file in block_files: # loop through blocks in order
        block_hex = validate_block(block_file) # validate current block and get its content 
        blocks.append(block_hex)              # append to list of blocks
        block_lengths.append(len(block_hex)) # record length

    full_hex = "".join(blocks) # Concatenate all blocks that have been validated into a long hex sequence

    if len(full_hex) < TARGET_HEX_CHARS: # check sequence above is long enough to meet target hex characters
        raise ValueError( # if not, raise error
            f"{run_dir}: not enough validated data. "
            f"Have {len(full_hex)} hex chars, need {TARGET_HEX_CHARS}."
        )

    final_hex = full_hex[:TARGET_HEX_CHARS] # truncate the sequence to exactly the target hex length

    save_sequence( #save validated run
        base_dir=OUT_DIR,
        provider="llm",
        model=f"manual__{model_name}",
        run_id=run_dir.name,
        raw_text=full_hex,
        clean_hex=final_hex,
        metadata={
            "model": model_name,
            "pilot": False,
            "target_bits": TARGET_BITS,
            "target_hex_chars": TARGET_HEX_CHARS,
            "lines_per_block": LINES_PER_BLOCK,
            "chars_per_line": CHARS_PER_LINE,
            "n_blocks_used": len(block_files),
            "source_run_dir": str(run_dir),
            "source_block_files": [str(p) for p in block_files],
            "block_lengths": block_lengths,
        },
    )

    print(f"Saved validated run: model={model_name}, run={run_dir.name}")
    #confirm the validated run was saved with message^

def main() -> None:

    model_dirs = [p for p in MANUAL_RAW_DIR.iterdir() if p.is_dir()] # get subdirectories
    if not model_dirs: # raise error if no model directories were found
        raise RuntimeError(f"No model directories found in {MANUAL_RAW_DIR} !!")

    for model_dir in sorted(model_dirs): # loop through model directories
        model_name = model_dir.name # get model name
        run_dirs = [p for p in model_dir.iterdir() if p.is_dir()] # find all runs for this model
        if not run_dirs: # if the model has no run directories (origionally for when grok and claud were to be used)
            print(f"Skipping {model_name}: no run directories found.")
            continue

        for run_dir in sorted(run_dirs): # validate and save all runs
            process_run(model_name, run_dir)


if __name__ == "__main__":
    main()