"""Topic bank: pick the next unused topic for a niche from topics/topic_bank.csv."""

import csv
import json
from pathlib import Path

from .config import resolve


def load_bank(cfg: dict) -> list:
    with open(resolve(cfg["topic_bank"]), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def used_topics(cfg: dict) -> set:
    used = set()
    for run_json in resolve(cfg["runs_dir"]).glob("*/run.json"):
        try:
            run = json.loads(run_json.read_text())
        except ValueError:
            continue
        if not run.get("dry_run") and run.get("topic"):
            used.add(run["topic"].strip().lower())
    return used


def niches(cfg: dict) -> list:
    return sorted({row["niche"] for row in load_bank(cfg)})


def unused(cfg: dict, niche: str, subcategory: str = "") -> list:
    used = used_topics(cfg)
    rows = [r for r in load_bank(cfg)
            if r["niche"].lower() == niche.lower()
            and (not subcategory or r["subcategory"].lower() == subcategory.lower())
            and r["title"].strip().lower() not in used]
    if not rows and niche.lower() not in {n.lower() for n in niches(cfg)}:
        raise RuntimeError(f"Unknown niche '{niche}'. Options: {', '.join(niches(cfg))}")
    return rows
