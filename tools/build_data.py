"""Build the plugin's data from a ShorList release tree.

    git -C <shorlist clone> archive v0.2.0 forms schema VERSION | tar -x -C <empty dir>
    python3 tools/build_data.py <empty dir> skills/shorlist/data

Needs PyYAML (the release stores rows as YAML). The plugin itself only reads the JSON this
writes, with the Python standard library.

What changes against the release, and nothing else:
- rows are stored as JSON Lines, several rows per file, so that the plugin stays under the
  directory's limits (512 files, 256 KiB per file);
- each row gets `axis` (quantum, weak or defect), computed as the generator does;
- in rows whose context_template holds a PEM block with a body (the published throwaway
  test keys), the template is removed and `plugin_note` says so. The row's literal (the
  PEM label line) and `expected` are unchanged.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import yaml

SHARD_LIMIT = 200 * 1024  # bytes per file, under the 256 KiB limit
AXIS_OF_GROUP = {"quantum_vulnerable": "quantum", "post_quantum": "quantum",
                 "classically_weak": "weak", "defect_only": "defect"}
PEM_WITH_BODY = re.compile(r"^-----BEGIN [^-]+-----\n[A-Za-z0-9+/=]{16,}$", re.M)
REPO = "https://github.com/shorlist/shorlist"


def catalogue_sha256(root: Path) -> str:
    """Same as generator/shorlist/catalogue.py: path, NUL, bytes, NUL per forms/*.yaml."""
    h = hashlib.sha256()
    for p in sorted((root / "forms").glob("*.yaml")):
        h.update(p.relative_to(root).as_posix().encode())
        h.update(b"\0")
        h.update(p.read_bytes())
        h.update(b"\0")
    return h.hexdigest()


def main(src: Path, out: Path) -> None:
    version = (src / "VERSION").read_text().strip()
    groups = yaml.safe_load((src / "schema" / "families.yaml").read_text())
    axis_of_family = {name: AXIS_OF_GROUP[g] for g, fams in groups.items() for name in fams}

    rows, stripped = [], []
    for p in sorted((src / "forms").glob("*.yaml")):
        row = yaml.safe_load(p.read_text())
        if row.get("row_kind") == "defect":
            row["axis"] = "defect"
        elif "weakness" in row or axis_of_family[row["family"]] == "weak":
            row["axis"] = "weak"
        else:
            row["axis"] = "quantum"
        if PEM_WITH_BODY.search(row["context_template"]):
            row["context_template"] = None
            row["plugin_note"] = ("context_template removed in the plugin copy: it holds "
                                  "throwaway test key material. Full row: "
                                  f"{REPO}/blob/v{version}/forms/{row['id']}.yaml")
            stripped.append(row["id"])
        rows.append(row)

    for old in out.glob("rows-*.jsonl"):
        old.unlink()
    shards, buf, size = [], [], 0
    for row in rows:
        line = json.dumps(row, ensure_ascii=False, sort_keys=True, default=str) + "\n"
        if buf and size + len(line.encode()) > SHARD_LIMIT:
            shards.append(buf)
            buf, size = [], 0
        buf.append(line)
        size += len(line.encode())
    shards.append(buf)
    for i, lines in enumerate(shards, start=1):
        (out / f"rows-{i:02d}.jsonl").write_text("".join(lines))

    meta = {
        "catalogue": "ShorList",
        "version": version,
        "catalogue_sha256_of_release": catalogue_sha256(src),
        "sha256_note": "sha256 of the release's forms/*.yaml (generator rule), not of these JSON files",
        "rows": len(rows),
        "doi": "10.5281/zenodo.23974515",
        "source": f"{REPO}/tree/v{version}",
        "licence_data": "CC BY 4.0",
        "pem_bodies_removed_from": stripped,
        "shards": len(shards),
    }
    (out / "catalogue.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
