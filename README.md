# YS Tax & Advisory – source code

This `source` branch holds the code behind the website. The built website itself is on the `main`
branch (published to the testing site by GitHub Pages).

| Folder | What it is |
| --- | --- |
| `ysbookkeepers-website/` | Website source: content, page templates, styles, build script (`python3 build.py`) |
| `ysblog-admin/` | Private blog admin (`/admin`) and website form mailer (`/forms/send`), Flask + SQLite |
| `ysforms/` | Hosting entry point for the form mailer |

Not in this repository, by design: `ysblog-data/` (the SQLite database with blog posts and the admin
login, and the session secret key). It lives outside the web root on the server and must be backed up separately.

Setup and hosting steps: `ysblog-admin/README.md`.
