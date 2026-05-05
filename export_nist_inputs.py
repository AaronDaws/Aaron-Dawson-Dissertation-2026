from __future__ import annotations

import shutil # files copied with metadata
from pathlib import Path

RUNS_DIR = Path("runs") # generated runs directory
NIST_DIR = Path("nist_inputs") # where nist ready unput files will be exported


def main() -> None:
    files_exported = 0 # track how many files exported
    for bits_file in RUNS_DIR.rglob("sequence_bits.txt"): # search for all sequence_bits.txt file in 'runs'
        run_dir = bits_file.parent
        model_dir = run_dir.parent      # get directories for extraction 
        provider_dir = model_dir.parent

        provider = provider_dir.name
        model = model_dir.name      # extract each run identifier / name from its directory name
        run_id = run_dir.name

        out_name = f"{provider}__{model}__{run_id}.txt" #builds the filename of output using the above extracted info
        out_path = NIST_DIR / out_name # constructs path in the export directory

        shutil.copy2(bits_file, out_path) # copy ascii bitstring into input directory
        files_exported += 1 #files exported +1
        print(f"Copied: {bits_file} -> {out_path}") # prints message for debugging

    # shows how many files were exported and where they were saved.
    print(f"\nExported {files_exported} NIST input files to: {NIST_DIR.resolve()}")

#py files were ran from ubuntu
if __name__ == "__main__":
    main()