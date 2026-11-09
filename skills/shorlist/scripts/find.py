"""Look up rows of the ShorList catalogue bundled with this skill. Standard library only;
reads ../data/ next to this script and nothing else, and makes no network request.

    python3 find.py --stats
    python3 find.py --id SL-0001 --full
    python3 find.py --family ML-KEM --kind config_value
    python3 find.py --product nginx --decoys
    python3 find.py --text getInstance
    python3 find.py --in path/to/file      # catalogue literals that occur verbatim in a file

Filters combine with AND; text filters are case-insensitive substrings.
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"


def load() -> tuple[dict, list[dict]]:
    meta = json.loads((DATA / "catalogue.json").read_text())
    rows = []
    for p in sorted(DATA.glob("rows-*.jsonl")):
        rows += [json.loads(line) for line in p.read_text().splitlines() if line]
    if len(rows) != meta["rows"]:
        raise SystemExit(f"expected {meta['rows']} rows, read {len(rows)}: the data folder is incomplete")
    return meta, rows


def main() -> None:
    ap = argparse.ArgumentParser(description="Look up ShorList rows.")
    ap.add_argument("--id", action="append", help="row id, e.g. SL-0001 (repeatable)")
    ap.add_argument("--family", help="exact family, e.g. RSA, ML-KEM, SHA-1")
    ap.add_argument("--kind", help="exact form_kind, e.g. api_call, config_value, oid")
    ap.add_argument("--axis", choices=["quantum", "weak", "defect"])
    ap.add_argument("--product", help="substring of language_or_product, e.g. java, nginx")
    ap.add_argument("--text", help="substring of the literal")
    ap.add_argument("--cwe", help="defect rows with this CWE, e.g. CWE-327")
    ap.add_argument("--in", dest="infile", help="rows whose literal occurs verbatim in this file")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--decoys", action="store_true", help="only decoys (negative: true)")
    g.add_argument("--positives", action="store_true", help="only positive rows")
    ap.add_argument("--full", action="store_true", help="print whole rows as JSON")
    ap.add_argument("--limit", type=int, default=50, help="rows to print (default 50, 0 = all)")
    ap.add_argument("--stats", action="store_true", help="counts by axis, family and form_kind")
    a = ap.parse_args()

    meta, rows = load()
    print(f"ShorList {meta['version']} ({meta['rows']} rows, catalogue sha256 "
          f"{meta['catalogue_sha256_of_release'][:16]}..., CC BY 4.0, DOI {meta['doi']})")

    if a.id:
        ids = {i.upper() for i in a.id}
        rows = [r for r in rows if r["id"] in ids]
    if a.family:
        rows = [r for r in rows if r["family"] == a.family]
    if a.kind:
        rows = [r for r in rows if r["form_kind"] == a.kind]
    if a.axis:
        rows = [r for r in rows if r["axis"] == a.axis]
    if a.product:
        rows = [r for r in rows if a.product.lower() in r["language_or_product"].lower()]
    if a.text:
        rows = [r for r in rows if a.text.lower() in r["literal"].lower()]
    if a.cwe:
        rows = [r for r in rows if (r.get("defect") or {}).get("cwe", "").upper() == a.cwe.upper()]
    if a.decoys:
        rows = [r for r in rows if r["negative"]]
    if a.positives:
        rows = [r for r in rows if not r["negative"]]
    if a.infile:
        text = Path(a.infile).read_text(errors="replace")
        rows = [r for r in rows if r["literal"].strip() and r["literal"].strip() in text]
        print("Verbatim literal matches only. A match is not a finding (decoys match too), and no "
              "match does not mean the file has no cryptography.")

    if a.stats:
        for field in ("axis", "family", "form_kind"):
            c = collections.Counter(r[field] for r in rows)
            print(f"\n{field}: " + ", ".join(f"{k} {v}" for k, v in c.most_common()))
        print(f"\nrows {len(rows)}, decoys {sum(r['negative'] for r in rows)}")
        return

    shown = rows if a.limit == 0 else rows[:a.limit]
    print(f"{len(rows)} rows match" + (f"; showing {len(shown)}" if len(shown) < len(rows) else ""))
    for r in shown:
        if a.full:
            print(json.dumps(r, ensure_ascii=False, indent=2))
        else:
            tag = "DECOY" if r["negative"] else "pos"
            print(f"{r['id']}\t{r['axis']}\t{tag}\t{r['family']}\t{r['form_kind']}\t"
                  f"{r['language_or_product']}\t{r['literal']}")


if __name__ == "__main__":
    main()
