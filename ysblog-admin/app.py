"""YS Tax & Advisory - private blog admin.

Small Flask app. Users and posts live in SQLite (see ../ysbookkeepers-website/blogstore.py);
publishing regenerates the static site with build.py. The admin is not linked from the
website and every response is marked noindex.

Commands:
  python app.py create-admin <username>   create the first admin (asks for a password)
  python app.py set-password <username>   reset a password from the server
  python app.py serve [port]              local preview: website at /, admin at /admin, forms at /forms
                                          (emails are saved to ysblog-data/outbox instead of being sent)
"""
import os
import re
import secrets
import sqlite3
import sys
import time
from datetime import date, timedelta
from functools import wraps
from html import escape
from pathlib import Path

from flask import (Blueprint, Flask, abort, flash, g, jsonify, redirect, render_template, request,
                   send_file, send_from_directory, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

HERE = Path(__file__).resolve().parent
SITE_SRC = Path(os.environ.get("YS_SITE_SRC", HERE.parent / "ysbookkeepers-website")).resolve()
sys.path.insert(0, str(SITE_SRC))

import blogstore  # noqa: E402  (site source on sys.path above)
import build      # noqa: E402

URL_PREFIX = os.environ.get("YS_URL_PREFIX", "/admin").rstrip("/")
UPLOAD_SUBDIR = "assets/img/blog/uploads"
IMAGE_TYPES = {  # extension -> magic-byte check
    "jpg": lambda b: b[:3] == b"\xff\xd8\xff", "jpeg": lambda b: b[:3] == b"\xff\xd8\xff",
    "png": lambda b: b[:8] == b"\x89PNG\r\n\x1a\n", "gif": lambda b: b[:6] in (b"GIF87a", b"GIF89a"),
    "webp": lambda b: b[:4] == b"RIFF" and b[8:12] == b"WEBP",
}
MAX_FAILS, LOCK_SECONDS = 5, 15 * 60
# Max lengths - kept in step with the maxlength attributes in templates/
POST_LIMITS = {"title": 160, "excerpt": 300, "slug": 80, "category": 60, "read_time": 20, "image_alt": 200,
               "seo_title": 70, "cta_h2": 120, "cta_body": 1000, "body": 200_000}
USERNAME_MAX, PASSWORD_MAX = 50, 128
MIN_PASSWORD = 10
DEFAULT_IMAGE = "/assets/img/practitioner_consultation_wood_desk.webp"

bp = Blueprint("admin", __name__, template_folder="templates", static_folder="static", static_url_path="/static")


# ------------------------------------------------------------------ helpers
def db():
    if "db" not in g:
        g.db = blogstore.connect()
    return g.db


def secret_key():
    f = blogstore.DATA_DIR / "secret_key"
    blogstore.DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not f.exists():
        f.write_text(secrets.token_hex(32))
        os.chmod(f, 0o600)
    return f.read_text().strip()


def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(32)
    return session["csrf"]


def check_csrf():
    sent = request.form.get("csrf") or request.headers.get("X-CSRF-Token") or ""
    if not secrets.compare_digest(sent, session.get("csrf", "")):
        abort(400, "Your session expired. Please reload the page and try again.")


def login_required(view):
    @wraps(view)
    def wrapped(*a, **kw):
        if not session.get("uid"):
            return redirect(url_for("admin.login", next=request.path))
        if request.method == "POST":
            check_csrf()
        return view(*a, **kw)
    return wrapped


def current_user():
    return db().execute("SELECT * FROM users WHERE id = ?", (session.get("uid"),)).fetchone()


def clean_html(html):
    """Admins are trusted, but strip anything that runs code before it reaches the public site."""
    html = re.sub(r"(?is)<(script|style|object|embed|form|input|button|textarea|select)\b.*?(</\1\s*>|/?>)", "", html or "")
    html = re.sub(r"(?i)\son\w+\s*=\s*(\"[^\"]*\"|'[^']*'|[^\s>]+)", "", html)
    html = re.sub(r"(?i)(href|src)\s*=\s*([\"'])\s*(javascript|vbscript|data):[^\"']*\2", r'\1="#"', html)
    html = re.sub(r"(?is)<iframe\b(?![^>]*\bsrc=[\"']https://(www\.)?(youtube(-nocookie)?\.com|player\.vimeo\.com)/)[^>]*>.*?</iframe>", "", html)
    return html.strip()


def text_to_html(text):
    """CTA box text: allow simple HTML, otherwise turn paragraphs into <p>."""
    text = (text or "").strip()
    if not text:
        return None
    if re.search(r"<\w+[^>]*>", text):
        return clean_html(text)
    return "".join(f"<p>{escape(p.strip())}</p>" for p in re.split(r"\n\s*\n", text) if p.strip())


def save_image(file):
    """Validate and store an uploaded image in the public site; return its site URL."""
    name = file.filename or ""
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    head = file.stream.read(16)
    file.stream.seek(0)
    if ext not in IMAGE_TYPES or not IMAGE_TYPES[ext](head):
        raise ValueError("Please upload a JPG, PNG, WebP or GIF image.")
    stem = blogstore.slugify(name.rsplit(".", 1)[0])[:50]
    fname = f"{time.strftime('%Y%m%d-%H%M%S')}-{stem}.{'jpg' if ext == 'jpeg' else ext}"
    dest = build.OUT / UPLOAD_SUBDIR
    dest.mkdir(parents=True, exist_ok=True)
    file.save(dest / fname)
    os.chmod(dest / fname, 0o644)
    return f"/{UPLOAD_SUBDIR}/{fname}"


def rebuild():
    try:
        build.build_all()
        return True
    except Exception as exc:  # keep the admin usable; show what failed
        flash(f"Saved, but the website could not be rebuilt: {exc}", "error")
        return False


def unique_slug(slug, post_id=None):
    base, n = slug, 2
    while db().execute("SELECT 1 FROM posts WHERE slug = ? AND id IS NOT ?", (slug, post_id)).fetchone():
        slug, n = f"{base}-{n}", n + 1
    return slug


def form_data(f):
    d = f.to_dict()
    d["image"] = f.get("image_current") or None
    d["guide_box"] = 1 if f.get("guide_box") else 0
    return d


def site_url(path):
    return "/" + path.replace("index.html", "")


# ------------------------------------------------------------------ security headers
@bp.after_request
def no_index(resp):
    resp.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Referrer-Policy"] = "same-origin"
    return resp


@bp.app_context_processor
def template_globals():
    return {"csrf_token": csrf_token, "site_url": site_url, "user": session.get("username")}


@bp.teardown_app_request
def close_db(_exc):
    con = g.pop("db", None)
    if con:
        con.close()


# ------------------------------------------------------------------ auth
@bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("uid"):
        return redirect(url_for("admin.dashboard"))
    ip = request.remote_addr or "?"
    con = db()
    con.execute("DELETE FROM login_attempts WHERE ts < ?", (time.time() - LOCK_SECONDS,))
    fails = con.execute("SELECT COUNT(*) FROM login_attempts WHERE ip = ?", (ip,)).fetchone()[0]
    if request.method == "POST":
        check_csrf()
        if fails >= MAX_FAILS:
            flash("Too many attempts. Please wait 15 minutes and try again.", "error")
        else:
            name, pw = request.form.get("username", "").strip(), request.form.get("password", "")
            u = None
            if len(name) <= USERNAME_MAX and len(pw) <= PASSWORD_MAX:
                u = con.execute("SELECT * FROM users WHERE username = ?", (name,)).fetchone()
            if u and check_password_hash(u["password_hash"], request.form.get("password", "")):
                con.execute("DELETE FROM login_attempts WHERE ip = ?", (ip,))
                con.commit()
                session.clear()
                session.permanent = True
                session.update(uid=u["id"], username=u["username"], csrf=secrets.token_urlsafe(32))
                nxt = request.args.get("next", "")
                return redirect(nxt if nxt.startswith(URL_PREFIX + "/") or (not URL_PREFIX and nxt.startswith("/")) else url_for("admin.dashboard"))
            con.execute("INSERT INTO login_attempts (ip, ts) VALUES (?, ?)", (ip, time.time()))
            con.commit()
            flash("Incorrect username or password.", "error")
    con.commit()
    return render_template("login.html")


@bp.post("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("admin.login"))


@bp.route("/password", methods=["GET", "POST"])
@login_required
def password():
    if request.method == "POST":
        u = current_user()
        cur, new, confirm = (request.form.get(k, "") for k in ("current", "new", "confirm"))
        if not check_password_hash(u["password_hash"], cur):
            flash("Your current password is incorrect.", "error")
        elif len(new) > PASSWORD_MAX:
            flash(f"The new password must be at most {PASSWORD_MAX} characters.", "error")
        elif len(new) < MIN_PASSWORD:
            flash(f"The new password must be at least {MIN_PASSWORD} characters.", "error")
        elif new != confirm:
            flash("The new passwords don't match.", "error")
        else:
            db().execute("UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?",
                         (generate_password_hash(new), blogstore.now(), u["id"]))
            db().commit()
            flash("Password changed.", "ok")
            return redirect(url_for("admin.dashboard"))
    return render_template("password.html", min_len=MIN_PASSWORD)


# ------------------------------------------------------------------ posts
@bp.get("/")
@login_required
def dashboard():
    posts = db().execute(
        "SELECT * FROM posts ORDER BY CASE status WHEN 'draft' THEN 0 ELSE 1 END, COALESCE(date, '0000') DESC, id DESC").fetchall()
    return render_template("dashboard.html", posts=posts)


@bp.route("/posts/new", methods=["GET", "POST"])
@bp.route("/posts/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit_post(post_id=None):
    con = db()
    post = None
    if post_id is not None:
        post = con.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone() or abort(404)
    categories = [r[0] for r in con.execute("SELECT DISTINCT category FROM posts WHERE category != '' ORDER BY 1")]

    if request.method == "POST":
        f = request.form
        too_long = [k for k, n in POST_LIMITS.items() if len(f.get(k, "")) > n]
        if too_long:
            flash("Too long: " + ", ".join(f"{k.replace('_', ' ')} (max {POST_LIMITS[k]:,} characters)" for k in too_long), "error")
            return render_template("post_form.html", post=form_data(f), post_id=post_id, categories=categories), 400
        if f.get("date") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", f.get("date")):
            flash("Please pick a valid date.", "error")
            return render_template("post_form.html", post=form_data(f), post_id=post_id, categories=categories), 400
        title = f.get("title", "").strip()
        action = f.get("action", "draft")
        if not title:
            flash("Please add a title.", "error")
            return render_template("post_form.html", post=form_data(f), post_id=post_id, categories=categories), 400
        slug = unique_slug(blogstore.slugify(f.get("slug") or title), post_id)
        path = post["path"] if post and post["slug"] == slug else blogstore.post_path(slug)
        image = f.get("image_current") or None
        upload = request.files.get("image_file")
        if upload and upload.filename:
            try:
                image = save_image(upload)
            except ValueError as exc:
                flash(str(exc), "error")
                return render_template("post_form.html", post=form_data(f), post_id=post_id, categories=categories), 400
        status = "published" if action == "publish" else ("draft" if action in ("draft", "unpublish") else (post["status"] if post else "draft"))
        if status == "published" and not f.get("excerpt", "").strip():
            flash("Please add a short summary before publishing; it appears on the blog list and in Google.", "error")
            return render_template("post_form.html", post=form_data(f), post_id=post_id, categories=categories), 400
        values = dict(
            slug=slug, path=path, title=title, seo_title=f.get("seo_title", "").strip() or None,
            excerpt=f.get("excerpt", "").strip(), category=f.get("category", "").strip(),
            date=f.get("date") or date.today().isoformat(), date_label=f.get("date_label") or "Published",
            image=image or DEFAULT_IMAGE, image_alt=f.get("image_alt", "").strip(),
            body=clean_html(f.get("body", "")), guide_box=1 if f.get("guide_box") else 0,
            read_time=f.get("read_time", "").strip() or None,
            cta_h2=f.get("cta_h2", "").strip() or None, cta_body=text_to_html(f.get("cta_body")),
            status=status, updated_at=blogstore.now(),
        )
        if post:
            con.execute(f"UPDATE posts SET {', '.join(k + ' = ?' for k in values)} WHERE id = ?", (*values.values(), post_id))
        else:
            values["created_at"] = values["updated_at"]
            cur = con.execute(f"INSERT INTO posts ({', '.join(values)}) VALUES ({', '.join('?' * len(values))})", tuple(values.values()))
            post_id = cur.lastrowid
        con.commit()
        was_live = bool(post and post["status"] == "published")
        if status == "published" or was_live:
            if rebuild():
                flash("Published. The post is live." if status == "published" else "Unpublished and removed from the website.", "ok")
        else:
            flash("Draft saved. It isn't on the website until you publish it.", "ok")
        return redirect(url_for("admin.edit_post", post_id=post_id))

    return render_template("post_form.html", post=dict(post) if post else None, post_id=post_id,
                           categories=categories, today=date.today().isoformat())


@bp.post("/posts/<int:post_id>/delete")
@login_required
def delete_post(post_id):
    post = db().execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone() or abort(404)
    db().execute("DELETE FROM posts WHERE id = ?", (post_id,))
    db().commit()
    if post["status"] == "published":
        rebuild()
    flash(f"Deleted \"{post['title']}\".", "ok")
    return redirect(url_for("admin.dashboard"))


@bp.post("/upload")
@login_required
def upload():
    """Image upload used by the editor (Jodit's expected response format)."""
    files = list(request.files.values())
    try:
        if not files:
            raise ValueError("No file received.")
        urls = [save_image(fl) for fl in files]
        return jsonify(success=True, time=blogstore.now(),
                       data=dict(baseurl="", messages=[], files=urls, isImages=[True] * len(urls), code=220))
    except ValueError as exc:
        return jsonify(success=False, time=blogstore.now(), data=dict(messages=[str(exc)], files=[], code=400)), 400


@bp.post("/rebuild")
@login_required
def rebuild_site():
    if rebuild():
        flash("Website rebuilt.", "ok")
    return redirect(url_for("admin.dashboard"))


@bp.get("/backup")
@login_required
def backup():
    out = blogstore.DATA_DIR / "backup-download.db"
    src = sqlite3.connect(blogstore.DB_PATH)
    dst = sqlite3.connect(out)
    src.backup(dst)
    dst.execute("DELETE FROM login_attempts")
    dst.commit()
    dst.close()
    src.close()
    return send_file(out, as_attachment=True, download_name=f"ys-blog-backup-{date.today().isoformat()}.db")


# ------------------------------------------------------------------ app factory
def create_app(serve_site=False):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=secret_key(),
        SESSION_COOKIE_NAME="ys_admin",
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("YS_COOKIE_SECURE", "1") == "1",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
        MAX_CONTENT_LENGTH=10 * 1024 * 1024,
    )
    app.register_blueprint(bp, url_prefix=URL_PREFIX or None)

    @app.errorhandler(413)
    def too_big(_e):
        return "Image is larger than 10 MB. Please resize it and try again.", 413

    if serve_site:  # local preview only; in production the web server serves the static site
        import forms_app  # website forms at /forms/send (a separate cPanel app in production)
        os.environ.setdefault("YS_MAIL_OUTBOX", str(blogstore.DATA_DIR / "outbox"))
        app.register_blueprint(forms_app.bp, url_prefix="/forms")

        @app.get("/")
        @app.get("/<path:path>")
        def site(path="index.html"):
            full = build.OUT / path
            if full.is_dir():
                path = path.rstrip("/") + "/index.html"
            return send_from_directory(build.OUT, path)
    return app


def _cli():
    import getpass
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd in ("create-admin", "set-password") and len(sys.argv) == 3:
        username = sys.argv[2]
        pw = getpass.getpass("New password: ")
        if len(pw) < MIN_PASSWORD or pw != getpass.getpass("Repeat password: "):
            sys.exit(f"Passwords must match and be at least {MIN_PASSWORD} characters.")
        con = blogstore.connect()
        h, ts = generate_password_hash(pw), blogstore.now()
        if cmd == "create-admin":
            con.execute("INSERT INTO users (username, password_hash, created_at, updated_at) VALUES (?,?,?,?)", (username, h, ts, ts))
        elif not con.execute("UPDATE users SET password_hash = ?, updated_at = ? WHERE username = ?", (h, ts, username)).rowcount:
            sys.exit(f"No user called {username}.")
        con.commit()
        print(f"Done. {username} can now sign in at {URL_PREFIX or '/'}/login")
    elif cmd == "serve":
        os.environ.setdefault("YS_COOKIE_SECURE", "0")
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8770
        create_app(serve_site=True).run(host="127.0.0.1", port=port, debug=False)
    else:
        print(__doc__)


if __name__ == "__main__":
    _cli()
