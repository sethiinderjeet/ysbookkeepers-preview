# YS Tax & Advisory – blog admin

Private admin for writing blog posts. Not linked from the website; every page sends
`noindex`. Posts and the admin login live in one SQLite file. Publishing regenerates
the static website pages, so visitors never touch Python or the database.

```
ysbookkeepers-website/   site source (build.py, pages.py, content.py, blogstore.py)
ysblog-admin/            this app (Flask)
ysblog-data/             PRIVATE: blog.db (posts + users), secret_key – never inside public_html
```

## Run locally
```bash
cd ysblog-admin
.venv/bin/python app.py create-admin yourname     # first time only
.venv/bin/python app.py serve                      # website http://127.0.0.1:8770/  admin /admin/login
```

## Admin
| URL | Page |
| --- | --- |
| `/admin/login` | Sign in (5 wrong tries → 15-minute lock) |
| `/admin/` | All posts: edit, view, delete; rebuild website; download backup |
| `/admin/posts/new` | Write a post (Jodit HTML editor, image upload, draft/publish) |
| `/admin/password` | Change password |

New posts are published at `/resources/blog/<web-address>/`.

## GoDaddy (cPanel Linux hosting) setup
1. Upload `ysbookkeepers-website/` (source) and `ysblog-admin/` to your home folder,
   **outside** `public_html`. Create an empty `ysblog-data/` next to them.
2. cPanel → **Setup Python App** → Create: Python 3.10+, Application root `ysblog-admin`,
   Application URL `ystaxadvisory.ca/admin`, startup file `passenger_wsgi.py`, entry point `application`.
3. Environment variables in that screen:
   - `YS_SITE_SRC` = `/home/<user>/ysbookkeepers-website`
   - `YS_SITE_OUT` = `/home/<user>/public_html`
   - `YS_DATA_DIR` = `/home/<user>/ysblog-data`
   - `YS_URL_PREFIX` = *(empty — Passenger already mounts the app at /admin)*
4. Run `pip install -r requirements.txt` (button in the same screen), then in cPanel Terminal:
   `python app.py create-admin <name>` and `python -c "import build; build.build_all()"` from the site folder.
5. HTTPS must be on (cPanel → SSL/TLS Status); the login cookie is sent over HTTPS only.

## Website forms (Contact Us, Refer a Business) — Python, no PHP
`forms_app.py` emails each submission to a fixed address: Contact → hello@ystaxadvisory.ca,
Referral → referral@ystaxadvisory.ca (Reply-To = the visitor). Spam trap + 10 per hour per visitor.
The incorporation-guide form is ActiveCampaign's own embed and is not handled here.

On GoDaddy, create a **second** Python app: Application root `ysforms`, Application URL
`ystaxadvisory.ca/forms`, startup file `passenger_wsgi.py`, entry point `application`, same Python version.
Environment variables: `YS_SITE_SRC`, `YS_DATA_DIR` (as above) plus mail settings:
- `YS_MAIL_FROM` = an address on the domain, e.g. `no-reply@ystaxadvisory.ca`
- `YS_SMTP_HOST` / `YS_SMTP_PORT` / `YS_SMTP_SECURITY` (`none`, `starttls` or `ssl`) / `YS_SMTP_USER` / `YS_SMTP_PASSWORD`
  (cPanel usually works with host `localhost`, port `25`; or use the mailbox's SMTP settings)
Run `pip install -r ../ysblog-admin/requirements.txt` for this app too. Locally, `app.py serve` runs the
forms at `/forms/send` and saves emails to `ysblog-data/outbox/` instead of sending them.

Backups: use **Download backup** on the posts page, or copy `ysblog-data/blog.db`.
