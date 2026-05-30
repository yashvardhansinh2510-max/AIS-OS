#!/usr/bin/env python3
"""
Research Agent — Data Fetcher
Pulls YouTube RSS feeds for 10 monitored creators and outputs JSON for Claude analysis.
Run daily at 6 AM IST. No API keys required.
"""

import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

CHANNELS = [
    {"creator": "Alex Hormozi",      "id": "UCGBgB7VC1ZzIjUbf1jrQflQ", "tier": 1},
    {"creator": "Dan Koe",           "id": "UCWXYDYv5STLk-zoxMP2I1Lw", "tier": 1},
    {"creator": "Codie Sanchez",     "id": "UCJZ8lEnZmzQ5qOqF9joxIxQ", "tier": 1},
    {"creator": "My First Million",  "id": "UCyaN6mg5u8Cjy2ZI4ikWaug", "tier": 3},
    {"creator": "Chris Williamson",  "id": "UCIaH-gZIVC432YRjNVvnyCA", "tier": 2},
    {"creator": "Justin Welsh",      "id": "UCoAnsP_Mm8YDjwSo_MigD8Q", "tier": 1},
]

RSS_BASE = "https://www.youtube.com/feeds/videos.xml?channel_id="
NS = {"atom": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015", "media": "http://search.yahoo.com/mrss/"}

# Fetch videos published in last N days
LOOKBACK_DAYS = 7


def fetch_channel(channel):
    url = RSS_BASE + channel["id"]
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read()
    except Exception as e:
        print(f"[WARN] Failed to fetch {channel['creator']}: {e}", file=sys.stderr)
        return []

    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        print(f"[WARN] Failed to parse XML for {channel['creator']}: {e}", file=sys.stderr)
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)
    videos = []

    for entry in root.findall("atom:entry", NS):
        published_el = entry.find("atom:published", NS)
        if published_el is None:
            continue
        try:
            published = datetime.fromisoformat(published_el.text.replace("Z", "+00:00"))
        except ValueError:
            continue
        if published < cutoff:
            continue

        title_el = entry.find("atom:title", NS)
        link_el = entry.find("atom:link", NS)
        desc_el = entry.find("media:group/media:description", NS)

        title = title_el.text.strip() if title_el is not None else ""
        url_val = link_el.get("href", "") if link_el is not None else ""
        description = (desc_el.text or "").strip()[:500] if desc_el is not None else ""

        if not title:
            continue

        videos.append({
            "creator": channel["creator"],
            "tier": channel["tier"],
            "title": title,
            "description": description,
            "url": url_val,
            "published": published_el.text,
        })

    return videos


def main():
    all_videos = []
    for channel in CHANNELS:
        videos = fetch_channel(channel)
        all_videos.extend(videos)
        print(f"[INFO] {channel['creator']}: {len(videos)} videos in last {LOOKBACK_DAYS} days", file=sys.stderr)

    all_videos.sort(key=lambda v: v["published"], reverse=True)

    output = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "lookback_days": LOOKBACK_DAYS,
        "total_videos": len(all_videos),
        "videos": all_videos,
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
