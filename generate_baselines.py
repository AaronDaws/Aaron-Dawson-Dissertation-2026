from __future__ import annotations

import random # random baseline
import secrets # secrets baseline
from pathlib import Path
import numpy as np # used for pcg64 baseline
from utils import save_sequence

NUMBER_OF_BITS = 1_000_000 # the required number of bits in every run
NUMBER_OF_BYTES = NUMBER_OF_BITS // 8 # the selected generators return bytes, so convert bits to bytes
NUMBER_OF_RUNS = 10 # define the amount of runs to generate for every baseline
OUT_DIR = Path("runs") # directory root where all runs will be stored

def pyrandom_bytes(n_bytes: int, seed: int) -> bytes: # returns bytes of python random data
    rng = random.Random(seed) # seed for bytes
    return rng.randbytes(n_bytes)

def pcg64_bytes(n_bytes: int, seed: int) -> bytes: # returns bytes of numpy pcg64 data
    rng = np.random.default_rng(seed)
    return rng.bytes(n_bytes)

def csprng_bytes(n_bytes: int) -> bytes: # returns bytes of python secrets data
    return secrets.token_bytes(n_bytes)

def main() -> None: # main function  generates all baselines
    print(f"Generating {NUMBER_OF_RUNS} runs per baseline...")
    print(f"Bits per run: {NUMBER_OF_BITS}")                    # used prints to debug errors in generation
    print(f"Bytes per run: {NUMBER_OF_BYTES}") 

    for i in range(NUMBER_OF_RUNS):
        run_id = f"run_{i:03d}" # no pad folder name like 'run_001' etc
        print(f"Creating {run_id}...") # so i can follow the generation process
        # build seed for python random
        seed_pyrandom = 1000 + i
        pyrandom = pyrandom_bytes(NUMBER_OF_BYTES, seed_pyrandom) # generate bytes of python random for the run
        save_sequence(
            base_dir=OUT_DIR, # root directory
            provider="baseline", # label run as baseline
            model="python_random",
            run_id=run_id,
            raw_text=pyrandom.hex(),
            clean_hex=pyrandom.hex(),
            metadata={
                "generator": "python_random",
                "seed": seed_pyrandom,
            },
        )

        seed_pcg = 2000 + i # seed for this run
        pcg = pcg64_bytes(NUMBER_OF_BYTES, seed_pcg) # generate pcg bytes
        save_sequence(
            base_dir=OUT_DIR,
            provider="baseline",
            model="numpy_pcg64",
            run_id=run_id,
            raw_text=pcg.hex(),
            clean_hex=pcg.hex(),
            metadata={
                "generator": "numpy_pcg64",
                "seed": seed_pcg,
            },
        )

        cs = csprng_bytes(NUMBER_OF_BYTES) # generate python secrets bytes
        save_sequence(
            base_dir=OUT_DIR,
            provider="baseline",
            model="python_secrets_csprng",
            run_id=run_id,
            raw_text=cs.hex(),
            clean_hex=cs.hex(),
            metadata={
                "generator": "python_secrets_csprng",
                "seed": None,
            },
        )

if __name__ == "__main__":
    main() # call main generation routine