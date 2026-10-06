"""Evaluate per-origin budgets from a local HAR without exporting request details."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
from urllib.parse import urlsplit

MAX_BYTES = 50_000_000
MAX_ENTRIES = 100_000


def object_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON field')
        result[key] = value
    return result


def read_json(path: Path):
    with path.open('rb') as handle:
        raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError('JSON exceeds 50 MB')
    return json.loads(raw, object_pairs_hook=object_pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite JSON number')))


def number(value, name, unknown=False):
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
        raise ValueError(f'{name} must be a finite number')
    if unknown and value == -1:
        return None
    if value < 0:
        raise ValueError(f'{name} must be nonnegative or -1 for unknown')
    return value


def origin(url):
    if not isinstance(url, str):
        raise ValueError('request URL must be a string')
    parsed = urlsplit(url)
    if parsed.scheme not in {'http', 'https'} or not parsed.hostname:
        raise ValueError('HAR requires absolute HTTP(S) request URLs')
    host = parsed.hostname.lower().encode('idna').decode('ascii')
    if any(c.isspace() for c in host):
        raise ValueError('invalid hostname')
    if ':' in host:
        host = '[' + host + ']'
    port = parsed.port
    suffix = f':{port}' if port is not None and port != (443 if parsed.scheme == 'https' else 80) else ''
    return parsed.scheme + '://' + host + suffix


def summarize(har):
    if not isinstance(har, dict) or not isinstance(har.get('log'), dict):
        raise ValueError('expected HAR log object')
    log = har['log']
    if log.get('version') != '1.2' or not isinstance(log.get('entries'), list):
        raise ValueError('expected HAR 1.2 entries array')
    if len(log['entries']) > MAX_ENTRIES:
        raise ValueError('entry count exceeds 100000')
    groups = {}
    for entry in log['entries']:
        if not isinstance(entry, dict) or not isinstance(entry.get('request'), dict) or not isinstance(entry.get('response'), dict):
            raise ValueError('entry requires request and response objects')
        key = origin(entry['request'].get('url'))
        response = entry['response']
        if '_transferSize' in response:
            size = number(response['_transferSize'], '_transferSize', unknown=True)
        else:
            body = number(response.get('bodySize', -1), 'bodySize', unknown=True)
            headers = number(response.get('headersSize', -1), 'headersSize', unknown=True)
            size = None if body is None or headers is None else body + headers
        if size is not None and int(size) != size:
            raise ValueError('transfer size must be integer bytes')
        duration = number(entry.get('time', -1), 'time', unknown=True)
        g = groups.setdefault(key, {'origin': key, 'requests': 0, 'transfer_bytes': 0, 'unknown_sizes': 0,
                                     'unknown_times': 0, '_times': []})
        g['requests'] += 1
        if size is None:
            g['unknown_sizes'] += 1
        else:
            g['transfer_bytes'] += int(size)
        if duration is None:
            g['unknown_times'] += 1
        else:
            g['_times'].append(duration)
    result = []
    for key in sorted(groups):
        g = groups[key]
        times = sorted(g.pop('_times'))
        g['p95_ms'] = times[math.ceil(0.95 * len(times)) - 1] if times else None
        result.append(g)
    return result


def evaluate(groups, policy, allow_unknown=False):
    allowed = {'requests', 'transfer_bytes', 'p95_ms'}
    if not isinstance(policy, dict):
        raise ValueError('budget file must map origins (or *) to metric limits')
    for key, limits in policy.items():
        if key != '*' and origin(key) != key:
            raise ValueError('budget keys must be canonical origins or *')
        if not isinstance(limits, dict) or not limits or set(limits) - allowed:
            raise ValueError('budget metrics: requests, transfer_bytes, p95_ms')
        for metric, limit in limits.items():
            number(limit, metric)
            if metric != 'p95_ms' and int(limit) != limit:
                raise ValueError('request and byte limits must be integers')
    violations = []
    for g in groups:
        limits = {**policy.get('*', {}), **policy.get(g['origin'], {})}
        for metric, limit in limits.items():
            if g[metric] is not None and g[metric] > limit:
                violations.append({'origin': g['origin'], 'metric': metric, 'actual': g[metric], 'limit': limit})
        if not allow_unknown:
            for metric in ['unknown_sizes', 'unknown_times']:
                if g[metric]:
                    violations.append({'origin': g['origin'], 'metric': metric, 'actual': g[metric], 'limit': 0})
    return {'schema': 1, 'origins': groups, 'violations': violations,
            'allow_unknown': allow_unknown, 'empty_capture': not bool(groups)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture', type=Path)
    parser.add_argument('--budget', type=Path)
    parser.add_argument('--allow-unknown', action='store_true', help='permit unknown sizes/times; counts remain visible')
    args = parser.parse_args(argv)
    try:
        result = evaluate(summarize(read_json(args.capture)), read_json(args.budget) if args.budget else {}, args.allow_unknown)
        print(json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False))
        return int(bool(result['violations'] or result['empty_capture']))
    except (OSError, ValueError, TypeError, RecursionError) as exc:
        # Never echo HAR exception values; they may contain credentials or bodies.
        print('har-budget: invalid or unsupported input; inspect schema, numeric fields and size limits', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
