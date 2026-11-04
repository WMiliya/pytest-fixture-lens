# Report JSON schema

FixtureLens writes `report.json` with `schema_version: 1`.

## Top level

```json
{
  "schema_version": 1,
  "generator": { "name": "fixturelens", "version": "0.1.0" },
  "summary": {},
  "hotspots": ["fixture-key"],
  "fixtures": [],
  "tests": [],
  "limitations": []
}
```

## summary

| Field | Type | Meaning |
| --- | --- | --- |
| `tests` | int | Number of test records. |
| `fixtures` | int | Number of observed fixture functions. |
| `setup_exclusive_ms` | float | Sum of exclusive fixture setup time. |
| `reused_setups` | int | Sum of fixture reuse counts. |
| `failed_tests` | int | Tests with outcome `failed` or `error`. |
| `exitstatus` | int | pytest session exit status. |

## fixtures[]

| Field | Type | Meaning |
| --- | --- | --- |
| `key` | string | Stable function-level fixture key. |
| `name` | string | Fixture argument name. |
| `scope` | string | pytest scope: session, package, module, class, function. |
| `source` | string | Source path relative to rootdir when possible. |
| `line` | int | Source line. |
| `dependencies` | string[] | Fixture keys this fixture depends on. |
| `requested_count` | int | Tests whose closure includes this fixture. |
| `setup_count` | int | Observed setup events. |
| `reuse_count` | int | `max(0, requested_count - setup_count)`. |
| `total_exclusive_ms` | float | Total exclusive setup time. |
| `total_inclusive_ms` | float | Total inclusive setup time. |
| `avg_exclusive_ms` | float | Average exclusive setup time. |
| `param_indices` | int[] | Observed parameter indices, if mapped. |

## tests[]

| Field | Type | Meaning |
| --- | --- | --- |
| `nodeid` | string | pytest node ID. |
| `location` | array | pytest item location. |
| `outcome` | string | `passed`, `failed`, `error`, `skipped`, or `unknown`. |
| `phases` | object | Setup/call/teardown outcome and duration. |
| `requested` | string[] | Fixture keys in the test closure. |
| `setup_events` | object[] | Fixture setup events observed during the test. |

### setup_events[]

| Field | Type | Meaning |
| --- | --- | --- |
| `key` | string | Fixture key. |
| `name` | string | Fixture name. |
| `scope` | string | Fixture scope. |
| `param_index` | int or null | Parameter index when mapped. |
| `inclusive_ms` | float | Inclusive setup time. |
| `exclusive_ms` | float | Exclusive setup time. |
| `failed` | bool | Whether the fixture setup failed. |

## Stability

`schema_version` may change when fields are added or renamed. Consumers should check it before parsing.
