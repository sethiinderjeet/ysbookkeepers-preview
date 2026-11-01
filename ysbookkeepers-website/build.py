#!/usr/bin/env python3
"""Static site generator for the YS Tax & Advisory website.

Every page shares one header (with the Who We Serve mega-menu and the Services /
Resources dropdowns) and one footer, so they are defined once here and each page
only supplies its <main> content. Run:  python3 build.py
Output is written next to this file (index.html, services/…, who-we-serve/…).
"""
import os
from pathlib import Path
from html import escape

from content import (SITE, NAV_SERVE_HEALTH, NAV_SERVE_OTHER, SERVICES, RESOURCES,
                     CTA_LABEL, CTA_CHECKS, HOW_WE_WORK, IMG, CONTACT_CARDS)

ROOT = Path(__file__).parent
# Where pages are written. Locally this folder; in production set YS_SITE_OUT to public_html.
OUT = Path(os.environ.get("YS_SITE_OUT", ROOT)).resolve()

# ---------------------------------------------------------------- icons (lucide)
ICONS = {
    "check": '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
    "arrow": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "chev": '<path d="m6 9 6 6 6-6"/>',
    "menu": '<path d="M4 6h16M4 12h16M4 18h16"/>',
    "x": '<path d="M18 6 6 18M6 6l12 12"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "heart": '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/><path d="M3.22 12H9.5l.5-1 2 4.5 2-7 1.5 3.5h5.27"/>',
    "hand": '<path d="M18 11V6a2 2 0 0 0-4 0v5"/><path d="M14 10V4a2 2 0 0 0-4 0v2"/><path d="M10 10.5V6a2 2 0 0 0-4 0v8"/><path d="M18 8a2 2 0 1 1 4 0v6a8 8 0 0 1-8 8h-2c-2.8 0-4.5-.86-5.99-2.34l-3.6-3.6a2 2 0 0 1 2.83-2.82L7 15"/>',
    "activity": '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    "message": '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>',
    "leaf": '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>',
    "building": '<rect x="4" y="2" width="16" height="20" rx="2"/><path d="M9 22v-4h6v4M8 6h.01M16 6h.01M12 6h.01M12 10h.01M12 14h.01M16 10h.01M16 14h.01M8 10h.01M8 14h.01"/>',
    "stethoscope": '<path d="M11 2v2M5 2v2M5 3H4a2 2 0 0 0-2 2v4a6 6 0 0 0 12 0V5a2 2 0 0 0-2-2h-1"/><path d="M8 15a6 6 0 0 0 12 0v-3"/><circle cx="20" cy="10" r="2"/>',
    "hammer": '<path d="m15 12-8.37 8.37a1 1 0 1 1-3-3L12 9"/><path d="m18 15 4-4"/><path d="m21.5 11.5-1.91-1.91A2 2 0 0 1 19 8.17V7l-2.26-1.13a6 6 0 0 0-2.38-.63H13l.92.82A6.18 6.18 0 0 1 16 10.46V12l2 2h1.17a2 2 0 0 1 1.42.59L22 16"/>',
    "utensils": '<path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2M7 2v20M21 15V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"/>',
    "home": '<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/>',
    "rocket": '<path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/>',
    "briefcase": '<rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
    "file": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4M10 9H8M16 13H8M16 17H8"/>',
    "landmark": '<path d="M3 22h18M6 18v-7M10 18v-7M14 18v-7M18 18v-7M12 2l8 5H4Z"/>',
    "user": '<circle cx="12" cy="8" r="5"/><path d="M20 21a8 8 0 0 0-16 0"/>',
    "book": '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2zM22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
    "history": '<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5M12 7v5l4 2"/>',
    "wallet": '<path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/>',
    "trend": '<path d="M22 7 13.5 15.5 8.5 10.5 2 17"/><path d="M16 7h6v6"/>',
    "present": '<path d="M2 3h20M21 3v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V3M7 21l5-5 5 5"/>',
    "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/><path d="m9 12 2 2 4-4"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "quote": '<path d="M3 21c3 0 7-1 7-8V5c0-1.25-.76-2-2-2H4c-1.25 0-2 .75-2 1.97V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 0-1 1.03V20c0 1 0 1 1 1z"/><path d="M15 21c3 0 7-1 7-8V5c0-1.25-.76-2-2-2h-4c-1.25 0-2 .75-2 1.97V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3c0 1 0 1 1 1z"/>',
    "download": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/>',
    "percent": '<path d="M19 5 5 19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/>',
    "help": '<circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3M12 17h.01"/>',
    "pen": '<path d="M12 20h9M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/>',
    "sparkle": '<path d="M12 3l1.9 5.8L20 11l-6.1 2.2L12 19l-1.9-5.8L4 11l6.1-2.2z"/>',
    "compass": '<circle cx="12" cy="12" r="10"/><path d="m16.24 7.76-2.12 6.36-6.36 2.12 2.12-6.36z"/>',
    "login": '<path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M15 12H3"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "link": '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
    "external": '<path d="M15 3h6v6M10 14 21 3M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
    "award": '<circle cx="12" cy="8" r="6"/><path d="M15.48 12.89 17 22l-5-3-5 3 1.52-9.11"/>',
    "laptop": '<path d="M20 16V7a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v9m16 0H4m16 0 1.28 2.55a1 1 0 0 1-.9 1.45H3.62a1 1 0 0 1-.9-1.45L4 16"/>',
    "instagram": '<rect x="2" y="2" width="20" height="20" rx="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><path d="M17.5 6.5h.01"/>',
    "facebook": '<path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/>',
    "linkedin": '<path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-4 0v7h-4v-7a6 6 0 0 1 6-6z"/><rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/>',
    "userplus": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M19 8v6M22 11h-6"/>',
    "gift": '<rect x="3" y="8" width="18" height="4" rx="1"/><path d="M12 8v13M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7M7.5 8a2.5 2.5 0 0 1 0-5C11 3 12 8 12 8s1-5 4.5-5a2.5 2.5 0 0 1 0 5"/>',
}


def icon(name, cls=""):
    return f'<svg class="i {cls}" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


e = escape  # short alias for templates

# ---------------------------------------------------------------- components

def btn_call(label=CTA_LABEL, cls="btn btn-primary"):
    # All consultation buttons go to the Contact form; the team replies with a booking link.
    return f'<a class="{cls}" href="/contact.html">{e(label)} {icon("arrow")}</a>'


def btn_pricing(label="See Plans & Pricing"):
    return f'<a class="btn btn-outline" href="/pricing.html">{e(label)}</a>'


def badge(text, upper=False):
    return f'<span class="badge{" upper" if upper else ""}">{e(text)}</span>'


def checks(items, two=False):
    lis = "".join(f"<li>{icon('check')}<span>{e(t)}</span></li>" for t in items)
    return f'<ul class="checks{" two" if two else ""}">{lis}</ul>'


def list_check(items, cols=False):
    lis = "".join(f"<li>{icon('check')}<span>{t}</span></li>" for t in items)
    return f'<ul class="list-check{" cols" if cols else ""}">{lis}</ul>'


def breadcrumbs(trail):
    """trail: list of (label, href|None)."""
    parts = []
    for i, (label, href) in enumerate(trail):
        if i:
            parts.append('<span aria-hidden="true">/</span>')
        parts.append(f'<a href="{href}">{e(label)}</a>' if href else f'<span>{e(label)}</span>')
    return f'<nav class="breadcrumbs" aria-label="Breadcrumb">{"".join(parts)}</nav>'


def page_hero(*, trail, eyebrow, title, lead, image=None, image_alt="", chip=None, actions=None, center=False, extra=""):
    actions = actions if actions is not None else btn_call() + btn_pricing()
    text = f"""
      {breadcrumbs(trail)}
      {badge(eyebrow)}
      <h1 class="h1">{title}</h1>
      <p class="lead">{lead}</p>{extra}
      {f'<div class="actions">{actions}</div>' if actions else ''}"""
    if image:
        chip_html = ""
        if chip:
            chip_html = f'<div class="media-chip"><div class="ico-box">{icon(chip[0])}</div><div><strong>{e(chip[1])}</strong><span>{e(chip[2])}</span></div></div>'
        body = f"""<div class="split"><div>{text}</div>
      <div class="media reveal"><div class="media-frame"><img src="{image}" alt="{e(image_alt)}" width="1200" height="1000"></div>{chip_html}</div></div>"""
    else:
        body = f'<div class="{"center" if center else ""}" style="max-width:{"48rem;margin:0 auto" if center else "48rem"}">{text}</div>'
    return f'<section class="page-hero{" center" if center else ""}"><div class="container">{body}</div></section>'


def section_head(eyebrow, title, lead=None, left=False):
    return f"""<div class="section-head{" left" if left else ""}">{badge(eyebrow)}<h2 class="h2">{title}</h2>{f'<p class="lead">{lead}</p>' if lead else ''}</div>"""


def cta_band(title="Spend less time on the numbers and more time with your clients",
             lead="Whether you're working solo, running a clinic or managing another business, we’ll explain things in plain English and help you choose the right support.",
             eyebrow="Free Consultation Call"):
    return f"""<section class="section"><div class="container"><div class="cta-band reveal">
      {badge(eyebrow)}<h2 class="h2">{title}</h2><p class="lead">{lead}</p>
      <div class="actions">{btn_call()}</div>
      {checks(CTA_CHECKS)}
    </div></div></section>"""


def faq(items):
    out = "".join(
        f'<details><summary>{e(q)} {icon("plus")}</summary><div>{a}</div></details>' for q, a in items)
    return f'<div class="faq">{out}</div>'


def faq_section(items, title="Common questions", eyebrow="FAQ", reviewed=False):
    note = f'<p class="reviewed">{icon("calendar")}Tax information last reviewed: {SITE["reviewed"]}</p>' if reviewed else ""
    return f"""<section class="section"><div class="container container-narrow">
      <div class="section-head">{badge(eyebrow)}<h2 class="h2">{title}</h2>{note}</div>{faq(items)}</div></section>"""


def service_card(s, tag=True, text=None, tag_text=None):
    tg = tag_text or s["tag"]
    t = f'<span class="tag">{e(tg)}</span>' if tag else ""
    return f"""<a class="card reveal" href="/services/{s['slug']}.html">
      <div class="card-top"><div class="ico-box">{icon(s['icon'])}</div>{t}</div>
      <h3>{e(s['name'])}</h3><p>{e(text or s['short'])}</p>
      <span class="link">Learn more {icon('arrow')}</span></a>"""


def steps(items):
    out = []
    for i, (title, meta, text) in enumerate(items, 1):
        m = f'<span class="step-meta">{icon("clock")}{e(meta)}</span>' if meta else ""
        out.append(f"""<div class="card card-row reveal step"><span class="step-num">{i:02d}</span>
          <div class="step-body"><div class="step-head"><h3>{e(title)}</h3>{m}</div><p>{e(text)}</p></div></div>""")
    return f'<div class="stack">{"".join(out)}</div>'


def how_we_work_section(alt=True):
    """The revised Home 'How we work together' block, reused on every Services page."""
    return f"""<section class="section{' section-alt' if alt else ''}" id="how-we-work"><div class="container">
  {section_head('Simple onboarding', HOW_WE_WORK['title'], HOW_WE_WORK['lead'])}
  <div class="split stretch">
    <div class="media media-fill reveal"><div class="media-frame"><img src="{IMG['how']}" alt="Client checking in at a calm, modern clinic front desk" width="1000" height="1200" loading="lazy"></div>
      <div class="media-chip"><div class="ico-box">{icon('sparkle')}</div><div><strong>Zero disruption to your day</strong><span>We work quietly in the background so you can stay focused on your clients.</span></div></div></div>
    <div class="steps-col">{steps(HOW_WE_WORK['steps'])}<div class="actions">{btn_call()}</div></div>
  </div>
</div></section>"""


# ---------------------------------------------------------------- header / footer

def _dd_link(href, ic, label, sub=None):
    sub_html = f'<small class="muted" style="display:block;font-size:.75rem;font-weight:400">{e(sub)}</small>' if sub else ""
    return f'<a class="dd-link" href="{href}"><span class="ico">{icon(ic)}</span><span>{e(label)}{sub_html}</span></a>'


def serve_menu_html():
    health = "".join(_dd_link(f"/who-we-serve/{p['slug']}.html", p["icon"], p["nav"]) for p in NAV_SERVE_HEALTH)
    other = "".join(_dd_link(f"/who-we-serve/other-industries.html#{i['slug']}", i["icon"], i["name"]) for i in NAV_SERVE_OTHER)
    return f"""<div class="dd-group"><div class="dd-group-title">{icon('heart')}Health &amp; Wellness</div>{health}</div>
      <div class="dd-group"><div class="dd-group-title">{icon('briefcase')}Other Industries</div>{other}</div>"""


def services_menu_html():
    return "".join(_dd_link(f"/services/{s['slug']}.html", s["icon"], s["name"]) for s in SERVICES)


def resources_menu_html():
    return "".join(_dd_link(r["href"], r["icon"], r["name"]) for r in RESOURCES)


def header(active):
    # Client Login always shows; it opens the client portal once its URL is set in content.SITE
    login_url = (SITE.get("client_login") or "").strip()
    tgt = ' target="_blank" rel="noopener"' if login_url else ""
    login_href = e(login_url) if login_url else "#"
    login_top = f'<a class="topbar-login" href="{login_href}"{tgt}>{icon("login")}Client Login</a>'
    login_mobile = f'<a class="btn btn-outline btn-block" href="{login_href}"{tgt}>{icon("login")} Client Login</a>'
    def cur(key):
        return ' aria-current="page"' if active == key else ""

    def dd(key, label, inner, mega=False):
        cls = "dropdown dropdown-mega" if mega else "dropdown"
        act = " active" if active == key else ""
        footer = ""
        if mega:
            footer = f'<div class="dd-footer"><span class="muted">Not sure where you fit? We support practitioners and businesses across Canada.</span><a class="link" href="/who-we-serve/">See everyone we serve {icon("arrow")}</a></div>'
        return f"""<li class="nav-item has-dd"><button class="nav-link{act}" aria-expanded="false" aria-haspopup="true">{label} {icon('chev')}</button>
          <div class="{cls}">{inner}{footer}</div></li>"""

    services_inner = services_menu_html() + f'<div style="border-top:1px solid var(--border);margin-top:.5rem;padding:.75rem .75rem .25rem"><a class="link" href="/services/">All services {icon("arrow")}</a></div>'
    resources_inner = resources_menu_html()

    nav = f"""<ul class="nav-list">
      <li class="nav-item"><a class="nav-link" href="/"{cur('home')}>Home</a></li>
      {dd('serve', 'Who We Serve', serve_menu_html(), mega=True)}
      {dd('services', 'Services', services_inner)}
      <li class="nav-item"><a class="nav-link" href="/pricing.html"{cur('pricing')}>Pricing</a></li>
      <li class="nav-item"><a class="nav-link" href="/our-story.html"{cur('story')}>Our Story</a></li>
      {dd('resources', 'Resources', resources_inner)}
      <li class="nav-item"><a class="nav-link" href="/contact.html"{cur('contact')}>Contact Us</a></li>
    </ul>"""

    mobile = f"""<div class="mobile-menu" id="mobile-menu">
      <a class="m-link" href="/">Home</a>
      <button class="m-toggle" aria-expanded="false">Who We Serve {icon('chev')}</button><div class="m-panel">{serve_menu_html()}<a class="dd-link" href="/who-we-serve/"><span class="ico">{icon('compass')}</span>Everyone we serve</a></div>
      <button class="m-toggle" aria-expanded="false">Services {icon('chev')}</button><div class="m-panel">{services_menu_html()}<a class="dd-link" href="/services/"><span class="ico">{icon('compass')}</span>All services</a></div>
      <a class="m-link" href="/pricing.html">Pricing</a>
      <a class="m-link" href="/our-story.html">Our Story</a>
      <button class="m-toggle" aria-expanded="false">Resources {icon('chev')}</button><div class="m-panel">{resources_menu_html()}</div>
      <a class="m-link" href="/contact.html">Contact Us</a>
      <div class="mobile-cta">{btn_call(cls="btn btn-primary btn-block")}{login_mobile}</div>
    </div>"""

    topbar = f"""<div class="topbar"><div class="container topbar-inner">
    <div class="topbar-contact"><a href="tel:{SITE['phone_href']}">{icon('phone')}<span>{e(SITE['phone'])}</span></a>
      <a href="mailto:{SITE['email']}">{icon('mail')}<span>{e(SITE['email'])}</span></a>
      <span class="topbar-loc">{icon('pin')}{e(SITE['location'])}</span></div>
    {login_top}
  </div></div>"""
    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="site-header">{topbar}<div class="container header-inner">
  <a class="logo" href="/" aria-label="YS Tax &amp; Advisory home"><img src="/assets/img/logo-header.svg" alt="YS Tax &amp; Advisory" width="95" height="68"></a>
  <nav class="nav" aria-label="Main">{nav}</nav>
  <div class="header-actions">{btn_call(cls="btn btn-primary btn-sm")}</div>
  <button class="menu-toggle" aria-label="Open menu" aria-expanded="false" aria-controls="mobile-menu">{icon('menu', 'open-i')}{icon('x', 'close-i')}</button>
</div></header>
{mobile}"""


SOCIAL_LABELS = {"instagram": "Instagram", "facebook": "Facebook", "linkedin": "LinkedIn"}


def socials_html():
    """Logo-only social icons; an icon becomes a link once its URL is set in content.SITE['socials']."""
    out = []
    for key, label in SOCIAL_LABELS.items():
        url = SITE["socials"].get(key)
        if url:
            out.append(f'<a href="{e(url)}" target="_blank" rel="noopener" aria-label="{label}">{icon(key)}</a>')
        else:
            out.append(f'<span class="soon" title="{label} (link coming soon)">{icon(key)}</span>')
    return f'<div class="socials">{"".join(out)}</div>'


def footer():
    serve = "".join(f'<li><a href="/who-we-serve/{p["slug"]}.html">{e(p["nav"])}</a></li>' for p in NAV_SERVE_HEALTH)
    serve += '<li><a href="/who-we-serve/other-industries.html">Other Industries</a></li>'
    serv = "".join(f'<li><a href="/services/{s["slug"]}.html">{e(s["name"])}</a></li>' for s in SERVICES)
    quick = "".join(f'<li><a href="{h}">{e(l)}</a></li>' for l, h in [
        ("Home", "/"), ("Pricing", "/pricing.html"), ("Blog", "/resources/blog/"),
        ("Free Incorporation Guide", "/resources/incorporation-guide.html"), ("Useful Links", "/resources/useful-links/")])
    connect = "".join(
        f'<li>{icon("userplus")}<a href="/assets/contact/{c["file"]}" download>{e(c["label"])}</a></li>' for c in CONTACT_CARDS)
    return f"""<footer class="site-footer"><div class="container">
  <div class="footer-grid">
    <div class="footer-brand"><img src="/assets/img/logo-footer.svg" alt="YS Tax &amp; Advisory" width="134" height="96">
      <p>Accounting, tax and advisory services for healthcare professionals and businesses across Canada.</p>
      {socials_html()}
    </div>
    <div><h3>Who We Serve</h3><ul class="f-links">{serve}</ul></div>
    <div><h3>Services</h3><ul class="f-links">{serv}</ul></div>
    <div><h3>Quick Links</h3><ul class="f-links">{quick}</ul></div>
    <div><h3>Contact</h3><ul class="f-links">
        <li>{icon('pin')}<span>Based in Delta, BC<br>Virtual across Canada</span></li>
        <li>{icon('phone')}<a href="tel:{SITE['phone_href']}">{e(SITE['phone'])}</a></li>
        <li>{icon('mail')}<a href="mailto:{SITE['email']}">{e(SITE['email'])}</a></li>
        <li>{icon('clock')}<span>{e(SITE['hours'])}</span></li>
        {connect}
      </ul></div>
  </div>
  <div class="footer-bottom"><p>&copy; <span id="year">2026</span> YS Tax &amp; Advisory. All rights reserved.<br>
      <a href="/privacy-policy.html">Privacy Policy</a> <span aria-hidden="true">·</span> <a href="/terms-of-service.html">Terms of Service</a></p>
    <p>The content on this site is general information only and does not constitute professional accounting, tax, or legal advice. Please contact us directly for guidance specific to your situation.</p></div>
</div></footer>"""


def write_vcards(out_root):
    """Downloadable contact cards (.vcf) for the footer "Connect with" links."""
    d = Path(out_root) / "assets" / "contact"
    d.mkdir(parents=True, exist_ok=True)
    for c in CONTACT_CARDS:
        lines = ["BEGIN:VCARD", "VERSION:3.0", f"N:{c['last']};{c['first']};;;", "FN:" + c["full"].replace(",", "\\,"),
                 f"ORG:{SITE['name']}", f"TITLE:{c['title']}", f"TEL;TYPE=WORK,VOICE:{c['phone']}",
                 f"EMAIL;TYPE=INTERNET,WORK:{c['email']}", "URL:https://ystaxadvisory.ca",
                 "ADR;TYPE=WORK:;;;Delta;British Columbia;;Canada", "END:VCARD"]
        (d / c["file"]).write_bytes(("\r\n".join(lines) + "\r\n").encode("utf-8"))


def layout(*, title, description, active, main, path, extra_head=""):
    canonical = SITE["domain"] + "/" + path.replace("index.html", "")
    return f"""<!doctype html>
<html lang="en-CA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:image" content="{SITE['domain']}/assets/img/bc-health-wellness-clinic-treatment-room.webp">
<meta property="og:site_name" content="YS Tax &amp; Advisory">
<meta name="theme-color" content="#2C6049">
<link rel="icon" href="/assets/img/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/img/favicon-32.png">
<link rel="icon" type="image/png" sizes="192x192" href="/assets/img/favicon-192.png">
<link rel="apple-touch-icon" sizes="180x180" href="/assets/img/favicon-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/styles.css">
{extra_head}
</head>
<body>
{header(active)}
<main id="main">
{main}
</main>
{footer()}
<script src="/assets/js/main.js" defer></script>
</body>
</html>
"""


def write(path, out_root=None, **kw):
    out = (out_root or OUT) / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(layout(path=path, **kw), encoding="utf-8")
    return path


MANIFEST = ".blog-pages.json"


def build_all(out_root=None):
    """Build every page into out_root (default $YS_SITE_OUT or this folder).

    Blog post pages from the previous build that are no longer published (deleted,
    unpublished or renamed) are removed, using a small manifest in out_root.
    """
    import json
    import pages  # imported lazily: pages.py uses the helpers defined above
    out_root = Path(out_root or OUT)
    specs = pages.all_pages()
    blog_now = {p["path"] for p in pages.POSTS}
    mf = out_root / MANIFEST
    blog_before = set(json.loads(mf.read_text())) if mf.exists() else set()
    for stale in blog_before - blog_now:
        f = out_root / stale
        if f.exists():
            f.unlink()
            if f.name == "index.html" and f.parent != out_root and not any(f.parent.iterdir()):
                f.parent.rmdir()
    built = [write(spec.pop("path"), out_root=out_root, **spec) for spec in specs]
    write_vcards(out_root)
    mf.write_text(json.dumps(sorted(blog_now), indent=1))
    return built


def main():
    built = build_all()
    print(f"Built {len(built)} pages into {OUT}:")
    for p in built:
        print("  ", p)


if __name__ == "__main__":
    main()
