# AGENTS.md for wpvdb playground demo

Agent guidance for this repository. Keep public product documentation in `README.md`; keep this file focused on implementation boundaries and known Playground caveats.

## Boundaries

This repo owns Playground packaging for the WPVDB demo:

- Blueprints.
- Sample content.
- Precomputed vectors.
- Preset query UI.
- Demo mode glue.

Keep ownership split by repo:

- Core SQLite fallback behavior, runtime detection, REST query handling, and provider settings belong in `wpvdb`.
- Shared search algorithms belong in `wpvdb-search`.
- The Smart Search route, React UI, public REST adapter, examples, and browser assets belong in `wpvdb-smart-search`.
- Editorial blocks belong in `wpvdb-blocks`.

Do not add credentials, tokens, application passwords, private hostnames, or user-specific deployment details.

## Playground caveats

The main Blueprint is the reliable no-key demo. It loads sample content, precomputed vectors, and preset query buttons on the WPVDB dashboard.

The suite Blueprint is broader. It verifies that the following plugins can be installed and activated together on a single Playground site: `wpvdb`, `wpvdb-search`, `wpvdb-smart-search`, `wpvdb-blocks`, `wpvdb-playground-demo`.

Current no-key behavior:

- Dashboard preset queries work because they post precomputed vectors to the core `wpvdb/v1/query` endpoint.
- Related Articles can work because it compares stored source post vectors against stored candidate vectors.
- The demo plugin must keep related lookups on the preloaded `wpvdb-demo-768` model.

Current Smart Search limitation:

- Arbitrary-typed Smart Search is not currently available as an offline no-key demo.
- Dense and hybrid modes need a fresh query embedding.
- Sparse mode needs a SQLite-compatible sparse search path in `wpvdb-search`.
- Do not document typed Smart Search as working in Playground until those sibling repos implement the missing runtime paths.

## Development notes

When adding a companion plugin to a Blueprint:

- Install `wpvdb` before dependents.
- Activate this demo plugin after the companion plugins.
- Prefer release zip URLs for companion plugins so public Playground smoke tests use tagged artifacts.

Run a public Playground smoke test before committing Blueprint URL changes when practical. At minimum, verify:

- The WPVDB dashboard loads.
- All expected plugins are active.
- Dashboard presets return ranked results.
- `/smart-search/` routes.
- Related Articles returns results for preloaded posts.
