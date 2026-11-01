"""Website form mailer (Contact Us + Refer a Business) - Python, no PHP, no extra database.

POST /forms/send  ->  emails the submission to a fixed address per form.
Recipients live here, so a visitor can't make the site send mail anywhere else.

Mail settings (environment variables):
  YS_SMTP_HOST      default "localhost" (cPanel hosts relay local mail)
  YS_SMTP_PORT      default 25   (587 with STARTTLS, 465 with SSL)
  YS_SMTP_SECURITY  "none" | "starttls" | "ssl"   (default "none")
  YS_SMTP_USER / YS_SMTP_PASSWORD   optional login, e.g. a mailbox on the domain
  YS_MAIL_FROM      default no-reply@ystaxadvisory.ca  (must be on the website's domain)
  YS_MAIL_OUTBOX    a folder: save emails there as .eml instead of sending (local testing)
"""
import os
import re
import smtplib
import ssl
import sys
import time
from datetime import datetime
from email.message import EmailMessage
from email.utils import formataddr, make_msgid
from pathlib import Path
from urllib.parse import urlparse

from flask import Blueprint, Flask, jsonify, redirect, request

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(Path(os.environ.get("YS_SITE_SRC", HERE.parent / "ysbookkeepers-website")).resolve()))
import blogstore  # noqa: E402  (shared SQLite file, used only for the rate limit)
from content import FORM_LIMITS  # noqa: E402  (same max lengths as the website fields)

FORMS = {
    "contact": {
        "to": "hello@ystaxadvisory.ca",
        "subject": "Website enquiry",
        "fields": {"first_name": "First name", "last_name": "Last name", "email": "Email", "phone": "Phone",
                   "profession": "Profession / industry", "service": "Needs help with", "message": "Message"},
        "required": ["first_name", "last_name", "email", "phone", "profession", "consent"],
        "reply_to": "email",
        "who": lambda d: f"{d['first_name']} {d['last_name']}".strip(),
    },
    "referral": {
        "to": "referral@ystaxadvisory.ca",
        "subject": "New referral",
        "fields": {"your_name": "Referred by", "your_email": "Referrer email",
                   "referral_name": "Referral name", "referral_email": "Referral email"},
        "required": ["your_name", "your_email", "referral_name", "referral_email"],
        "reply_to": "your_email",
        "who": lambda d: d["your_name"],
    },
}
MAX_PER_HOUR = 10  # per visitor IP
FAIL_MSG = "Sorry, your message could not be sent. Please email us at hello@ystaxadvisory.ca or call 778-503-8310."
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+'-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$")
PHONE_CHARS = re.compile(r"^[0-9\s().+-]+$")


def valid_email(v):
    return bool(EMAIL_RE.match(v)) and ".." not in v


def phone_digits(v):
    """North American 10-digit number (optional leading 1), else None."""
    if not PHONE_CHARS.match(v):
        return None
    d = re.sub(r"\D", "", v)
    if len(d) == 11 and d[0] == "1":
        d = d[1:]
    return d if re.fullmatch(r"[2-9]\d{2}[2-9]\d{6}", d) else None

bp = Blueprint("forms", __name__)


def _clean(value, limit):
    value = (value or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    value = "".join(ch for ch in value if ch in "\n\t" or ch.isprintable())
    return value[:limit]


def _respond(ok, error="", code=200):
    if "application/json" in request.headers.get("Accept", ""):
        body = {"ok": True} if ok else {"ok": False, "error": error}
        return jsonify(body), code
    # No-JavaScript fallback: back to the page the form was on
    back = urlparse(request.referrer or "").path or "/contact.html"
    return redirect(f"{back}?{'sent' if ok else 'error'}=1", 303)


def _rate_limited(ip):
    con = blogstore.connect()
    con.execute("CREATE TABLE IF NOT EXISTS form_hits (ip TEXT NOT NULL, ts REAL NOT NULL)")
    con.execute("DELETE FROM form_hits WHERE ts < ?", (time.time() - 3600,))
    n = con.execute("SELECT COUNT(*) FROM form_hits WHERE ip = ?", (ip,)).fetchone()[0]
    con.commit()
    con.close()
    return n >= MAX_PER_HOUR


def _record_hit(ip):
    con = blogstore.connect()
    con.execute("INSERT INTO form_hits (ip, ts) VALUES (?, ?)", (ip, time.time()))
    con.commit()
    con.close()


def send_email(msg):
    outbox = os.environ.get("YS_MAIL_OUTBOX")
    if outbox:  # local testing: write the email to a file instead of sending it
        Path(outbox).mkdir(parents=True, exist_ok=True)
        (Path(outbox) / f"{time.strftime('%Y%m%d-%H%M%S')}-{time.time_ns() % 10**6}.eml").write_bytes(bytes(msg))
        return
    host = os.environ.get("YS_SMTP_HOST", "localhost")
    port = int(os.environ.get("YS_SMTP_PORT", "25"))
    security = os.environ.get("YS_SMTP_SECURITY", "none").lower()
    user, password = os.environ.get("YS_SMTP_USER"), os.environ.get("YS_SMTP_PASSWORD")
    if security == "ssl":
        server = smtplib.SMTP_SSL(host, port, timeout=20, context=ssl.create_default_context())
    else:
        server = smtplib.SMTP(host, port, timeout=20)
        if security == "starttls":
            server.starttls(context=ssl.create_default_context())
    with server:
        if user:
            server.login(user, password or "")
        server.send_message(msg)


@bp.post("/send")
def send():
    cfg = FORMS.get(request.form.get("form", ""))
    if not cfg:
        return _respond(False, "Unknown form.", 400)
    if request.form.get("website"):  # spam trap: hidden field people never fill in
        return _respond(True)
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "?").split(",")[0].strip()
    if _rate_limited(ip):
        return _respond(False, "Too many messages from your connection. Please email us instead.", 429)

    for k, label in cfg["fields"].items():
        limit = FORM_LIMITS.get(k, 200)
        if len((request.form.get(k) or "").strip()) > limit:
            return _respond(False, f"{label} is too long (maximum {limit} characters).", 422)
    data = {k: _clean(request.form.get(k), FORM_LIMITS.get(k, 200)) for k in cfg["fields"]}
    data["consent"] = request.form.get("consent", "")
    if any(not data.get(k) for k in cfg["required"]):
        return _respond(False, "Please fill in all required fields.", 422)
    if any("email" in k and v and not valid_email(v) for k, v in data.items()):
        return _respond(False, "Please enter a valid email address, e.g. name@example.com.", 422)
    if "phone" in data:
        digits = phone_digits(data["phone"])
        if not digits:
            return _respond(False, "Please enter a valid 10-digit phone number, e.g. 604-555-1234.", 422)
        data["phone"] = f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"

    width = max(len(label) for label in cfg["fields"].values()) + 2
    lines = [f"{(label + ':').ljust(width)} {data[k] or '-'}" for k, label in cfg["fields"].items()]
    sent_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    body = "\n".join(lines) + f"\n\nSent from {request.host} on {sent_at}\n"

    mail_from = os.environ.get("YS_MAIL_FROM", "no-reply@ystaxadvisory.ca")
    msg = EmailMessage()
    msg["Subject"] = f"{cfg['subject']}: {cfg['who'](data)}"
    msg["From"] = formataddr(("YS Tax & Advisory website", mail_from))
    msg["To"] = cfg["to"]
    msg["Reply-To"] = data[cfg["reply_to"]]
    msg["Message-ID"] = make_msgid(domain=mail_from.split("@")[-1])
    msg.set_content(body)
    try:
        send_email(msg)
    except Exception as exc:  # log for the host's error log, show a friendly message
        print(f"[forms] send failed: {exc!r}", file=sys.stderr)
        return _respond(False, FAIL_MSG, 500)
    _record_hit(ip)
    return _respond(True)


def create_app():
    """Standalone app for cPanel: mounted at /forms, so routes have no prefix."""
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 64 * 1024
    app.register_blueprint(bp, url_prefix=os.environ.get("YS_FORMS_PREFIX", "") or None)
    return app
