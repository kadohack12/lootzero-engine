#!/usr/bin/env python3
"""Fetch free-game deals and upsert them into Supabase."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

SOURCE_URL = os.getenv("DEALS_SOURCE_URL", "https://www.gamerpower.com/api/giveaways")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")


def get_json(url: str) -> Any:
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "LootZero/1.0"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def normalize_deal(raw: dict[str, Any]) -> dict[str, Any] | None:
    # GamerPower exposes a stable numeric giveaway id, which is our game_id.
    giveaway_id = raw.get("id") or raw.get("game_id")
    title = raw.get("title")
    url = raw.get("open_giveaway_url") or raw.get("url")
    if not giveaway_id or not title or not url:
        return None

    end_date = raw.get("end_date")
    expires_at = None
    if end_date and end_date.lower() not in {"n/a", "none"}:
        # Keep ISO timestamps for PostgreSQL timestamptz; unknown formats are omitted.
        try:
            expires_at = datetime.fromisoformat(end_date.replace("Z", "+00:00")).astimezone(timezone.utc).isoformat()
        except ValueError:
            pass

    return {
        "game_id": str(giveaway_id),
        "title": str(title),
        "store": str(raw.get("platforms") or raw.get("type") or "Unknown"),
        "original_price": str(raw.get("worth")) if raw.get("worth") else None,
        "url": str(url),
        "expires_at": expires_at,
    }


def upsert(deals: list[dict[str, Any]]) -> None:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be configured")
    if not deals:
        print("No valid deals found")
        return

    endpoint = f"{SUPABASE_URL}/rest/v1/deals?on_conflict=game_id"
    body = json.dumps(deals).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=body,
        method="POST",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=minimal",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            print(f"Upserted {len(deals)} deals (HTTP {response.status})")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Supabase returned HTTP {exc.code}: {detail}") from exc


def main() -> int:
    try:
        payload = get_json(SOURCE_URL)
        raw_deals = payload if isinstance(payload, list) else payload.get("data", [])
        deals = [deal for item in raw_deals if isinstance(item, dict) and (deal := normalize_deal(item))]
        upsert(deals)
        return 0
    except (urllib.error.URLError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"LootZero error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
