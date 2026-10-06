# Validation

Observed 6 October 2026 UTC. Local state: VALIDATED. Python 3.12.14, Linux x86_64.
Original synthetic fixtures; no competitor workloads measured. CPU/hardware timing is not used for superiority claims.

| Check | Directory | Expected exit | Observed exit |
|---|---|---:|---:|
| `python -m unittest -v` | source | 0 | 0 |
| `python -m compileall -q har_budget.py` | source | 0 | 0 |
| `python -m build` | source | 0 | 0 |
| `<preparation>/project-envs/har-budget/bin/python -m pip install --no-deps <preparation>/projects/har-budget/dist/har_budget-0.1.0-py3-none-any.whl` | source | 0 | 0 |
| `<preparation>/project-envs/har-budget/bin/python -m pip check` | source | 0 | 0 |
| `<preparation>/project-envs/har-budget/bin/har-budget --help` | empty directory | 0 | 0 |
| `<preparation>/project-envs/har-budget/bin/har-budget <preparation>/projects/har-budget/example.har --budget <preparation>/projects/har-budget/budget.json` | empty directory | 0 | 0 |
| `<preparation>/project-envs/har-budget/bin/har-budget <preparation>/projects/har-budget/example.har --budget <preparation>/project-empty/har-budget/bad-input` | empty directory | 1 | 1 |

A built wheel was installed without runtime dependencies in a fresh virtual environment.
Installed command help, documented synthetic demo and a meaningful failure input ran
outside the source tree. Bytecode compilation is syntax verification, not a static type checker.
Unit tests exercise the documented core and rejection contracts; inspect the test source.

Build tooling uses setuptools/build from the package registry. There are zero runtime
third-party dependencies. The current shared Python runtime/build/dev audit reported no
known findings; unsupported optional extras elsewhere do not change this project's empty
runtime dependency set. Build toolchains and future advisory feeds can change.

Windows, macOS and Python versions other than the local 3.12 interpreter were not
locally tested. Linux 3.11/3.12/3.13 are configured in CI; publication is LIVE only after
remote checks pass. No cross-tool performance benchmark or user/adoption results claimed.

The intentionally failing installed fixture exited 1, demonstrating the gate.
Unknown sizes/times and empty captures do not silently pass; origins are retained but request details are omitted.

Remote CI on Python 3.11 exposed preinstalled setuptools 79.0.1 (PYSEC-2026-3447). The build requirement and CI bootstrap now require setuptools >=83; the vulnerability gate remains enabled. Remote verification of this correction is required before LIVE.
