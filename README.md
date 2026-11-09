# ShorList for Claude

[ShorList](https://github.com/shorlist/shorlist) is an open, versioned catalogue of the
*forms* in which cryptographic algorithms appear in source code and configuration: the
exact text, the minimal file it stands in, what a scanner should report for it, and the
primary source that defines it. Decoys (text that names an algorithm but is not a use of
it) measure false alarms. This plugin bundles **ShorList v0.2.0** (2035 rows, DOI
[10.5281/zenodo.23974515](https://doi.org/10.5281/zenodo.23974515)) as one Claude skill.

## Where it works

The plugin contains one skill and nothing else: no hooks, no MCP server, no commands, no
agents, no scripts. Every file in it is Markdown, JSON or the PNG icon. Skills load in
**claude.ai chat**, **Cowork** and **Claude Code**. In chat Claude reads the data files with
code execution, so code execution has to be on.

## Install

In claude.ai or Cowork: **Customize > Plugins**, find ShorList in the directory. In Claude
Code:

```
/plugin marketplace add shorlist/shorlist-plugin
/plugin install shorlist@shorlist
```

## Use it

Ask Claude, for example:

- "Which forms of ML-KEM does ShorList list for nginx and OpenSSH?"
- "Show ShorList row SL-0001 with its source."
- "What decoys does ShorList have for Java?"
- "Which ShorList literals occur verbatim in this file?"
- "How do I score my scanner against ShorList?"

Claude answers with row ids, the catalogue version and each row's primary source. For
scoring a scanner, the skill explains the steps; the measurement itself is made by the
generator in the [ShorList repository](https://github.com/shorlist/shorlist), on your own
machine, and Claude asks before cloning or installing anything.

## What is in the catalogue

| axis | rows | positive | decoys |
|---|---|---|---|
| quantum (Shor-vulnerable and post-quantum) | 1537 | 1368 | 169 |
| weak (classically weak algorithms and parameters) | 311 | 280 | 31 |
| defect (misuse that one line shows, scored on the CWE) | 187 | 162 | 25 |

The families, languages and products covered are listed in the catalogue's README,
section "Scope of v0.2".

## What it does not do

- **It is not a scanner.** Looking up which literals occur in a file is a verbatim string
  match. A match is not a finding (decoys match too), and no match does not mean the file
  has no cryptography.
- **It is not recall.** The catalogue is not complete and does not claim to be; *M of N*
  is recognition of the listed forms, not a share of all the cryptography that exists.
- **It is not finding in a real tree.** Each form is planted alone, in a minimal file.
  Whether a scanner reaches that file in a real repository (file types, sizes, vendored
  code, generated code, archives) is a different measurement, coverage, and is not made
  here.
- **Misuse only where one line shows it.** Misuse that depends on data flow across
  functions or files is not in the catalogue.
- Known not covered in v0.2: families with no entry in the vocabulary yet (Streamlined
  NTRU Prime, pre-standard Kyber names, SM2/SM3/SM4, GOST, Blowfish, IDEA,
  bcrypt/scrypt/Argon2); vendor network configuration beyond a few FortiOS and Junos
  lines; binaries and archives.

## What it sends

Nothing. Claude reads the bundled data files; the skill makes no network request and
stores nothing. If you ask how to score
a scanner, Claude proposes cloning the public ShorList repository from GitHub; that
happens only in Claude Code, only after you agree, and is an ordinary command you see
before it runs.

## How the data was made

The data under the skill's data folder is built from the v0.2.0 tag of the catalogue
repository by a build script kept outside the plugin, since the plugin ships no code. It differs from the release in four ways, and in nothing else:

1. Rows are stored as JSON arrays, one row per line and about 150 rows per file, instead
   of one YAML file per row, to stay within the plugin directory's file limits.
2. Each row carries `axis`, computed as the generator computes it.
3. Ten PEM rows (SL-3596 to SL-3604 and SL-3616) carry real, throwaway test keys in the
   release, published on purpose. In this copy their minimal file is removed and a note
   links the full row; the literal (the PEM label) and the expected result are unchanged.
4. The 24 hard-coded-key rows (CWE-321) carry made-up keys in the release. In this copy their
   minimal file is removed and long key bytes in the literal are replaced by
   `<KEY-BYTES-REMOVED>`, so that a secret scanner does not read them as real keys; a note
   links the full row. The expected result is unchanged.

The catalogue sha256 recorded with the data is the release's own (over its YAML files, as
the generator computes it), so a result made with the generator on v0.2.0 is on the same
rows.

## Conflict of interest

ShorList was started by Stanimir Tenev of Elkan Electronic, who also writes qrp-mcp, one of
the scanners it can measure. The catalogue's rules do not depend on any scanner's output;
rows are admitted on their primary source, not on whether qrp-mcp detects them; qrp-mcp's
own misses are published in the catalogue's results like anyone else's. No reviewer outside
Elkan Electronic has checked those numbers yet.

## Licences

The catalogue data is under [CC BY 4.0](LICENSE-DATA.md): credit "ShorList v0.2.0, DOI
10.5281/zenodo.23974515". The script and the build tool are under
[Apache-2.0](LICENSE).

Issues and corrections to rows: [github.com/shorlist/shorlist](https://github.com/shorlist/shorlist/issues).
