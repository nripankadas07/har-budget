# har-budget

Groups HTTP(S) HAR requests by normalized origin, evaluates byte/request/p95 budgets and exposes unknown measurements.

Built for performance engineers reviewing exported browser HAR files in CI or offline. Budgets need trustworthy transfer bytes and durations; treating unknown cache sizes as zero gives misleading results. HAR files can contain credentials and bodies.

## Quickstart

Python 3.11 or later. No runtime dependencies, service account or API key.
Clone the public source, create an isolated environment and install:

```sh
git clone https://github.com/nripankadas07/har-budget.git
cd har-budget
python -m venv .venv
. .venv/bin/activate
python -m pip install .
har-budget example.har --budget budget.json
```

Expected synthetic demo outcome: two origins, known transfers 2168 and 4296 bytes, zero violations. JSON goes to stdout.
Use `--help` for options. On Windows, activate with `.venv\Scripts\activate`.
Windows is not locally validated in this launch; remote CI covers Linux Python 3.11/3.12/3.13.

## Contract

Normalize origins and default ports; keep unknown sizes/times visible; honor cache zero and encoded transfer sizes; compute nearest-rank p95; support wildcard and origin override budgets; reject malformed/duplicate JSON and nonfinite metrics; omit request secrets.

Exit 0 means the supported input has no gated finding; 1 means a finding or gate failure;
2 means malformed or unsupported input/coverage. Read the JSON counts and limitations
before interpreting a zero result as comprehensive validation.

## Limitations

HAR 1.2 HTTP(S) entries only, at most 50 MB and 100000 entries. _transferSize, when present, takes precedence; otherwise bodySize plus headersSize must both be known. This differs from decoded content size. p95 is nearest-rank over known request elapsed times, not page-load percentile across repeated runs. Unknowns fail by default; --allow-unknown retains visible counts. Empty capture fails. No network, capture collection, complete HAR schema validation or hardware benchmarks. Reports retain origin hostnames; they omit paths, queries, userinfo, cookies, headers and bodies.

## Verify and contribute

```sh
python -m unittest -v
python -m compileall -q har_budget.py
python -m pip install build
python -m build
```

The tests exercise successful behavior and meaningful failure cases. See
[validation](VALIDATION.md), [research](RESEARCH.md), [contribution guidance](CONTRIBUTING.md)
and [security guidance](SECURITY.md). Open a reproducible issue with a synthetic fixture;
do not post private exports or credentials. MIT licensed; implementation is original,
with no competitor code or prose copied.
