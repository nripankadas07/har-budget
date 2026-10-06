# Research and project brief

Observed: 2026-10-06T06:12:48.529565+00:00 UTC, exact query `HAR viewer`, sorted by stars descending.
[Search receipt](https://api.github.com/search/repositories?q=HAR%20viewer&sort=stars&order=desc&per_page=10). Only the first ten results were inspected;
this is not an exhaustive worldwide ranking. janodvarko/harviewer is the highest-star
relevant comparable found in this query. Comparables can serve broader/different workflows.

| Repository | Observed stars | Repository pushed UTC | License metadata |
|---|---:|---|---|
| [janodvarko/harviewer](https://github.com/janodvarko/harviewer) | 1076 | 2022-11-25T22:54:43Z | unclassified metadata |
| [ericduran/chromeHAR](https://github.com/ericduran/chromeHAR) | 498 | 2026-03-07T04:57:51Z | MIT |
| [micmro/PerfCascade](https://github.com/micmro/PerfCascade) | 286 | 2023-03-03T11:27:56Z | MIT |

Pushed timestamps are evidence of repository activity, not proof of response/support quality.
Commit observations for the original research are in [machine-readable evidence](research.json).
Latest PR activity can be dependency automation rather than substantive maintenance.

## User, need and smallest useful capability

Performance engineers reviewing exported browser HAR files in CI or offline. Budgets need trustworthy transfer bytes and durations; treating unknown cache sizes as zero gives misleading results. HAR files can contain credentials and bodies. Groups HTTP(S) HAR requests by normalized origin, evaluates byte/request/p95 budgets and exposes unknown measurements.

Read HarViewer EntrySizeInfoTip.js and docs. HarViewer issue #158 reports cache-related validation; chromeHAR issue #78 reports size sorting. Those are verified public issue reports, not requests for our budget tool; broader demand is inferred.

## Fair feature comparison

HarViewer, chromeHAR and PerfCascade visualize HAR activity. HarViewer code already distinguishes transferred versus uncompressed and unknown sizes. Our capability is a standalone budget/report contract, not a claim that viewers cannot analyze transfers.

Our install path is a source clone plus Python pip install, with no runtime third-party
dependencies. Alternatives have their documented Go/Node/Python/Rust, hosted platform or
calendar-server workflows; their setup was reviewed in current documentation, not timed.
Our example and failure checks are runnable. Our supported input surface and support are
smaller; mature alternatives have broader documentation, integrations and maintenance history.
License metadata is reported, not legal compatibility advice; no code was reused.

No equivalent cross-tool workload was measured. No speed, reliability or global ranking
superiority is claimed. Synthetic fixtures prove only our documented behavior. Negative
results and unsupported configurations are in [validation](VALIDATION.md).

## Distinctness and discovery

Compared all five candidate briefs with 138 existing README/description briefs.
Existing trace/report/diff tools do not make these five one product: their users, accepted
input contracts and working algorithms differ. The archive-preflight idea was rejected
because it overlapped the existing wheel/path safety tools. HAR/web-performance topics, reproducible synthetic budgets and privacy example.

Acceptance criteria: Normalize origins and default ports; keep unknown sizes/times visible; honor cache zero and encoded transfer sizes; compute nearest-rank p95; support wildcard and origin override budgets; reject malformed/duplicate JSON and nonfinite metrics; omit request secrets.
