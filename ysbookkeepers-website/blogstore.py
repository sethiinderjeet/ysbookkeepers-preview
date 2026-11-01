"""SQLite storage for blog posts and admin users (no database server needed).

The database file lives OUTSIDE the public website folder. Location:
  $YS_DATA_DIR/blog.db   (default: ../ysblog-data/blog.db next to this folder)

build.py / pages.py read published posts from here; the admin app (ysblog-admin)
reads and writes it. On first use the table is seeded from content.POSTS.
"""
import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SITE_SRC = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("YS_DATA_DIR", SITE_SRC.parent / "ysblog-data")).resolve()
DB_PATH = DATA_DIR / "blog.db"

BLOG_DIR = "resources/blog"

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY,
    username      TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS posts (
    id         INTEGER PRIMARY KEY,
    slug       TEXT NOT NULL UNIQUE,
    path       TEXT NOT NULL UNIQUE,      -- output file, e.g. resources/blog/<slug>/index.html
    title      TEXT NOT NULL,
    seo_title  TEXT,
    excerpt    TEXT NOT NULL DEFAULT '',  -- card text + meta description
    category   TEXT NOT NULL DEFAULT '',
    date       TEXT,                      -- YYYY-MM-DD shown on the post
    date_label TEXT NOT NULL DEFAULT 'Published',
    image      TEXT,                      -- site path of the featured image
    image_alt  TEXT NOT NULL DEFAULT '',
    body       TEXT NOT NULL DEFAULT '',  -- article HTML from the editor
    guide_box  INTEGER NOT NULL DEFAULT 0,
    read_time  TEXT,                      -- optional override, e.g. "5–6 min read"; blank = auto
    cta_h2     TEXT,
    cta_body   TEXT,
    status     TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'published')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS login_attempts (
    ip TEXT NOT NULL,
    ts REAL NOT NULL
);
"""


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(DATA_DIR, 0o700)
    except OSError:
        pass
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(SCHEMA)
    cols = {r[1] for r in con.execute("PRAGMA table_info(posts)")}
    if "read_time" not in cols:  # databases created before this column existed
        con.execute("ALTER TABLE posts ADD COLUMN read_time TEXT")
    try:
        os.chmod(DB_PATH, 0o600)
    except OSError:
        pass
    _seed_posts(con)
    return con


def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:80].rstrip("-") or "post"


def post_path(slug):
    return f"{BLOG_DIR}/{slug}/index.html"


def _seed_posts(con):
    if con.execute("SELECT 1 FROM posts LIMIT 1").fetchone():
        return
    from content import POSTS, IMG
    for p in POSTS:
        ts = now()
        con.execute(
            """INSERT INTO posts (slug, path, title, seo_title, excerpt, category, date, date_label, image, image_alt,
                                  body, guide_box, read_time, cta_h2, cta_body, status, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, 'published', ?, ?)""",
            (p["slug"], p["path"], p["title"], p.get("seo_title"), p["excerpt"], p["category"], p.get("date"),
             p.get("date_label", "Published"), IMG[p["image"]], p["image_alt"], p["body"].strip(),
             1 if p.get("guide_box") else 0, p.get("read"), p.get("cta_h2"), p.get("cta_body"), ts, ts))
    con.commit()


def read_minutes(html):
    words = len(re.sub(r"<[^>]+>", " ", html or "").split())
    return f"{max(1, round(words / 220))} min read"


def _as_page(row):
    """Shape a DB row the way pages.py renders a post."""
    p = dict(row)
    p["seo_title"] = p.get("seo_title") or f"{p['title']} | YS Tax & Advisory"
    p["read"] = (p.get("read_time") or "").strip() or read_minutes(p["body"])
    return p


def published_posts():
    """Newest first. Missing DB → empty list (build still works)."""
    con = connect()
    rows = con.execute(
        "SELECT * FROM posts WHERE status = 'published' ORDER BY COALESCE(date, '0000-00-00') DESC, id ASC"
    ).fetchall()
    con.close()
    return [_as_page(r) for r in rows]
