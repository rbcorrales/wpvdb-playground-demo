# WPVDB Playground Demo

[![WordPress](https://img.shields.io/badge/WordPress-6.5%2B-3858e9?logo=wordpress&logoColor=white)](#requirements)
[![PHP](https://img.shields.io/badge/PHP-7.4%2B-777bb4?logo=php&logoColor=white)](#requirements)
[![License](https://img.shields.io/badge/License-GPLv2%2B-blue.svg)](LICENSE)

Demo packaging for running WPVDB inside WordPress Playground.

This plugin depends on WPVDB core runtime support. Core owns SQLite fallback behavior, Playground runtime guards, and the public hooks. This demo plugin includes sample content, precomputed vectors, a preset query UI, and public Blueprints.

## Requirements

| Requirement | Version or notes |
|---|---|
| WordPress | 6.5 or newer |
| PHP | 7.4 or newer |
| [`wpvdb`](https://github.com/rbcorrales/wpvdb) | Runtime support branch with SQLite and Playground hooks |
| WordPress Playground | Public Blueprint or compatible custom host |

## Blueprints

| Blueprint | Installs | Purpose |
|---|---|---|
| `playground/blueprint.json` | [`wpvdb`](https://github.com/rbcorrales/wpvdb), [`wpvdb-playground-demo`](https://github.com/rbcorrales/wpvdb-playground-demo) | Main public demo. Loads sample content, precomputed vectors, and preset query buttons on the WPVDB dashboard. |
| `playground/blueprint-suite.json` | [`wpvdb`](https://github.com/rbcorrales/wpvdb), [`wpvdb-playground-demo`](https://github.com/rbcorrales/wpvdb-playground-demo), [`wpvdb-search`](https://github.com/rbcorrales/wpvdb-search), [`wpvdb-smart-search`](https://github.com/rbcorrales/wpvdb-smart-search), [`wpvdb-blocks`](https://github.com/rbcorrales/wpvdb-blocks) | Full plugin suite demo. Loads the companion search, smart search, and blocks plugins in the same Playground site so their admin and frontend surfaces can be inspected alongside the WPVDB demo. |

The suite Blueprint verifies that the companion plugins load together. The WPVDB dashboard presets and Related Articles work without a key, while arbitrary typed Smart Search still depends on future offline search support for SQLite in Playground.

Launch links:

- [Open the main demo in WordPress Playground](https://playground.wordpress.net/?blueprint-url=https%3A%2F%2Fraw.githubusercontent.com%2Frbcorrales%2Fwpvdb-playground-demo%2Fmain%2Fplayground%2Fblueprint.json)
- [Open the suite demo in WordPress Playground](https://playground.wordpress.net/?blueprint-url=https%3A%2F%2Fraw.githubusercontent.com%2Frbcorrales%2Fwpvdb-playground-demo%2Fmain%2Fplayground%2Fblueprint-suite.json)

## Contents

`wpvdb-playground-demo.php`
Plugin bootstrap and dependency checks.

`includes/`
Demo hook registration and admin UI helpers.

`assets/js/wpvdb-demo.js`
Vanilla JavaScript for preset query buttons and results rendering.

`playground/`
Blueprint, preloader, and generated demo vectors.

## Development

Install dependencies:

```bash
composer install
```

Run the local checks:

```bash
composer lint
```

## Local intent

The plugin is inert unless both `WPVDB_PLAYGROUND_RUNTIME` and `WPVDB_DEMO_MODE` are true. The Blueprints in this repo set those constants before activating plugins, install WPVDB before this demo plugin, and then preload the sample content and vectors.
