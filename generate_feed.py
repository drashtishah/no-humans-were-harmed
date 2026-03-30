#!/usr/bin/env python3
"""Generate a podcast RSS feed from podcast.yaml and episodes.yaml."""

import yaml
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def generate_feed(podcast, episodes):
    """Generate RSS XML as a string using template approach for clean output."""

    # Sort episodes by date, newest first
    episodes.sort(key=lambda e: str(e.get("date", "")), reverse=True)

    items = []
    for ep in episodes:
        pub_date = ep.get("date", "")
        if isinstance(pub_date, str):
            dt = datetime.strptime(pub_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        else:
            dt = datetime.combine(pub_date, datetime.min.time()).replace(tzinfo=timezone.utc)

        episode_num = ""
        if ep.get("episode_number"):
            episode_num = f"    <itunes:episode>{ep['episode_number']}</itunes:episode>"

        item = f"""  <item>
    <title>{escape(ep['title'])}</title>
    <description>{escape(ep.get('description', ''))}</description>
    <content:encoded><![CDATA[<p>{escape(ep.get('description', ''))}</p>]]></content:encoded>
    <pubDate>{format_datetime(dt)}</pubDate>
    <enclosure url="{escape(ep['audio_url'])}" length="{ep.get('file_size', 0)}" type="audio/x-m4a"/>
    <guid isPermaLink="false">{escape(ep['audio_url'])}</guid>
    <itunes:summary>{escape(ep.get('description', ''))}</itunes:summary>
    <itunes:duration>{ep.get('duration', '00:00:00')}</itunes:duration>
    <itunes:explicit>false</itunes:explicit>
{episode_num}
  </item>"""
        items.append(item)

    items_xml = "\n".join(items)
    feed_url = f"https://drashtishah.github.io/no-humans-were-harmed/feed.xml"

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
     xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"
     xmlns:atom="http://www.w3.org/2005/Atom"
     xmlns:content="http://purl.org/rss/1.0/modules/content/">
<channel>
  <title>{escape(podcast['title'])}</title>
  <description>{escape(podcast['description'])}</description>
  <language>{podcast.get('language', 'en')}</language>
  <link>{escape(podcast.get('website', ''))}</link>
  <atom:link href="{escape(feed_url)}" rel="self" type="application/rss+xml"/>
  <itunes:author>{escape(podcast.get('author', ''))}</itunes:author>
  <itunes:summary>{escape(podcast['description'])}</itunes:summary>
  <itunes:explicit>{str(podcast.get('explicit', False)).lower()}</itunes:explicit>
  <itunes:owner>
    <itunes:name>{escape(podcast.get('author', ''))}</itunes:name>
    <itunes:email>{escape(podcast.get('email', ''))}</itunes:email>
  </itunes:owner>
  <itunes:image href="{escape(podcast.get('cover_url', ''))}"/>
  <itunes:category text="{escape(podcast.get('category', 'Technology'))}">
    <itunes:category text="{escape(podcast.get('subcategory', ''))}"/>
  </itunes:category>
{items_xml}
</channel>
</rss>"""

    return xml


def main():
    root = Path(__file__).parent
    podcast = load_yaml(root / "podcast.yaml")
    episodes_data = load_yaml(root / "episodes.yaml")
    episodes = episodes_data.get("episodes", [])

    feed_xml = generate_feed(podcast, episodes)

    output = root / "feed.xml"
    output.write_text(feed_xml, encoding="utf-8")
    print(f"Generated {output} with {len(episodes)} episodes")


if __name__ == "__main__":
    main()
