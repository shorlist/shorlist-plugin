---
name: shorlist
description: Look up ShorList, an open catalogue (v0.2.0, 2035 rows) of the forms in which cryptographic algorithms appear in source code and configuration, each with a primary source, plus decoys that name an algorithm without using it. Use when asked which concrete forms of an algorithm (RSA, ECDSA, ML-KEM, SHA-1, 3DES ...) a scanner should recognise in a language or product, what a ShorList row (SL-xxxx) says and where its source is, which catalogue literals occur verbatim in a file, or how to score a cryptography scanner or CBOM tool against ShorList.
---

# ShorList

The catalogue is bundled in `data/` next to this file: `catalogue.json` (version, the
release's catalogue sha256, DOI, licence) and `rows-01.json` … `rows-13.json`, each a JSON
array with one row per line. The plugin ships no script: read the files with your own tools.
In Claude Code, search them with Grep (a row is one line, so a match is a whole row) or load
them in a short program; in claude.ai chat, load them with code execution from the skill
folder. Make no network request to answer from the catalogue.

## Row fields

| field | meaning |
|---|---|
| `id` | `SL-nnnn` |
| `axis` | `quantum`, `weak` or `defect` |
| `negative` | `true` for a decoy |
| `family`, `parameter_set`, `role` | what the form uses |
| `form_kind` | `api_call`, `api_string`, `config_key`, `config_value`, `registry_id`, `oid`, `curve_name`, `cli`, `file_format` |
| `language_or_product` | where the form appears (substring match is the useful one) |
| `literal` | the exact text of the form |
| `context_filename`, `context_template` | the minimal file it is planted in |
| `expected` | what a scanner should report (for a decoy: what it would wrongly report) |
| `source` | primary source, with section and quote |
| `weakness`, `defect.cwe` | the standard or CWE for the weak and defect axes |

Typical questions: counts by axis or family; one row in full with its source; the forms of
a family for a product; the decoys of a family; the misuse rows of a CWE; which catalogue
literals occur verbatim in a given file (a plain string match, see the limits below).

## How to answer

- Cite rows by id, with the catalogue version and the row's `source` URL and section.
  Rows are CC BY 4.0: credit "ShorList v0.2.0, DOI 10.5281/zenodo.23974515".
- A row is a **form**: the exact text (`literal`), the minimal file it stands in
  (`context_filename`, `context_template`), and what a scanner should report (`expected`).
- `negative: true` is a **decoy**: text that names an algorithm but is not a use of it
  (a ban list, a comment, a log string, a switch set to off). For a decoy, `expected` is
  what a scanner would wrongly report.
- The three axes are reported apart: `quantum` (Shor-vulnerable and post-quantum forms),
  `weak` (classically weak algorithms and parameters, with the standard that says so in
  `weakness`), `defect` (misuse scored on the CWE in `defect.cwe`).
- Ten PEM rows (SL-3596 to SL-3604, SL-3616) have no `context_template` in this copy: it
  held published throwaway key material. Their `plugin_note` links the full row.
- The 24 hard-coded-key rows (CWE-321) have no `context_template` in this copy, and long
  key bytes in their literal read `<KEY-BYTES-REMOVED>`, so that a secret scanner does not take
  the made-up keys for real ones. Their `plugin_note` links the full row; quote that row when
  the exact literal matters.

## What this does not do

Say these plainly when they matter; do not soften them.

- **It is not a scanner.** Matching literals against a file is a verbatim string match of catalogue literals. A
  match is not a finding (decoys match too), and no match does not mean the file has no
  cryptography. For an inventory of a real code base, use a scanner.
- **It is not recall.** The catalogue is not complete and does not claim to be. A
  scanner's *M of N* on ShorList is recognition of the listed forms, not a share of all the
  cryptography that exists.
- **It is not finding in a real tree.** Each form is planted alone, in a minimal file.
  Whether a scanner reaches that file in a real repository is a different measurement and
  is not made here.
- **Misuse only where one line shows it.** Misuse that depends on data flow across
  functions or files is not in the catalogue.
- Known not covered in v0.2: families with no entry in the vocabulary yet (Streamlined
  NTRU Prime, pre-standard Kyber names, SM2/SM3/SM4, GOST, Blowfish, IDEA,
  bcrypt/scrypt/Argon2); vendor network configuration beyond a few FortiOS and Junos lines;
  binaries and archives.

## Scoring a scanner

Scoring plants every row in its own minimal tree, runs the scanner on each, and scores
its output. That is done by the generator in the ShorList repository, not by this skill:
it needs the scanner installed (several run in containers) and runs only on the user's
own machine, so in practice in Claude Code.

1. Ask the user before cloning or installing anything. Work in a clone of
   https://github.com/shorlist/shorlist at tag `v0.2.0`, so the result is on the same
   rows as this copy (catalogue sha256 in `data/catalogue.json`).
2. Follow that repository's README, sections "Running the generator" and "Adding a
   scanner". An adapter is the only place that knows a scanner's field names.
3. Report the result in the catalogue's own words: "Of N positive forms in ShorList
   v0.2.0, <scanner and version> recognises M; of K decoys it reports L as a use", per
   axis, with the "without registry rows" figure beside the quantum one.

The README's Results section has measurements of several tools on v0.2.0. qrp-mcp, one of
them, is written by the author of ShorList; say so whenever you cite its row.
