#!/usr/bin/env python3
"""
Generate real text-embedding-3-small vectors for the Playground demo, plus an
inline quality eval that ranks each preset query against the full post corpus
so we can sanity-check semantic clustering before committing.

Writes playground/demo-vectors.json with 768-dim embeddings
for the 20 demo posts and 4 preset queries. The Playground preloader reads
this file at Blueprint boot and falls back to deterministic placeholder
vectors if the file is missing or malformed.

IMPORTANT: the DEMO_POSTS and DEMO_PRESETS lists below must mirror the
`$sample_posts` and `$preset_queries` arrays in
playground/preload-demo.php exactly (matching seed values,
content, ids). The seed integer is the JSON key in the output; the PHP
preloader looks up the vector by that key. If you change one, change the
other.

Usage:
    tools/generate-playground-demo-vectors.py

Requirements:
    - $OPENAI_A8C_API_KEY in env (Automattic AI proxy via OpenAI passthrough)
    - AutoProxxy running on localhost (default port 8080), since the proxy is
      IP-allowlisted to the Automattic-internal gateway. See AGENTS.md
      "Atomic API access via curl" for the rationale.

Cost: ~$0.0005 (24 embeddings against text-embedding-3-small at $0.02/1M
tokens, ~75 tokens average each).
"""

from __future__ import annotations

import json
import math
import os
import socket
import subprocess
import sys
from pathlib import Path

# Each post is keyed by an integer `seed` that matches preload-demo.php's
# $sample_posts array. The `topic` field is metadata for the quality eval
# below; it isn't shipped in the JSON.
DEMO_POSTS = [
    # --- Cooking (5) ---
    {
        "seed": 1,
        "topic": "cooking",
        "title": "Pasta carbonara",
        "content": (
            "Whisk eggs with grated pecorino and black pepper. Crisp "
            "guanciale in a hot pan until rendered, then toss hot pasta in "
            "the fat. Remove from heat and stir in the egg mixture with a "
            "splash of pasta water; the residual heat sets a silky sauce "
            "without scrambling."
        ),
    },
    {
        "seed": 2,
        "topic": "cooking",
        "title": "Slow-cooked beef stew for cold evenings",
        "content": (
            "Brown the beef in batches so it sears rather than steams. Build "
            "a stock with onion, carrot, garlic, red wine, bay, and thyme. "
            "Simmer covered for three hours until the connective tissue "
            "gives way and the meat falls apart at the touch of a fork."
        ),
    },
    {
        "seed": 3,
        "topic": "cooking",
        "title": "Sourdough basics",
        "content": (
            "Feed a starter for at least a week before baking. Mix flour and "
            "water, autolyse for an hour, then fold every thirty minutes "
            "through the bulk ferment. Shape the dough, proof cold overnight, "
            "score the top, and bake in a covered Dutch oven."
        ),
    },
    {
        "seed": 4,
        "topic": "cooking",
        "title": "Vegetable curry",
        "content": (
            "Bloom whole cumin, coriander, and mustard seeds in ghee until "
            "they pop. Add onion, garlic, ginger, and a tin of tomato. "
            "Simmer cauliflower, potato, and chickpeas in coconut milk until "
            "tender. Finish with cilantro, lime, and a pinch of salt."
        ),
    },
    {
        "seed": 5,
        "topic": "cooking",
        "title": "Knife skills primer",
        "content": (
            "A sharp knife is safer than a dull one because it stays where "
            "you put it. Curl your fingertips back into a claw and anchor "
            "the blade against your knuckles. Practice the rock chop on a "
            "bunch of parsley before tackling onions or shallots."
        ),
    },

    # --- Travel (5) ---
    {
        "seed": 6,
        "topic": "travel",
        "title": "Lisbon alleys",
        "content": (
            "The cobblestone alleys of Alfama widen into a square where "
            "vendors sell bread and azulejos. Pigeons scatter as a yellow "
            "tram clatters past. Climb to Castelo de Sao Jorge for a view "
            "across the Tagus to the Cristo Rei statue on the far bank."
        ),
    },
    {
        "seed": 7,
        "topic": "travel",
        "title": "Tokyo morning markets",
        "content": (
            "Tsukiji outer market wakes at five. Stall holders slice maguro "
            "under fluorescent light while regulars line up for tamagoyaki "
            "on a stick and freshly grilled scallops in their shells. Walk "
            "through before the tour buses arrive and the prices double."
        ),
    },
    {
        "seed": 8,
        "topic": "travel",
        "title": "Marrakech souks",
        "content": (
            "Beyond Jemaa el-Fnaa the souks fold into themselves: brass "
            "lanterns, leather slippers, mountains of saffron and ras el "
            "hanout. Tea is poured from a meter above the glass to froth "
            "the surface; refuse the cup and you have already accepted the "
            "next round of bargaining."
        ),
    },
    {
        "seed": 9,
        "topic": "travel",
        "title": "Edinburgh closes",
        "content": (
            "The Royal Mile drops away into narrow closes that lead to "
            "hidden courtyards. Each has a story: plague pits walled up at "
            "Mary King's Close, the ghost of Greyfriars Bobby, smugglers, "
            "poets, the doctor whose dissections inspired Jekyll and Hyde."
        ),
    },
    {
        "seed": 10,
        "topic": "travel",
        "title": "A dusk walk through Panama City's Casco Viejo",
        "content": (
            "Casco Viejo's colonial balconies look across the bay to a "
            "skyline of glass towers. Walk the seawall at dusk while the "
            "city lights come up, then duck into a salsa club where locals "
            "dance until the bands stop and the streets cool down enough "
            "to walk back."
        ),
    },

    # --- WordPress / web dev (5) ---
    {
        "seed": 11,
        "topic": "wordpress",
        "title": "Vector search with wpvdb",
        "content": (
            "WordPress sites can do semantic search by storing embeddings "
            "alongside posts. The wpvdb plugin handles chunking long "
            "content, generating embeddings through OpenAI or a custom "
            "provider, and querying similarity against a custom MariaDB "
            "table using native VECTOR functions."
        ),
    },
    {
        "seed": 12,
        "topic": "wordpress",
        "title": "Headless WordPress",
        "content": (
            "Decouple the front end by treating WordPress as a content API. "
            "React, Next.js, or Astro can render pages from the REST API or "
            "a GraphQL gateway while the WP admin stays familiar to editors. "
            "Authentication still flows through application passwords or JWT."
        ),
    },
    {
        "seed": 13,
        "topic": "wordpress",
        "title": "Block themes",
        "content": (
            "Theme.json declares the design system: typography scales, "
            "color palettes, layout widths, spacing tokens. Block templates "
            "replace PHP template hierarchy files, so editors can rearrange "
            "the front end visually without touching code or losing the "
            "existing performance budget."
        ),
    },
    {
        "seed": 14,
        "topic": "wordpress",
        "title": "REST API endpoints",
        "content": (
            "Custom endpoints register through register_rest_route with a "
            "namespace, route, methods, callback, and permission_callback. "
            "Authentication uses cookies for browsers, application "
            "passwords for scripts and CLI, and OAuth for third-party "
            "integrations like Zapier or Make."
        ),
    },
    {
        "seed": 15,
        "topic": "wordpress",
        "title": "Performance budgets",
        "content": (
            "Set a Lighthouse target for every page template and fail CI "
            "when it regresses. Lazy-load images, defer non-critical "
            "JavaScript, use Server Timing headers to spot slow database "
            "queries before they ship, and pin a budget per route in the "
            "pull request template."
        ),
    },

    # --- Outdoors (5) ---
    {
        "seed": 16,
        "topic": "outdoors",
        "title": "Sierra hiking",
        "content": (
            "The granite spine of the Sierra rises above tree line by "
            "mid-July. Carry layers; afternoon thunderstorms build over "
            "the high passes around two even in the dry months. The trail "
            "from Tuolumne Meadows to Mount Conness is a classic "
            "introduction to high alpine terrain."
        ),
    },
    {
        "seed": 17,
        "topic": "outdoors",
        "title": "Native pollinators",
        "content": (
            "Bumblebees pollinate plants honeybees cannot reach because "
            "they vibrate flowers loose. Mason bees emerge in early spring, "
            "weeks before honeybees are even active. Plant native "
            "wildflowers in clumps across a full season of bloom to "
            "support both species."
        ),
    },
    {
        "seed": 18,
        "topic": "outdoors",
        "title": "Coastal birding",
        "content": (
            "Migrating shorebirds stage on mudflats in spring and fall. "
            "Bring a spotting scope; semipalmated plovers and least "
            "sandpipers look identical at a hundred meters without one. "
            "Best light is the first two hours after sunrise, before the "
            "tide pushes the birds inland."
        ),
    },
    {
        "seed": 19,
        "topic": "outdoors",
        "title": "Winter trail prep",
        "content": (
            "Microspikes handle packed snow and rolling terrain. Crampons "
            "and an ice axe are the line you cross into mountaineering, "
            "and they need practice on a low-consequence slope first. "
            "Always carry a beacon, shovel, and probe when traveling in "
            "avalanche country."
        ),
    },
    {
        "seed": 20,
        "topic": "outdoors",
        "title": "Mushroom foraging",
        "content": (
            "Chanterelles fruit after summer rain in oak and conifer "
            "forests across the Pacific Northwest. Look for the golden "
            "vase shape with false gills and a peppery, fruity scent. When "
            "in doubt, photograph and ask a local mycologist; toxic "
            "species can look identical to a beginner."
        ),
    },
]

# Presets are keyed by `id` (slug) in the output JSON. The `text` is what we
# embed for the preset's stored vector. `expected_topic` lets the eval below
# assert that the top-5 ranked posts belong to the matching topic.
DEMO_PRESETS = [
    {"id": "cooking",   "label": "Easy dinner recipes",        "text": "easy dinner recipes I can cook tonight",         "expected_topic": "cooking"},
    {"id": "travel",    "label": "Interesting cities to walk", "text": "interesting cities and places to walk and explore", "expected_topic": "travel"},
    {"id": "wordpress", "label": "WordPress and search",       "text": "WordPress plugins and semantic search",          "expected_topic": "wordpress"},
    {"id": "outdoors",  "label": "Hiking and the outdoors",    "text": "hiking and outdoor activities",                   "expected_topic": "outdoors"},
]

MODEL = "text-embedding-3-small"
DIMENSIONS = 768
PROXY_ENDPOINT = "https://public-api.wordpress.com/wpcom/v2/ai-api-proxy/v1/embeddings"
PROXY_PORT = 8080
OUTPUT = Path(__file__).resolve().parent.parent / "playground" / "demo-vectors.json"


def require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        sys.exit(
            f"error: {name} is not set. The Automattic AI proxy requires this "
            "token; export it before running this script."
        )
    return value


def require_autoproxxy(port: int) -> None:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.0)
    try:
        s.connect(("127.0.0.1", port))
    except OSError as e:
        sys.exit(
            f"error: AutoProxxy is not reachable on 127.0.0.1:{port} ({e}). "
            "Start it before running this script (proxy is mandatory for the "
            "Automattic-internal AI gateway)."
        )
    finally:
        s.close()


def embed(text: str, token: str) -> list[float]:
    body = json.dumps({"model": MODEL, "input": text, "dimensions": DIMENSIONS})
    result = subprocess.run(
        [
            "curl",
            "-sS",
            "--proxy", f"socks5h://127.0.0.1:{PROXY_PORT}",
            "--request", "POST",
            "--header", f"Authorization: Bearer {token}",
            "--header", "Content-Type: application/json",
            "--header", "X-WPCOM-AI-Feature: wpcloud-vector-search",
            "--max-time", "30",
            "--data-binary", body,
            PROXY_ENDPOINT,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        sys.exit(f"error: curl failed ({result.returncode}): {result.stderr.strip()}")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        sys.exit(f"error: proxy returned non-JSON: {e}\nbody: {result.stdout[:500]}")
    if "data" not in payload or not payload["data"]:
        sys.exit(f"error: unexpected proxy response: {payload}")
    vector = payload["data"][0].get("embedding")
    if not isinstance(vector, list) or len(vector) != DIMENSIONS:
        sys.exit(
            f"error: embedding has wrong shape "
            f"(got len={len(vector) if isinstance(vector, list) else type(vector).__name__}, "
            f"expected {DIMENSIONS})"
        )
    return vector


def cosine_distance(a: list[float], b: list[float]) -> float:
    # OpenAI text-embedding-3-small returns L2-normalized unit vectors, so
    # cosine distance reduces to 1 - dot(a, b). We still compute norms
    # defensively in case truncation via the `dimensions` param breaks
    # normalization at any point.
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na <= 0 or nb <= 0:
        return 1.0
    return 1.0 - dot / (na * nb)


def run_quality_eval(posts_with_topic, presets_with_topic) -> None:
    """Print a ranking table for each preset and flag obvious failures."""

    print("\n=== Quality eval ===", file=sys.stderr)
    print(
        "For each preset query, top results should belong to the matching "
        "topic. Topic-boundary gap is the distance from the worst same-topic "
        "match to the best other-topic match; bigger is better.\n",
        file=sys.stderr,
    )

    failures = []
    for preset in presets_with_topic:
        ranked = sorted(
            posts_with_topic,
            key=lambda p: cosine_distance(preset["vector"], p["vector"]),
        )
        same_topic = [p for p in ranked if p["topic"] == preset["expected_topic"]]
        other_topic = [p for p in ranked if p["topic"] != preset["expected_topic"]]

        print(f"Preset {preset['id']!r}  ('{preset['label']}')", file=sys.stderr)
        for rank, p in enumerate(ranked[:8], start=1):
            d = cosine_distance(preset["vector"], p["vector"])
            marker = "*" if p["topic"] == preset["expected_topic"] else " "
            print(f"  {rank:2d}.{marker} d={d:.4f}  [{p['topic']:9s}] {p['title']}", file=sys.stderr)

        # Top-N analysis: how many of top-N are same-topic?
        topn = min(5, len(same_topic))
        topn_same = sum(1 for p in ranked[:topn] if p["topic"] == preset["expected_topic"])
        max_same_d = cosine_distance(preset["vector"], same_topic[-1]["vector"]) if same_topic else None
        min_other_d = cosine_distance(preset["vector"], other_topic[0]["vector"]) if other_topic else None
        gap = (min_other_d - max_same_d) if (max_same_d is not None and min_other_d is not None) else None
        gap_str = f"{gap:+.4f}" if gap is not None else "n/a"

        print(
            f"     top-{topn} same-topic hits: {topn_same}/{topn}   "
            f"topic-boundary gap: {gap_str}",
            file=sys.stderr,
        )
        print("", file=sys.stderr)

        if topn_same < topn:
            failures.append(
                f"{preset['id']}: only {topn_same}/{topn} of top {topn} are "
                f"{preset['expected_topic']} posts"
            )
        if gap is not None and gap < 0:
            failures.append(
                f"{preset['id']}: top non-{preset['expected_topic']} ranked above "
                f"worst {preset['expected_topic']} (negative gap)"
            )

    if failures:
        print("Quality concerns:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        print(
            "\nReview the rankings above. Decide whether to adjust content / "
            "preset text before committing.",
            file=sys.stderr,
        )
    else:
        print("All presets pass top-5 same-topic check with positive boundary gap.", file=sys.stderr)


def main() -> int:
    token = require_env("OPENAI_A8C_API_KEY")
    require_autoproxxy(PROXY_PORT)

    posts_with_vectors = []
    for post in DEMO_POSTS:
        print(f"  embedding post seed={post['seed']:2d}: {post['title']!r}", file=sys.stderr)
        vec = embed(post["content"], token)
        posts_with_vectors.append({
            "seed":   post["seed"],
            "topic":  post["topic"],
            "title":  post["title"],
            "vector": vec,
        })

    presets_with_vectors = []
    for preset in DEMO_PRESETS:
        print(f"  embedding preset id={preset['id']!r}: {preset['text']!r}", file=sys.stderr)
        vec = embed(preset["text"], token)
        presets_with_vectors.append({
            "id":             preset["id"],
            "label":          preset["label"],
            "expected_topic": preset["expected_topic"],
            "vector":         vec,
        })

    run_quality_eval(posts_with_vectors, presets_with_vectors)

    # JSON output: posts keyed by seed integer (string for JSON), presets
    # keyed by id slug. Topic and title metadata are dropped from the shipped
    # file; preload-demo.php's $sample_posts is the source of truth for that.
    output = {
        "model": MODEL,
        "dimensions": DIMENSIONS,
        "generated_by": "tools/generate-playground-demo-vectors.py",
        "posts":   { str(p["seed"]): p["vector"] for p in posts_with_vectors },
        "presets": { p["id"]: p["vector"] for p in presets_with_vectors },
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, separators=(",", ":")) + "\n")
    print(f"\nwrote {OUTPUT}  ({OUTPUT.stat().st_size:,} bytes)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
