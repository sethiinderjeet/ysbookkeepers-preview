"""Page bodies. Each function returns a spec dict consumed by build.write()."""
import json
from pathlib import Path
from datetime import date

from build import (icon, e, btn_call, btn_pricing, badge, checks, list_check, page_hero, section_head,
                   cta_band, faq, faq_section, service_card, how_we_work_section)
from content import (SITE, IMG, SERVICES, HOME_SERVICES, PROFESSIONS, INDUSTRIES, OTHER_INDUSTRY_CARD_TEXT,
                     RESOURCES, USEFUL_LINKS, FORM_LIMITS, TESTIMONIALS, GOOGLE_REVIEWS_URL, MARQUEE, PRICING, CTA_CHECKS, GUIDE)

from blogstore import published_posts

SVC = {s["slug"]: s for s in SERVICES}
POSTS = []  # published posts, loaded from SQLite in all_pages()
BIZ_CTA = "Let's talk about your business"


def fmt_date(iso):
    return date.fromisoformat(iso).strftime("%B %-d, %Y")


def post_url(p):
    return "/" + p["path"].replace("index.html", "")


def view_all_services():
    return f'<p class="center mt-4"><a class="btn btn-outline" href="/services/">View All Services {icon("arrow")}</a></p>'


def not_sure_card(business=True):
    who = "your practice or business" if business else "your practice"
    return f"""<div class="card card-feature not-sure reveal">
      <div><span class="tag">Free Consultation</span><h3 class="mt-2">Not sure which service is right for you?</h3>
      <p>Tell us a bit about {who} and we’ll look at your current setup, explain your options and help you decide what support makes sense. <strong>No pressure, just clarity.</strong></p></div>
      <div>{btn_call()}</div></div>"""


# ======================================================================= HOME
def home():
    health_links = "".join(
        f'<a href="/who-we-serve/{p["slug"]}.html"><span>{e(p["list_name"])}'
        + (f'<small>{e(p["list_sub"])}</small>' if p.get("list_sub") else "")
        + f'</span>{icon("arrow")}</a>' for p in PROFESSIONS)
    other_links = "".join(
        f'<a href="/who-we-serve/other-industries.html#{i["slug"]}"><span>{e(i["name"])}</span>{icon("arrow")}</a>' for i in INDUSTRIES)

    why = [
        ("heart", "We know how your practice earns", "Associate splits, room rentals, Jane and Cliniko payouts, direct billing and product sales — we understand the accounting and tax questions that come with each."),
        ("message", "Advice you'll actually understand", "Clear, straightforward guidance without the accounting jargon."),
        ("calendar", "Support all year, not just at tax time", "We plan ahead with you, so deadlines never sneak up and decisions never feel rushed."),
        ("trend", "Guidance that grows with your practice", "From incorporating to hiring, expanding, or securing funding, we help you make confident next moves."),
    ]
    why_html = "".join(
        f'<div class="card card-row reveal"><div class="ico-box">{icon(i)}</div><div><h3>{e(t)}</h3><p>{e(d)}</p></div></div>' for i, t, d in why)
    stats = [("award", "15+ Years", "Accounting & Tax Experience"), ("pin", "Delta, BC", "Proudly Based in BC"), ("laptop", "Across Canada", "Virtual Services")]
    stats_html = "".join(f'<div class="stat-item"><div class="stat-ico">{icon(i)}</div><strong>{e(t)}</strong><span>{e(s)}</span></div>' for i, t, s in stats)
    marquee_items = "".join(f"<span>{e(m)}</span><span class=\"dot\" aria-hidden=\"true\">•</span>" for m in MARQUEE)
    stars = '<div class="stars" role="img" aria-label="5 out of 5 stars">' + '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.5l2.9 6.1 6.6.8-4.9 4.6 1.3 6.6L12 17.3 6.1 20.6l1.3-6.6L2.5 9.4l6.6-.8z"/></svg>' * 5 + '</div>'
    reviews_html = "".join(f"""<figure class="card quote-card review-card reveal">
      <div class="card-top">{stars}<span class="tag">Google review</span></div>
      <blockquote>&ldquo;{e(r['quote'])}&rdquo;</blockquote>
      <figcaption class="quote-person"><div><strong>{e(r['name'])}</strong>{f'<span>{e(r["role"])}</span>' if r['role'] else ''}</div></figcaption>
    </figure>""" for r in TESTIMONIALS)

    main = f"""
<section class="hero">
  <div class="hero-bg"><img src="{IMG['hero']}" alt="Sunlit BC wellness treatment room with a massage table, folded towels and plants" width="1920" height="1081" fetchpriority="high"></div>
  <div class="container"><div class="hero-content">
    {badge('Accounting for Health & Wellness', upper=True)}
    <h1 class="h1">Accounting, Tax &amp; Advisory for BC Health &amp; Wellness Practices</h1>
    <p class="lead">From solo practitioners to multi-practitioner clinics, we handle your tax, bookkeeping and payroll - with advice built around the way your practice actually works.</p>
    {checks(["Corporate (T2) & personal (T1) tax returns", "Tax planning & incorporation guidance", "Bookkeeping, GST/HST, payroll & year-end filings", "Year-round support, not just at tax time."], two=True)}
    <div class="actions">{btn_call()}<a class="underline-link" href="{GUIDE}">Get the free incorporation guide</a></div>
    <div class="hero-foot">{icon('pin')}<span>Based in Delta, BC. Serving physiotherapists, RMTs, counsellors, dentists, naturopathic doctors, clinic owners and other health &amp; wellness professionals across British Columbia.</span></div>
  </div></div>
</section>

<div class="marquee" aria-label="What we help with: {e(', '.join(MARQUEE))}"><div class="marquee-track" aria-hidden="true">
  <div class="marquee-group">{marquee_items}</div><div class="marquee-group">{marquee_items}</div>
</div></div>

<section class="section" id="why-were-different"><div class="container"><div class="split stretch">
  <div class="media media-fill reveal"><div class="media-frame"><img src="{IMG['why']}" alt="Accountant reviewing financial reports with a healthcare clinic owner" width="1080" height="1350" loading="lazy"></div>
    <div class="media-chip"><div class="ico-box">{icon('heart')}</div><div><strong>Focused on BC health &amp; wellness</strong><span>Zero accounting jargon</span></div></div></div>
  <div>
    {badge('Why YS?')}
    <h2 class="h2">Why Health &amp; Wellness Practices Choose YS</h2>
    <p class="lead mt-2">Your practice isn't a typical small business. The way you earn, bill clients, pay practitioners and handle GST can be very different from other businesses. We understand those differences, so the advice you receive fits the way your practice actually operates.</p>
    <div class="stack mt-4">{why_html}</div>
  </div>
</div>
  <div class="stats-strip reveal">{stats_html}</div>
  <div class="actions center-actions">{btn_call()}<a class="underline-link" href="/our-story.html">Read our story</a></div>
</div></section>

<section class="section section-alt" id="who-we-serve"><div class="container">
  {section_head('Who we serve', 'Built for BC health &amp; wellness, trusted by local businesses', 'Accounting built for health and wellness practitioners, from solo practices to multi-practitioner clinics, plus a select group of local businesses.')}
  <div class="grid grid-2">
    <div class="card audience reveal"><div class="audience-head"><div class="ico-box">{icon('heart')}</div><div><h3>Health &amp; Wellness</h3><p class="muted">Our specialty, with dedicated guidance for each profession</p></div></div>
      <div class="audience-list">{health_links}</div></div>
    <div class="card audience reveal"><div class="audience-head"><div class="ico-box">{icon('briefcase')}</div><div><h3>Other Industries</h3><p class="muted">The same clear, proactive approach for every business we serve</p></div></div>
      <div class="audience-list">{other_links}</div></div>
  </div>
  <div class="inline-cta mt-6 reveal"><div><h3>Don't see your profession or industry listed?</h3><p>Let's talk about your situation and the support you need.</p></div>{btn_call(cls="btn btn-light")}</div>
</div></section>

<section class="section" id="services"><div class="container">
  {section_head('Our Services', 'Tax, Accounting &amp; Advisory built around your practice', 'From your first self-employed tax return to running a multi-practitioner clinic, with the same full support for businesses in other industries.')}
  <div class="grid grid-3">{''.join(service_card(SVC[s]) for s in HOME_SERVICES)}</div>
  {view_all_services()}
  <div class="mt-6">{not_sure_card()}</div>
</div></section>

{how_we_work_section()}

<section class="section" id="client-trust"><div class="container">
  {section_head('Client stories', 'Trusted by BC health &amp; wellness practitioners', 'Real feedback from practitioners and business owners we work with across BC.')}
  <div class="grid grid-3 reviews">{reviews_html}</div>
  <p class="center mt-3"><a class="link" href="{GOOGLE_REVIEWS_URL}" target="_blank" rel="noopener">Read our reviews on Google {icon('external')}</a></p>
  <div class="inline-cta mt-6 reveal"><div><h3>Ready to take the guesswork out of your practice books?</h3><p>Book a free, no-obligation consultation. We'll look at your current setup and give you clear, practical answers, wherever you are in Canada.</p></div>{btn_call(cls="btn btn-light")}</div>
</div></section>

{cta_band()}
"""
    return dict(path="index.html", active="home", main=main,
                title="YS Tax & Advisory | Accounting, Tax & Advisory for BC Health & Wellness Practices",
                description="Accounting, tax and advisory for BC physiotherapists, RMTs, counsellors, naturopathic doctors and clinic owners. Based in Delta, BC, virtual across Canada. Book a free consultation.")


# ======================================================================= WHO WE SERVE
CARD_TITLES = {"rmts": "Registered Massage Therapists", "other-health-practitioners": "Other Health Practitioners"}


def serve_index():
    prof_cards = "".join(f"""<a class="card reveal" href="/who-we-serve/{p['slug']}.html"><div class="ico-box">{icon(p['icon'])}</div>
      <h3>{e(CARD_TITLES.get(p['slug'], p['title']))}</h3><p>{e(p['serve_desc'])}</p><span class="link">Learn more {icon('arrow')}</span></a>""" for p in PROFESSIONS)
    ind_cards = "".join(f"""<a class="card reveal" href="/who-we-serve/other-industries.html#{i['slug']}"><div class="ico-box">{icon(i['icon'])}</div>
      <h3>{e(i['name'])}</h3><p>{e(i['summary'])}</p><span class="link">Learn more {icon('arrow')}</span></a>""" for i in INDUSTRIES)
    ind_cards += f"""<a class="card card-feature reveal" href="/contact.html"><div class="ico-box">{icon('compass')}</div>
      <h3>Don't See Your Industry?</h3><p>We work with businesses across a range of industries. Tell us about your business, and we'll help you determine whether we're the right fit.</p>
      <span class="link">Book a Free Consultation {icon('arrow')}</span></a>"""
    main = f"""
{page_hero(trail=[('Home', '/'), ('Who We Serve', None)], eyebrow='Who we serve', center=True,
           title='Accounting That Understands Your Profession/Industry',
           lead='From solo RMTs, counsellors and yoga instructors to dental practices and multi-practitioner clinics, we understand the financial side of running a health and wellness practice. We also support businesses in construction, hospitality, real estate, technology and professional services with practical tax, bookkeeping and advisory services.')}
<section class="section-tight"><div class="container">
  {section_head('Our specialty', 'Health &amp; Wellness', 'Dedicated guidance for each profession: the GST rules, expenses and structures that apply to you.', left=True)}
  <div class="grid grid-3">{prof_cards}</div>
</div></section>
<section class="section"><div class="container">
  {section_head('Beyond Wellness', 'Other Industries', 'The same clear, proactive accounting and tax support for businesses across other industries.', left=True)}
  <div class="grid grid-3">{ind_cards}</div>
</div></section>
{cta_band(title=BIZ_CTA, lead="Whether you're self-employed, running a growing business or thinking about incorporating, tell us a little about your situation. We'll explain things in plain English and help you figure out what support you need.")}"""
    return dict(path="who-we-serve/index.html", active="serve", main=main,
                title="Who We Serve | YS Tax & Advisory",
                description="Accounting, tax and advisory for BC RMTs, physiotherapists, counsellors, naturopathic doctors, clinic owners and other health practitioners, plus small businesses across Canada.")


def profession(p):
    challenges = "".join(f'<div class="card reveal"><div class="ico-box">{icon(i)}</div><h3>{e(t)}</h3><p>{e(d)}</p></div>' for i, t, d in p["challenges"])
    help_cards = "".join(service_card(SVC[slug], text=text) for slug, text in p["help"])
    pills = ""
    if p.get("pills"):
        pills = f"""<section class="section-tight"><div class="container center">
          <p class="eyebrow-label">PRACTITIONERS WE SUPPORT INCLUDE</p>
          <div class="pills" style="justify-content:center">{''.join(f'<span class="pill">{icon("check")}{e(x)}</span>' for x in p['pills'])}</div></div></section>"""
    others = "".join(f'<a class="pill" href="/who-we-serve/{o["slug"]}.html">{icon(o["icon"])}{e(o["nav"])}</a>' for o in PROFESSIONS if o is not p)
    main = f"""
{page_hero(trail=[('Home', '/'), ('Who We Serve', '/who-we-serve/'), (p['nav'], None)], eyebrow=f"For {p['title']}",
           title=p['h1'], lead=e(p['lead']), image=IMG[p['image']], image_alt=p['image_alt'],
           chip=(p['icon'], p['chip'][0], p['chip'][1]))}
{pills}
<section class="section"><div class="container">
  {section_head('We understand your practice', p['ch_h2'], e(p['ch_lead']))}
  <div class="grid grid-4">{challenges}</div>
</div></section>
<section class="section section-alt"><div class="container">
  {section_head('How we help', p['help_h2'], 'Pick what you need now and add more as your practice grows.')}
  <div class="grid grid-4">{help_cards}</div>
  {view_all_services()}
</div></section>
<section class="section"><div class="container"><div class="split">
  <div>{badge('Practical tips')}<h2 class="h2">{p['tips_h2']}</h2>
    <p class="lead mt-2">Small habits that make tax time easier.</p>
    <div class="actions">{btn_call()}<a class="underline-link" href="{GUIDE}">Get the free incorporation guide</a></div></div>
  <div class="card reveal">{list_check([e(t) for t in p['tips']])}</div>
</div></div></section>
{faq_section(p['faq'], title=p['faq_h2'], reviewed=True)}
<section class="section-tight"><div class="container center"><p class="eyebrow-label">WE ALSO SUPPORT</p>
  <div class="pills" style="justify-content:center">{others}<a class="pill" href="/who-we-serve/other-industries.html">{icon('briefcase')}Other Industries</a></div></div></section>
{cta_band(title=p['cta_title'], lead=e(p['cta_lead']))}"""
    return dict(path=f"who-we-serve/{p['slug']}.html", active="serve", main=main,
                title=p["seo_title"], description=p["seo_desc"])


def other_industries():
    toc = "".join(f'<a href="#{i["slug"]}">{icon(i["icon"])}{e(i["name"])}</a>' for i in INDUSTRIES)
    blocks = "".join(f"""<article class="card industry reveal" id="{i['slug']}">
        <div style="display:flex;gap:1rem;align-items:center"><div class="ico-box">{icon(i['icon'])}</div><h2 class="h3" style="font-size:1.5rem">{e(i['name'])}</h2></div>
        <p style="font-size:1rem">{e(i['page_summary'])}</p>
        <p class="key-areas">Key areas we support:</p>{list_check([e(x) for x in i['points']], cols=True)}</article>""" for i in INDUSTRIES)
    cards = "".join(service_card(SVC[s], text=OTHER_INDUSTRY_CARD_TEXT.get(s)) for s in HOME_SERVICES)
    main = f"""
{page_hero(trail=[('Home', '/'), ('Who We Serve', '/who-we-serve/'), ('Other Industries', None)], eyebrow='Other industries',
           title='Accounting &amp; Tax Services for Small Businesses in BC',
           lead="From construction and hospitality to real estate, technology and professional services, we help business owners stay on top of their bookkeeping, taxes and financial decisions, so they can focus on running and growing their businesses.",
           image=IMG['smallbiz'], image_alt='Small business owners reviewing paperwork together at the counter of a café',
           chip=('briefcase', 'Built for small businesses', 'Trades, hospitality, real estate & more'))}
<section class="section"><div class="container"><div class="sidebar-layout">
  <aside><div class="industry-nav card" style="padding:1rem"><p class="eyebrow-label" style="padding:.5rem .85rem;margin:0">INDUSTRIES</p><nav class="toc">{toc}</nav></div></aside>
  <div class="stack" style="gap:1.5rem">{blocks}</div>
</div></div></section>
<section class="section section-alt"><div class="container">
  {section_head('How we help', 'The Same Core Services', 'All of our services are available, whatever your industry.')}
  <div class="grid grid-3">{cards}</div>
  {view_all_services()}
</div></section>
{cta_band(title=BIZ_CTA, lead="Whether you're self-employed, running a growing business or thinking about incorporating, tell us a little about your situation. We'll explain things in plain English and help you figure out what support you need.")}"""
    return dict(path="who-we-serve/other-industries.html", active="serve", main=main,
                title="Accounting & Tax for Small Businesses in BC | YS Tax & Advisory",
                description="Bookkeeping, tax and advisory for BC construction & trades, restaurants, real estate, tech startups, consultants and self-employed professionals.")


# ======================================================================= SERVICES
def services_index():
    main = f"""
{page_hero(trail=[('Home', '/'), ('Services', None)], eyebrow='Our Services', center=True,
           title='Tax, Accounting &amp; Advisory built around your practice',
           lead='From your first self-employed tax return to running a multi-practitioner clinic, with the same full support for businesses in other industries.')}
<section class="section-tight"><div class="container">
  <div class="grid grid-3">{''.join(service_card(s) for s in SERVICES)}</div>
  <div class="mt-6">{not_sure_card()}</div>
</div></section>
{how_we_work_section(alt=False)}
<section class="section-tight"><div class="container"><div class="inline-cta reveal"><div><h3>Want to know what it costs?</h3><p>Clear monthly plans with no hourly billing. See our packages and what's included.</p></div><a class="btn btn-light" href="/pricing.html">See Plans &amp; Pricing {icon('arrow')}</a></div></div></section>
{cta_band()}"""
    return dict(path="services/index.html", active="services", main=main,
                title="Services | Tax, Accounting & Advisory | YS Tax & Advisory",
                description="Corporate and personal tax, incorporation guidance, monthly and catch-up bookkeeping, payroll, advisory and business plans for BC practitioners and small businesses.")


def service(s):
    ideal = "".join(f'<span class="pill">{icon("check")}{e(x)}</span>' for x in s["ideal"])
    benefits = "".join(f'<div class="card card-row reveal" style="align-items:center"><div class="ico-box">{icon("check")}</div><h3 style="margin:0">{e(b)}</h3></div>' for b in s["benefits"])
    foot = f'<p class="footnote">{e(s["footnote"])}</p>' if s.get("footnote") else ""
    related = []
    for slug, tag, text in s["related"]:
        rs = SVC[slug]
        related.append(service_card(rs, text=text or rs["rel"][1], tag_text=tag or rs["rel"][0]))
    main = f"""
{page_hero(trail=[('Home', '/'), ('Services', '/services/'), (s['name'], None)], eyebrow=s['eyebrow'],
           title=e(s.get('h1', s['name'])), lead=e(s['lead']), image=IMG['consult'],
           image_alt='Accountant meeting with a business owner across a wooden desk', chip=(s['icon'], s['chip'][0], s['chip'][1]))}
<section class="section-tight"><div class="container center"><p class="eyebrow-label">IDEAL FOR</p>
  <div class="pills" style="justify-content:center">{ideal}</div></div></section>
<section class="section"><div class="container"><div class="split" style="align-items:start">
  <div>{badge("What's included")}<h2 class="h2">{e(s['inc_h2'])}</h2>
    {f'<p class="lead mt-2">{e(s["inc_lead"])}</p>' if s.get('inc_lead') else ''}
    <div class="stack mt-4">{benefits}</div></div>
  <div class="card reveal">{list_check([e(x) for x in s['includes']])}{foot}<div class="actions" style="margin-top:1rem">{btn_call()}{btn_pricing()}</div></div>
</div></div></section>
{how_we_work_section()}
{faq_section(s['faq'], title=e(s['faq_h2']), reviewed=s.get('reviewed'))}
<section class="section-tight"><div class="container">
  {section_head('Related services', 'Often paired with', None)}
  <div class="grid grid-3">{''.join(related)}</div>
</div></section>
{cta_band(title=BIZ_CTA, lead=e(s['cta_lead']))}"""
    return dict(path=f"services/{s['slug']}.html", active="services", main=main,
                title=s["seo_title"], description=s["seo_desc"])


# ======================================================================= PRICING
def pricing():
    def plan_card(pl):
        feats = []
        for i, f in enumerate(pl["features"]):
            if f.startswith("Everything in"):
                feats.append(f'<li class="inherit">{e(f)}</li>')
            else:
                feats.append(f"<li>{icon('check')}<span>{e(f)}</span></li>")
        note = f'<p class="footnote">Note: {e(pl["note"])}</p>' if pl.get("note") else ""
        pop = pl.get("popular")
        return f"""<div class="card price-card{' featured' if pop else ''} reveal">{'<span class="ribbon">Most Popular</span>' if pop else ''}
          <h3 style="font-size:1.4rem">{e(pl['name'])}</h3><p>{e(pl['desc'])}</p>
          <div class="price"><small>Starting from</small><br>{pl['price']}<small>/month</small></div><hr>
          <ul class="list-check">{''.join(feats)}</ul>{note}
          <div style="margin-top:auto;padding-top:1rem">{btn_call(cls='btn btn-primary btn-block' if pop else 'btn btn-outline btn-block')}</div></div>"""

    panels = ""
    for key in ("health", "other"):
        grp = PRICING[key]
        title, body = grp["callout"]
        panels += f"""<div class="price-panel" id="plans-{key}" role="tabpanel" aria-labelledby="tab-{key}"{'' if key == 'health' else ' hidden'}>
          <div class="grid grid-3" style="align-items:stretch">{''.join(plan_card(pl) for pl in grp['plans'])}</div>
          <div class="callout-banner reveal"><div><strong>{e(title)}</strong> <span>{e(body)}</span></div>{btn_call('Get a Quote', 'btn btn-primary btn-sm')}</div>
        </div>"""
    tabs = "".join(f'<button class="toggle-btn" role="tab" id="tab-{k}" aria-controls="plans-{k}" aria-selected="{"true" if k == "health" else "false"}" data-target="plans-{k}">{e(PRICING[k]["label"])}</button>' for k in ("health", "other"))
    add_rows = "".join(f"<tr><td><strong>{e(n)}</strong>{f'<br><span class=\"muted small\">{e(sub)}</span>' if sub else ''}</td><td>{e(pr)}</td></tr>" for n, sub, pr in PRICING["additional"])
    custom = "".join(f"""<div class="card reveal"><div class="card-top"><div class="ico-box">{icon(i)}</div><span class="tag">Custom pricing</span></div>
        <h3>{e(t)}</h3><p>{e(d)}</p><div style="margin-top:auto"><a class="link" href="/contact.html">Get a Quote {icon('arrow')}</a></div></div>""" for i, t, d in PRICING["custom"])
    gtk = "".join(f"<li>{icon('check')}<span>{e(x)}</span></li>" for x in PRICING["good_to_know"])
    main = f"""
{page_hero(trail=[('Home', '/'), ('Pricing', None)], eyebrow='Fixed-fee accounting & tax', center=True,
           title='Simple, Transparent Pricing',
           lead='No hourly billing. Clear monthly plans for your accounting, tax and advisory needs, with support that grows alongside your business.', actions='')}
<section class="section-tight" style="padding-top:0"><div class="container">
  <p class="center muted">Select your industry below to see packages built around how you work.</p>
  <div class="toggle" role="tablist" aria-label="Choose your industry">{tabs}</div>
  {panels}
</div></section>
<section class="section-tight"><div class="container"><div class="good-to-know reveal">
  <div>{badge('Good to know')}<ul class="list-check mt-2">{gtk}</ul></div>
  <div class="annual">{icon('gift')}<strong>{e(PRICING['annual'])}</strong></div>
</div></div></section>
<section class="section"><div class="container container-narrow">
  {section_head('Add-ons', 'Additional Services', 'Need extra support? Add services as your business grows.')}
  <div class="table-wrap reveal"><table class="compare addons"><tbody>{add_rows}</tbody></table></div>
  <p class="footnote center mt-2">Note: {e(PRICING['additional_note'])}</p>
</div></section>
<section class="section section-alt"><div class="container">
  {section_head('Custom services', 'Tailored Services. Priced for Your Needs.', "Some projects need a more personalized approach. We'll review your requirements, explain the scope and provide a clear quote before work begins.")}
  <div class="grid grid-4">{custom}</div>
</div></section>
<section class="section" id="referral"><div class="container"><div class="split referral">
  <div class="media reveal"><div class="media-frame"><img src="{IMG['referral']}" alt="Smiling woman holding Canadian bank notes" width="1264" height="1264" loading="lazy"></div></div>
  <div>{badge('Client referral program', upper=True)}<h2 class="h2">Spread the word. Get rewarded.</h2>
    <p class="lead mt-2">Know a business owner or practitioner who could use our help? Refer them to YS, and we’ll thank you with a credit toward your monthly accounting plan.</p>
    <div class="reward-box mt-3"><span class="eyebrow-label" style="margin:0">YOUR REFERRAL REWARD</span><strong>$100 credit per successful referral</strong>
      <p>When someone you refer joins one of our monthly accounting plans and completes their first two paid months.</p></div>
    {list_check(['Refer as many businesses as you like', 'Credit goes toward your future monthly invoices'])}
    <div class="actions"><a class="btn btn-primary" href="/refer-a-business.html">Refer a Business {icon('arrow')}</a></div>
    <p class="footnote mt-2">For active monthly-plan clients. Referral credits are issued after the new client completes two paid months, have no cash value and are applied to future invoices.</p>
  </div>
</div></div></section>
{faq_section(PRICING['faq'], title='Pricing questions', eyebrow="FAQ's")}
{cta_band(title='Get a clear quote in one short call', eyebrow='Free Consultation', lead="Tell us about your business or practice. We'll help you choose the right services and provide clear pricing before you get started. No pressure, no obligation.")}"""
    return dict(path="pricing.html", active="pricing", main=main,
                title="Pricing & Plans | YS Tax & Advisory",
                description="Fixed-fee monthly accounting and tax plans for BC health & wellness practices and small businesses, starting from $299/month. No hourly billing.")


def refer():
    main = f"""
{page_hero(trail=[('Home', '/'), ('Pricing', '/pricing.html'), ('Refer a Business', None)], eyebrow='Client referral program', center=True,
           title='Refer a Business',
           lead='Know a business owner or practitioner who could use our help? Share their details and we’ll take it from there. You’ll receive a $100 credit when they join a monthly plan and complete their first two paid months.', actions='')}
<section class="section-tight" style="padding-top:0"><div class="container container-narrow">
  <div class="form-card reveal">
    <form class="form-grid" method="post" action="/forms/send" data-endpoint="/forms/send" novalidate>
      <input type="hidden" name="form" value="referral"><div class="hp" aria-hidden="true"><label>Leave this empty<input name="website" tabindex="-1" autocomplete="off" maxlength="{FORM_LIMITS['website']}"></label></div>
      <div class="two"><div class="field"><label for="r-name">Your Name</label><input id="r-name" name="your_name" maxlength="{FORM_LIMITS['your_name']}" autocomplete="name" required></div>
      <div class="field"><label for="r-email">Your Email</label><input id="r-email" type="email" name="your_email" maxlength="{FORM_LIMITS['your_email']}" autocomplete="email" inputmode="email" data-validate="email" placeholder="name@example.com" aria-describedby="r-email-err" required><p class="field-error" id="r-email-err" aria-live="polite"></p></div></div>
      <div class="two"><div class="field"><label for="r-rname">Referral’s Name</label><input id="r-rname" name="referral_name" maxlength="{FORM_LIMITS['referral_name']}" required></div>
      <div class="field"><label for="r-remail">Referral’s Email</label><input id="r-remail" type="email" name="referral_email" maxlength="{FORM_LIMITS['referral_email']}" inputmode="email" data-validate="email" placeholder="name@example.com" aria-describedby="r-remail-err" required><p class="field-error" id="r-remail-err" aria-live="polite"></p></div></div>
      <button class="btn btn-primary btn-block" type="submit">Submit Referral {icon('arrow')}</button>
      <p class="form-note">For active monthly-plan clients. Credits have no cash value and are applied to future invoices.</p>
    </form>
    <div class="form-success"><div class="thanks-icon">{icon('gift')}</div><h2 class="h3" style="font-size:1.5rem">Thank you for your referral!</h2><p class="muted mt-1">We’ll reach out to them shortly and keep you posted.</p></div>
  </div>
</div></section>"""
    return dict(path="refer-a-business.html", active="pricing", main=main,
                title="Refer a Business | YS Tax & Advisory",
                description="Refer a business owner or practitioner to YS Tax & Advisory and receive a $100 credit toward your monthly accounting plan.")


# ======================================================================= OUR STORY
def our_story():
    values = [("calendar", "Advice before deadlines", "We help you plan ahead, understand your tax obligations and avoid last-minute surprises."),
              ("message", "Clarity over jargon", "We explain your numbers in plain English. If something's unclear, we take the time to explain it."),
              ("users", "One team that knows your business", "You won’t have to re-explain your situation every time. We learn how your business works and grow with it."),
              ("heart", "Relationships over transactions", "We're here to build lasting relationships, offering thoughtful advice and support as your needs change.")]
    values_html = "".join(f'<div class="card reveal"><div class="ico-box">{icon(i)}</div><h3>{e(t)}</h3><p>{e(d)}</p></div>' for i, t, d in values)
    logos = [("xero", "Xero", 859, 244), ("quickbooks", "QuickBooks Online", 777, 205), ("dext", "Dext", 800, 399),
             ("wagepoint", "Wagepoint", 820, 138), ("jane", "Jane App", 2101, 1801), ("cliniko", "Cliniko", 152, 152)]
    logos_html = "".join(f'<div class="logo-tile"><img src="/assets/img/logos/{f}.png" alt="{e(n)}" width="{w}" height="{h}" loading="lazy">{f"<span>{e(n)}</span>" if f in ("cliniko", "jane") else ""}</div>' for f, n, w, h in logos)
    intro = """<div class="story-intro">
      <p>Throughout his career, Pankaj has worked with individuals and business owners, helping them navigate complex tax matters, stay on top of their finances and make informed financial decisions.</p>
      <p>Today, YS Tax &amp; Advisory combines that hands-on experience with access to a trusted network of CPAs and senior finance professionals, providing practical accounting, tax and advisory support to businesses across industries.</p>
      <p>While we serve a diverse range of clients, we've developed a particular focus on health and wellness practitioners and clinic owners—helping them navigate the financial challenges of running a practice, from incorporation and tax planning to everyday accounting decisions.</p>
      <p>Our approach is simple: clear advice, proactive support and a genuine commitment to helping our clients succeed.</p></div>"""
    main = f"""
{page_hero(trail=[('Home', '/'), ('Our Story', None)], eyebrow='Our story',
           title="Tax and accounting for the people who take care of everyone else",
           lead="Founded by Pankaj Dhall, YS Tax &amp; Advisory (Formerly YS Bookkeepers) is built on over 15 years of experience in tax, accounting and financial management.",
           image=IMG['consult'], image_alt='YS Tax & Advisory meeting with a client', chip=('shield', '15+ years of experience', 'Based in Delta, BC'), extra=intro)}
<section class="section-tight"><div class="container"><div class="stat-row">
  <div class="stat"><strong>15+</strong><span>Years of tax &amp; accounting experience</span></div>
  <div class="stat"><strong>BC</strong><span>Based in Delta, serving clients across Canada</span></div>
  <div class="stat"><strong>100%</strong><span>Virtual, secure client experience</span></div>
  <div class="stat"><strong>1:1</strong><span>A dedicated team that knows your business</span></div>
</div></div></section>
<section class="section"><div class="container"><div class="split reverse founder-split" style="align-items:start">
  <figure class="founder reveal"><div class="media-frame"><img src="{IMG['founder']}" alt="Pankaj Dhall, Founder of YS Tax &amp; Advisory" width="601" height="801" loading="lazy"></div>
    <figcaption><strong>Pankaj Dhall</strong><span>Founder, YS Tax &amp; Advisory</span><em>“Behind the numbers, it's always about people.”</em></figcaption></figure>
  <div>{badge('Why health & wellness')}<h2 class="h2">Why we chose to focus on health &amp; wellness</h2>
    <div class="prose mt-3" style="font-size:1rem">
      <p>For years, we've helped business owners across different industries: from contractors and restaurants to consultants and property owners. Then one conversation inspired us to take a closer look at health and wellness.</p>
      <p>After four busy months of tax season, our founder, Pankaj Dhall, found himself on a physiotherapist's treatment table, getting some much-needed help for his back.</p>
      <p>During the session, the physiotherapist asked, "You run an accounting firm, right? Should I be charging GST? Should I incorporate?"</p>
      <p>Then he apologized for not knowing the answers.</p>
      <p><strong>That moment stayed with Pankaj.</strong></p>
      <p>Here was someone who had spent years learning how to help people recover, move better and live healthier lives. Yet he felt the need to apologize for not understanding taxes and incorporation.</p>
      <p><strong>He knew how to take care of his patients. Who was taking care of the financial side of his practice?</strong></p>
      <p>And the more we looked into it, the clearer it became: health and wellness practices face financial questions that aren't always straightforward. GST treatment varies by profession and service. Incorporation involves tax planning and professional requirements. Clinic owners must also navigate associate arrangements, payroll and business expenses.</p>
      <p>These aren't just accounting questions. They’re decisions that need someone who understands how a practice actually works.</p>
      <p>So we made a decision: we’d go deep on health and wellness.</p>
      <p>Today, we support physiotherapists, RMTs, counsellors, naturopathic doctors, clinic owners and a wide range of other health and wellness professionals, while continuing to serve individuals and businesses across other industries.</p>
      <div class="callout"><strong>Our belief is simple: You take care of your patients and clients. We'll help you take care of the financial side.</strong></div>
    </div></div>
</div></div></section>
<section class="section section-alt"><div class="container">
  {section_head('What we believe', 'The values behind everything we do')}
  <div class="grid grid-4">{values_html}</div>
</div></section>
<section class="section"><div class="container"><div class="split">
  <div>{badge('Our Approach')}<h2 class="h2">Modern tools, human support</h2>
    <p class="lead mt-2">We use trusted cloud accounting tools to keep your financial information organized, accessible and secure. But technology is only part of the experience.</p>
    <p class="lead mt-2">Every report and tax return comes with a real team ready to answer your questions and offer practical guidance when you need it.</p></div>
  <div class="logo-grid reveal">{logos_html}</div>
</div></div></section>
{cta_band(title="Let's get to know you and your business.", eyebrow='Free Consultation',
          lead="Every business has its own story, challenges and goals. We'd love to hear yours. Let's have a conversation about where you are, what you need and how we can help.")}"""
    return dict(path="our-story.html", active="story", main=main,
                title="Our Story | YS Tax & Advisory",
                description="Founded by Pankaj Dhall, YS Tax & Advisory brings 15+ years of tax and accounting experience to BC health & wellness practitioners and businesses across Canada.")


# ======================================================================= RESOURCES
def post_card(p):
    date_html = f"<span>{fmt_date(p['date'])}</span>" if p.get("date") else ""
    return f"""<a class="card post-card reveal" href="{post_url(p)}">
      <div class="thumb"><img src="{p['image']}" alt="{e(p['image_alt'])}" width="2000" height="1414" loading="lazy"></div>
      <div class="body"><div class="post-meta"><span class="tag">{e(p['category'])}</span>{date_html}<span>{p['read']}</span></div>
      <h3>{e(p['title'])}</h3><p>{e(p['excerpt'])}</p><span class="link">Read article {icon('arrow')}</span></div></a>"""


def guide_promo():
    return f"""<div class="inline-cta reveal"><div><span class="tag soon" style="margin-bottom:.75rem">Free download</span><h3>The Incorporation Guide for BC Health &amp; Wellness Practitioners</h3>
      <p>Find out when incorporating makes sense, how health profession corporations work, and how to pay yourself, in plain English.</p></div>
      <a class="btn btn-light" href="{GUIDE}">{icon('download')} Get the free guide</a></div>"""


def resources_index():
    main = f"""
{page_hero(trail=[('Home', '/'), ('Resources', None)], eyebrow='Resources', center=True,
           title='Plain-English guides for BC practitioners and business owners',
           lead='Articles, guides and trusted links to help you understand your numbers, stay compliant, and make confident decisions.', actions='')}
<section class="section-tight"><div class="container">{guide_promo()}</div></section>
<section class="section"><div class="container">
  <div class="row-head"><div>{badge('Blog')}<h2 class="h2">Latest articles</h2></div><a class="link" href="/resources/blog/">All articles {icon('arrow')}</a></div>
  <div class="grid grid-3">{''.join(post_card(p) for p in POSTS)}</div>
</div></section>
<section class="section-tight"><div class="container">
  <a class="card card-row hover reveal" href="/resources/useful-links/" style="align-items:center"><div class="ico-box">{icon('link')}</div>
    <div style="flex:1"><h3>Useful Tax &amp; Business Links</h3><p>Quick access to trusted CRA and BC Government resources for tax rates, payroll, PST, WorkSafeBC and business registration.</p></div>
    <span class="link">Open {icon('arrow')}</span></a>
</div></section>
{cta_band()}"""
    return dict(path="resources/index.html", active="resources", main=main,
                title="Resources | YS Tax & Advisory",
                description="Articles, guides and useful links on tax, GST, bookkeeping and incorporation for BC health and wellness practitioners and small businesses.")


def blog_index():
    main = f"""
{page_hero(trail=[('Home', '/'), ('Resources', '/resources/'), ('Blog', None)], eyebrow='Blog', center=True,
           title='Tax &amp; Accounting Guides for BC Health &amp; Wellness Professionals',
           lead='Plain-English answers to common questions from RMTs, physiotherapists, counsellors and clinic owners about GST, taxes, bookkeeping and incorporation and managing the financial side of their practice or clinic.', actions='')}
<section class="section-tight"><div class="container"><div class="grid grid-3">{''.join(post_card(p) for p in POSTS)}</div></div></section>
<section class="section"><div class="container">{guide_promo()}</div></section>
{cta_band()}"""
    return dict(path="resources/blog/index.html", active="resources", main=main,
                title="Tax Guides for BC Health Practitioners | YS Tax & Advisory",
                description="Plain-English guides on GST, tax, bookkeeping and incorporation for BC RMTs, physiotherapists, counsellors and clinic owners.")


def blog_post(p):
    more = [o for o in POSTS if o is not p]
    body = p["body"]
    if p.get("guide_box"):
        body = body.replace("<!--GUIDE_BOX-->", f"""<aside class="guide-box"><span class="tag soon">Free Download</span>
<h3>Thinking About Incorporating? Read This First.</h3>
<p>Before you make the move, understand the five key things BC health and wellness practitioners should consider, including tax benefits, PSB risk, GST/HST, salary vs. dividends and professional requirements.</p>
<a class="btn btn-primary" href="{GUIDE}">{icon('download')} Download the Free Incorporation Guide</a></aside>""")
    when = ""
    if p.get("date"):
        when = f" | {p.get('date_label', 'Published')} {fmt_date(p['date'])}"
    schema = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"], "description": p["excerpt"],
              "author": {"@type": "Organization", "name": "YS Tax & Advisory"},
              "publisher": {"@type": "Organization", "name": "YS Tax & Advisory"},
              "image": SITE["domain"] + p["image"], "mainEntityOfPage": SITE["domain"] + post_url(p)}
    if p.get("date"):
        schema["dateModified"] = p["date"]
    main = f"""
<section class="page-hero"><div class="container container-narrow">
  <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><a href="/resources/">Resources</a><span aria-hidden="true">/</span><a href="/resources/blog/">Blog</a></nav>
  <div class="post-meta" style="margin-bottom:1.25rem"><span class="tag">{e(p['category'])}</span><span>{p['read']}</span></div>
  <h1 class="h1" style="font-size:clamp(2rem,3.4vw + .5rem,3rem)">{e(p['title'])}</h1>
  <p class="byline">By YS Tax &amp; Advisory{when}</p>
</div></section>
<article class="container container-narrow" style="padding-bottom:2rem">
  <div class="article-img"><img src="{p['image']}" alt="{e(p['image_alt'])}" width="2000" height="1414"></div>
  <div class="prose">{body}</div>
  <p class="disclaimer">This article is general information only and is not professional tax, accounting or legal advice. Tax rules change; please contact us for guidance specific to your practice.</p>
  <div class="post-cta reveal"><h2>{e(p.get('cta_h2') or DEFAULT_POST_CTA[0])}</h2>{p.get('cta_body') or DEFAULT_POST_CTA[1]}
    <div class="actions">{btn_call()}</div><p class="small">Free, no obligation · Based in Delta, BC · Virtual across Canada</p></div>
</article>
<section class="section"><div class="container">
  {section_head('Keep reading', 'More from the blog')}
  <div class="grid grid-2" style="max-width:56rem;margin:0 auto">{''.join(post_card(o) for o in more)}</div>
</div></section>"""
    return dict(path=p["path"], active="resources", main=main, title=p["seo_title"], description=p["excerpt"],
                extra_head=f'<meta property="og:type" content="article">\n<script type="application/ld+json">{json.dumps(schema)}</script>')


def useful_links():
    groups = "".join(f"""<div class="card reveal"><h2 class="h3">{e(g)}</h2><ul class="link-list">{''.join(
        f'<li><a href="{u}" target="_blank" rel="noopener">{icon("external")}<span>{e(n)}</span></a></li>' for n, u in links)}</ul></div>""" for g, links in USEFUL_LINKS)
    main = f"""
{page_hero(trail=[('Home', '/'), ('Resources', '/resources/'), ('Useful Links', None)], eyebrow='Useful links', center=True,
           title='Useful Tax &amp; Business Links',
           lead='Quick access to trusted government resources for Canadian tax rates, payroll contributions, business registration and other important information.', actions='')}
<section class="section-tight" style="padding-top:0"><div class="container"><div class="grid grid-2">{groups}</div>
  <p class="footnote center mt-3">These links open official government websites in a new tab.</p></div></section>
{cta_band()}"""
    return dict(path="resources/useful-links/index.html", active="resources", main=main,
                title="Useful Tax & Business Links in Canada | YS Tax & Advisory",
                description="Access official CRA and BC Government resources for personal and corporate tax rates, CPP, EI, PST, WorkSafeBC and business registration.")


AC_FORM_ID = 15
AC_EMBED = f'<div class="_form_{AC_FORM_ID}"></div><script src="https://priyankadhall.activehosted.com/f/embed.php?id={AC_FORM_ID}" charset="utf-8"></script>'


def incorporation_guide():
    learn = ["When incorporation makes sense", "Key tax and financial considerations", "Mistakes to avoid"]
    main = f"""
<section class="page-hero"><div class="container"><div class="split" style="align-items:start">
  <div>
    <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><a href="/resources/">Resources</a><span aria-hidden="true">/</span><span>Incorporation Guide</span></nav>
    {badge('Free guide', upper=True)}
    <h1 class="h1">Thinking About Incorporating Your Practice?</h1>
    <p class="guide-sub">Free Guide for BC Health &amp; Wellness Practitioners</p>
    <p class="lead">5 practical checks to help you make a more informed decision.</p>
    <h2 class="h3 mt-4" style="margin-bottom:1rem">What You'll Learn</h2>
    {list_check([e(x) for x in learn])}
    <div class="hero-foot" style="border:0;padding-top:0">{icon('shield')}<span>Written for RMTs, physiotherapists, counsellors, naturopathic doctors, clinic owners and more.</span></div>
  </div>
  <div class="form-card ac-form-card reveal" id="get-guide">
    <!-- ActiveCampaign form {AC_FORM_ID}: fields, confirmation message and emails are managed in ActiveCampaign -->
    {AC_EMBED}
    <noscript><p>Please enable JavaScript to request the guide, or email <a href="mailto:{SITE['email']}">{SITE['email']}</a>.</p></noscript>
  </div>
</div></div></section>"""
    return dict(path="resources/incorporation-guide.html", active="resources", main=main,
                title="Free Incorporation Guide for BC Health Practitioners | YS Tax & Advisory",
                description="Thinking about incorporating your practice? Free guide for BC health & wellness practitioners: 5 practical checks, key tax considerations and mistakes to avoid.")


def incorporation_thanks():
    main = f"""
<section class="section"><div class="container container-narrow center">
  <div class="thanks-icon">{icon('mail')}</div>
  {badge('Check your inbox', upper=True)}
  <h1 class="h1">Thank you! Your guide is on its way.</h1>
  <p class="lead mt-2" style="max-width:36rem;margin-left:auto;margin-right:auto">We've emailed the Incorporation Guide for BC Health &amp; Wellness Practitioners to you. If it isn't there in a few minutes, check your spam or promotions folder.</p>
  <div class="actions" style="justify-content:center"><a class="btn btn-primary" href="/assets/incorporation-guide.pdf" download>{icon('download')} Download now</a><a class="btn btn-outline" href="/resources/blog/">Browse the blog</a></div>
</div></section>
<section class="section-tight"><div class="container">
  <div class="inline-cta"><div><h3>Want to know if incorporating makes sense for you?</h3><p>Book a free consultation and we'll run the numbers with your actual income.</p></div>{btn_call(cls="btn btn-light")}</div>
</div></section>
<section class="section"><div class="container">
  {section_head('While you wait', 'Recommended reading')}
  <div class="grid grid-3">{''.join(post_card(p) for p in POSTS)}</div>
</div></section>"""
    return dict(path="resources/incorporation-guide-thank-you.html", active="resources", main=main,
                title="Thank You | Incorporation Guide | YS Tax & Advisory",
                description="Your free Incorporation Guide for BC Health Practitioners is on its way.")


# ======================================================================= CONTACT
def contact():
    profs = "".join(f"<option>{e(p['title'])}</option>" for p in PROFESSIONS[:-1]) + "<option>Other health practitioner</option>" + \
        "".join(f"<option>{e(i['name'])}</option>" for i in INDUSTRIES) + "<option>Other</option>"
    svc_opts = "".join(f"<option>{e(s['name'])}</option>" for s in SERVICES) + "<option>Not sure yet</option>"
    main = f"""
{page_hero(trail=[('Home', '/'), ('Contact Us', None)], eyebrow='Contact us', center=True,
           title="Let’s talk about your business",
           lead="Fill out the short form and we'll reach out within 1 to 2 business days.", actions='')}
<section class="section-tight" style="padding-top:0"><div class="container"><div class="split" style="align-items:start">
  <div class="form-card reveal">
    <form class="form-grid" method="post" action="/forms/send" data-endpoint="/forms/send" novalidate>
      <input type="hidden" name="form" value="contact"><div class="hp" aria-hidden="true"><label>Leave this empty<input name="website" tabindex="-1" autocomplete="off" maxlength="{FORM_LIMITS['website']}"></label></div>
      <div class="two"><div class="field"><label for="c-first">First name</label><input id="c-first" name="first_name" maxlength="{FORM_LIMITS['first_name']}" autocomplete="given-name" required></div>
      <div class="field"><label for="c-last">Last name</label><input id="c-last" name="last_name" maxlength="{FORM_LIMITS['last_name']}" autocomplete="family-name" required></div></div>
      <div class="two"><div class="field"><label for="c-email">Email</label><input id="c-email" type="email" name="email" maxlength="{FORM_LIMITS['email']}" autocomplete="email" inputmode="email" data-validate="email" placeholder="name@example.com" aria-describedby="c-email-err" required><p class="field-error" id="c-email-err" aria-live="polite"></p></div>
      <div class="field"><label for="c-phone">Phone</label><input id="c-phone" type="tel" name="phone" maxlength="{FORM_LIMITS['phone']}" autocomplete="tel" inputmode="tel" data-validate="phone" placeholder="604-555-1234" aria-describedby="c-phone-err" required><p class="field-error" id="c-phone-err" aria-live="polite"></p></div></div>
      <div class="two"><div class="field"><label for="c-prof">Profession / industry</label><select id="c-prof" name="profession" required><option value="">Select one</option>{profs}</select></div>
      <div class="field"><label for="c-svc">What do you need help with?</label><select id="c-svc" name="service"><option value="">Select one</option>{svc_opts}</select></div></div>
      <div class="field"><label for="c-msg">Tell us a little about your needs (optional)</label><textarea id="c-msg" name="message" maxlength="{FORM_LIMITS['message']}" placeholder="e.g. I'm an RMT working at two clinics and thinking about incorporating..."></textarea></div>
      <label class="consent"><input type="checkbox" name="consent" required><span>I agree to be contacted by YS Tax &amp; Advisory about my enquiry.</span></label>
      <button class="btn btn-primary btn-block" type="submit">Send message {icon('arrow')}</button>
    </form>
    <div class="form-success"><div class="thanks-icon">{icon('check')}</div><h2 class="h3" style="font-size:1.5rem">Thank You for Reaching Out!</h2><p class="muted mt-1">We've received your message. Our team will review your inquiry and get back to you within 1 - 2 business days.</p></div>
  </div>
  <div class="stack">
    <div class="card card-feature reveal"><h3>Contact details</h3><ul class="f-links contact-list">
      <li>{icon('pin')}<span>{e(SITE['location'])}</span></li>
      <li>{icon('phone')}<a href="tel:{SITE['phone_href']}">{e(SITE['phone'])}</a></li>
      <li>{icon('mail')}<a href="mailto:{SITE['email']}">{e(SITE['email'])}</a></li>
      <li>{icon('clock')}<span>{e(SITE['hours'])}</span></li></ul></div>
    <div class="card reveal"><h3>What Happens Next?</h3>{list_check(['We review your inquiry.', 'We get back to you within 1- 2 business days.', 'We discuss your needs and recommend the right next step.'])}</div>
  </div>
</div></div></section>"""
    return dict(path="contact.html", active="contact", main=main,
                title="Contact Us | YS Tax & Advisory",
                description="Contact YS Tax & Advisory in Delta, BC. Accounting, tax and advisory for health & wellness practitioners and businesses, virtual across Canada.")


LEGAL_DIR = Path(__file__).parent / "legal"


def legal_page(slug, title, subtitle, description):
    body = (LEGAL_DIR / f"{slug}.html").read_text(encoding="utf-8")
    main = f"""
<section class="page-hero"><div class="container container-narrow">
  <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><span>{e(title)}</span></nav>
  <h1 class="h1">{e(title)}</h1>
  <p class="lead">{e(subtitle)}</p>
</div></section>
<article class="container container-narrow legal-page"><div class="prose">{body}</div></article>"""
    return dict(path=f"{slug}.html", active="", main=main, title=f"{title} | YS Tax & Advisory", description=description)


DEFAULT_POST_CTA = (
    "Have a question about your own situation?",
    "<p>At YS Tax &amp; Advisory, we help BC health and wellness practitioners and businesses across Canada with bookkeeping, tax and advisory. Tell us a little about your situation and we'll explain your options in plain English.</p>",
)


def all_pages():
    global POSTS
    POSTS = published_posts()
    return [home(), serve_index(), *[profession(p) for p in PROFESSIONS], other_industries(),
            services_index(), *[service(s) for s in SERVICES], pricing(), refer(), our_story(),
            resources_index(), blog_index(), *[blog_post(p) for p in POSTS], useful_links(),
            incorporation_guide(), incorporation_thanks(), contact(),
            legal_page("privacy-policy", "Privacy Policy", "How YS Tax & Advisory Ltd. collects, uses and protects your personal information.",
                       "How YS Tax & Advisory Ltd. collects, uses and protects personal information, under PIPEDA, BC PIPA and CASL."),
            legal_page("terms-of-service", "Terms of Service", "YS Customer Terms",
                       "The customer terms that govern services provided by YS Tax & Advisory Ltd.")]
