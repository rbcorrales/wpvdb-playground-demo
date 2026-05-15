# WPVDB Playground demo

[![WordPress](https://img.shields.io/badge/WordPress-6.5%2B-3858e9?logo=wordpress&logoColor=white)](#requirements)
[![PHP](https://img.shields.io/badge/PHP-7.4%2B-777bb4?logo=php&logoColor=white)](#requirements)
[![License](https://img.shields.io/badge/License-GPLv2%2B-blue.svg)](LICENSE)

Demo packaging for running wpvdb inside WordPress Playground.

This plugin depends on wpvdb core runtime support. Core owns SQLite fallback behavior, Playground runtime guards, and the public hooks. This demo plugin owns sample content, precomputed vectors, preset query UI, and the public Blueprint.

## Requirements

| Requirement | Version or notes |
|---|---|
| WordPress | 6.5 or newer |
| PHP | 7.4 or newer |
| [`wpvdb`](https://github.com/rbcorrales/wpvdb) | Runtime support branch with SQLite and Playground hooks |
| WordPress Playground | Public Blueprint or compatible custom host |

## Contents

`wpvdb-playground-demo.php`
Plugin bootstrap and dependency checks.

`includes/`
Demo hook registration and admin UI helpers.

`assets/js/wpvdb-demo.js`
Vanilla JavaScript for preset query buttons and results rendering.

`playground/`
Blueprint, preloader, and generated demo vectors.

## Local intent

The plugin has no effect unless both `WPVDB_PLAYGROUND_RUNTIME` and `WPVDB_DEMO_MODE` are true. The public Playground Blueprint sets both constants, then installs wpvdb first and this demo plugin second.
