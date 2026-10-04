#!/usr/bin/env python3
"""Populate data/ and output/ from the Zenodo deposit, so the figure notebooks run
without the raw data.

The normal route builds every table from the barcode counts (Scoring.ipynb ->
Annotations.ipynb -> figure notebooks). This script is the shortcut: it downloads
the deposited tables and puts each file at the path the figure notebooks already
read, so they run unmodified.

    python scripts/fetch_zenodo_data.py --record <ZENODO_RECORD_ID>
    python scripts/fetch_zenodo_data.py --from-dir <folder with the deposit files>

What it writes:
  output/Supplementary_Table_2.tsv
  output/annotated_combined.tsv   rebuilt from Supplementary Table 2 plus the
                                  deposited extra columns (annotated_extras.tsv.gz)
  everything in figure_inputs.tar.gz (paths inside are repo-relative)
  data/interactions/{pdb_controls,predictomes_MAPK,Zhangetal_structures}

All of Us data are not in the deposit (Controlled Tier; per-variant observations
may not be redistributed). `in_aou` is written as an empty column so Fig 4 runs,
and the All of Us rows of Fig 4f and Extended Data Fig 7e are therefore empty and
should be ignored. Every other panel reproduces.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import shutil
import sys
import tarfile
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from labelseq_mapk.supplementary_table import EXTRA_COLUMNS, ST2_COLUMNS  # noqa: E402

KEY = ["library", "variant", "assay", "assay_treatment"]
#: archive -> directory it is extracted into (relative to the repo root)
ARCHIVES = {
    "figure_inputs.tar.gz": ".",
    "pdb_complexes.tar.gz": ".",
    "predictomes_MAPK.tar.gz": "data/interactions",
    "Zhangetal_structures.tar.gz": "data/interactions",
}
TABLES = ["Supplementary_Table_2.tsv.gz", "annotated_extras.tsv.gz"]


def download(record: str, dest: Path) -> None:
    """Fetch every file of a published Zenodo record into `dest`, checking MD5s."""
    with urllib.request.urlopen(f"https://zenodo.org/api/records/{record}") as r:
        meta = json.load(r)
    for f in meta["files"]:
        name, url = f["key"], f["links"]["self"]
        out = dest / name
        if out.exists() and _md5(out) == f["checksum"].split(":")[-1]:
            print(f"  have {name}")
            continue
        print(f"  downloading {name} ({f['size'] / 1e6:.0f} MB)")
        with urllib.request.urlopen(url) as r, open(out, "wb") as fh:
            shutil.copyfileobj(r, fh)
        if _md5(out) != f["checksum"].split(":")[-1]:
            raise RuntimeError(f"checksum mismatch for {name}")


def _md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def install(src: Path) -> None:
    missing = [n for n in TABLES + list(ARCHIVES) if not (src / n).exists()]
    if missing:
        raise FileNotFoundError(f"not in {src}: {missing}")

    for name, target in ARCHIVES.items():
        dest = ROOT / target
        dest.mkdir(parents=True, exist_ok=True)
        print(f"  extracting {name} -> {target}/")
        with tarfile.open(src / name) as tar:
            # "data" filter (Python >= 3.12; backported to 3.8.17+) refuses absolute
            # paths and links out of the target directory.
            if hasattr(tarfile, "data_filter"):
                tar.extractall(dest, filter="data")
            else:
                tar.extractall(dest)

    out = ROOT / "output"
    out.mkdir(exist_ok=True)
    st2_path = out / "Supplementary_Table_2.tsv"
    with gzip.open(src / "Supplementary_Table_2.tsv.gz", "rb") as fi, open(st2_path, "wb") as fo:
        shutil.copyfileobj(fi, fo)
    print(f"  wrote {st2_path.relative_to(ROOT)}")

    # The figure notebooks read annotated_combined.tsv: Supplementary Table 2's
    # columns, then EXTRA_COLUMNS, in Supplementary Table 2's row order.
    st2 = pd.read_csv(st2_path, sep="\t", low_memory=False)
    extras = pd.read_csv(src / "annotated_extras.tsv.gz", sep="\t", low_memory=False)
    table = st2.merge(extras, on=KEY, how="left", validate="one_to_one")
    assert len(table) == len(st2)
    table["in_aou"] = pd.NA          # All of Us: not redistributable
    table = table[ST2_COLUMNS + EXTRA_COLUMNS]
    table.to_csv(out / "annotated_combined.tsv", sep="\t", index=False)
    print(f"  wrote output/annotated_combined.tsv ({len(table):,} rows; in_aou empty)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--record", help="Zenodo record ID to download")
    g.add_argument("--from-dir", type=Path, help="folder already holding the deposit files")
    ap.add_argument("--download-dir", type=Path, default=ROOT / "zenodo_download",
                    help="where downloaded files are kept (default: zenodo_download/)")
    a = ap.parse_args()
    if a.record:
        a.download_dir.mkdir(parents=True, exist_ok=True)
        download(a.record, a.download_dir)
        install(a.download_dir)
    else:
        install(a.from_dir)
    print("done — the figure notebooks can now be run.")


if __name__ == "__main__":
    main()
