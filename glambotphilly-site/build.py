#!/usr/bin/env python3
"""Static site generator for glambotphilly.com.

Every page is assembled from the shared pieces below so the header, footer,
schema markup and inquiry form stay identical across the site.

    python3 build.py            -> writes dist/ (deployable site)
    python3 build.py --artifact -> also writes artifact/ (preview build where
                                   index.html has no document wrapper)

Edit CONFIG first: prices, contact details and the form endpoint live there.
"""
import html
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
DIST = ROOT / "dist"

CONFIG = {
    "site_name": "GlamBot Philly",
    "brand_line": "The Philly Glam Experience",
    "domain": "https://www.glambotphilly.com",
    "email": "hello@glambotphilly.com",
    "phone": "(267) 888-GLAM",  # shown on the page; leave empty to hide phone everywhere
    "phone_digits": "(267) 888-4526",
    "phone_e164": "+12678884526",
    # Where the inquiry form POSTs (Formspree, Basin, a Rally/Tally webhook...).
    # Empty = the form shows a "not connected yet" message with the email.
    "form_endpoint": "",
    "price_from": "$2,995",
    "price_from_number": "2995",
    "package_hours": "3 hours",
    "extra_30": "$500",
    "extra_60": "$1,000",
    "addon_tv": "$250",
    "addon_branding": "$400",
    "addon_overlay": "from $250",
    "addon_backdrop": "Quoted per design",
    "travel_base": "Norristown, PA",
    "travel_radius": "40 miles",
    "travel_fee": "$100 per additional 10 miles",
}

C = CONFIG
FONTS = ("https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400..600;"
         "1,6..96,400..600&family=DM+Mono:wght@400&family=Jost:wght@300;400;500&display=swap")

EVENTS = [
    # slug, nav label, card eyebrow, card title, card blurb, form value
    ("wedding-glambot-philadelphia", "Weddings", "Weddings", "Wedding GlamBot",
     "A red carpet moment for the couple, the wedding party and every guest. The clip everyone sends to the group chat.", "Wedding"),
    ("gala-fundraiser-glambot", "Galas & Fundraisers", "Galas & benefits", "Gala & Fundraiser GlamBot",
     "Black-tie arrivals filmed like a premiere, with your sponsors on every video that gets shared.", "Gala / Fundraiser"),
    ("corporate-event-glambot", "Corporate & Brand Activations", "Corporate", "Brand Activations",
     "Branded slow-motion content for launches, conferences and client nights. Your logo travels with every share.", "Corporate / Brand activation"),
    ("holiday-party-glambot", "Holiday Parties", "Holiday season", "Holiday Party GlamBot",
     "Give the office party a red carpet. The one part of the night everyone actually lines up for.", "Holiday party"),
    ("bar-bat-mitzvah-glambot", "Bar & Bat Mitzvahs", "Mitzvahs", "Bar & Bat Mitzvah GlamBot",
     "Teens go all in for the camera. Grandparents too. A mitzvah moment nobody else at school has had.", "Bar / Bat Mitzvah"),
    ("prom-sweet-16-quinceanera-glambot", "Proms, Sweet 16s & Quinces", "Proms & milestones", "Proms, Sweet 16s & Quinces",
     "The grand entrance, filmed in slow motion. Built for proms, formals, sweet 16s and quinceañeras.", "Prom / Formal / Sweet 16 / Quinceañera"),
]
FORM_EVENT_TYPES = [e[5] for e in EVENTS] + ["Birthday / Private party", "Other"]

AREAS = {
    "Philadelphia": ["Center City", "Rittenhouse", "Old City", "Fishtown & Northern Liberties", "Manayunk", "University City", "Navy Yard"],
    "Montgomery County & Main Line": ["Norristown", "King of Prussia", "Blue Bell", "Ambler", "Bryn Mawr & Villanova", "Ardmore & Merion", "Glenside & Jenkintown"],
    "Bucks County": ["Doylestown", "Newtown", "New Hope", "Bensalem", "Yardley", "Warminster"],
    "Chester & Delaware Counties": ["West Chester", "Malvern & Paoli", "Media", "Newtown Square", "Radnor & Wayne"],
    "South Jersey & Delaware": ["Cherry Hill", "Mount Laurel", "Moorestown", "Haddonfield & Collingswood", "Wilmington, DE"],
}


def e(s):
    return html.escape(s, quote=True)


def url(slug):
    return f"{C['domain']}/" if slug == "index" else f"{C['domain']}/{slug}"


# --------------------------------------------------------------------------
# shared pieces
# --------------------------------------------------------------------------

def head(title, desc, slug, schema, og_image="media/bride.jpg"):
    blocks = "\n".join(
        f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in schema)
    return f"""<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url(slug)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(C['site_name'])}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url(slug)}">
<meta property="og:image" content="{C['domain']}/{og_image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0f0b0a">
<link rel="icon" type="image/png" href="media/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="assets/site.css">
{blocks}"""


def nav_links(current):
    def a(slug, label):
        cur = ' aria-current="page"' if slug == current else ""
        return f'<a href="{slug}.html"{cur}>{label}</a>'
    events = "".join(a(s, label) for s, label, *_ in EVENTS)
    phone_link = (f'<a class="nav-phone" href="tel:{C["phone_e164"]}">{e(C["phone"])}</a>' if C["phone"] else "")
    return f"""<nav class="nav" aria-label="Main">
  <details class="dropdown"><summary>Events</summary><div class="dropdown-panel">{events}</div></details>
  {a('glambot-pricing', 'Pricing')}
  {a('glambot-vs-360-photo-booth', 'GlamBot vs 360')}
  {a('faq', 'FAQ')}
  {a('service-area', 'Service Area')}
  {phone_link}<a class="btn btn-gold" href="book.html">Check your date</a>
</nav>"""


def header(current):
    nav = nav_links(current)
    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="index.html" aria-label="{e(C['site_name'])} home">
      <img src="media/logo.png" alt="" width="46" height="46">
      <span>{e(C['site_name'])}<small>{e(C['brand_line'])}</small></span>
    </a>
    <div class="header-nav">{nav}</div>
    <details class="menu-toggle"><summary aria-label="Open menu">Menu</summary>{nav}</details>
  </div>
</header>"""


def contact_lines():
    phone = (f'<div><span>Call or text</span><a href="tel:{C["phone_e164"]}">{e(C["phone"])} ({e(C["phone_digits"][-4:])})</a></div>' if C["phone"] else "")
    return f"""<div class="contact-lines">
  <div><span>Email</span><a href="mailto:{C['email']}">{C['email']}</a></div>
  {phone}
  <div><span>Based in</span><b>Montgomery County, PA. Serving Philadelphia, the Main Line, Bucks County and South Jersey.</b></div>
</div>"""


def footer():
    events = "".join(f'<li><a href="{s}.html">{label}</a></li>' for s, label, *_ in EVENTS)
    phone = f'<p><a href="tel:{C["phone_e164"]}">{e(C["phone"])} ({e(C["phone_digits"][-4:])})</a></p>' if C["phone"] else ""
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div class="stack">
        <a class="brand" href="index.html"><img src="media/logo.png" alt="" width="46" height="46"><span>{e(C['site_name'])}<small>{e(C['brand_line'])}</small></span></a>
        <p>Robotic slow-motion red carpet video for weddings, galas, mitzvahs and brand events across Greater Philadelphia.</p>
        <p><a href="mailto:{C['email']}">{C['email']}</a></p>{phone}
      </div>
      <div><h3>Events</h3><ul>{events}</ul></div>
      <div><h3>Planning</h3><ul>
        <li><a href="glambot-pricing.html">Pricing & packages</a></li>
        <li><a href="glambot-vs-360-photo-booth.html">GlamBot vs 360 booth</a></li>
        <li><a href="faq.html">FAQ</a></li>
        <li><a href="dj-planner-partners.html">DJs & planners</a></li>
        <li><a href="book.html">Check your date</a></li>
      </ul></div>
      <div><h3>Service area</h3><ul>
        <li><a href="service-area.html#philadelphia">Philadelphia</a></li>
        <li><a href="service-area.html#main-line">Main Line & Montgomery County</a></li>
        <li><a href="service-area.html#bucks">Bucks County</a></li>
        <li><a href="service-area.html#chester-delco">Chester & Delaware Counties</a></li>
        <li><a href="service-area.html#south-jersey">South Jersey & Wilmington</a></li>
      </ul></div>
    </div>
    <div class="footer-base"><span>© 2026 {e(C['site_name'])}. A PA Fun Company experience.</span><span>Staffed by our own director and host at every event.</span></div>
  </div>
</footer>
<script src="assets/site.js" defer></script>"""


def inquiry_form(preset="", heading="Check your date", sub=None):
    sub = sub or "Tell us about the night. We reply with availability and a quote, usually the same day."
    opts = "".join(
        f'<option{" selected" if t == preset else ""}>{e(t)}</option>' for t in FORM_EVENT_TYPES)
    return f"""<section class="section" id="book">
  <div class="wrap book">
    <div class="stack">
      <p class="eyebrow">Availability</p>
      <h2>{heading}</h2>
      <p class="muted">{sub}</p>
      {contact_lines()}
    </div>
    <form class="inquiry" data-endpoint="{e(C['form_endpoint'])}" novalidate>
      <div class="field"><label for="f-name">Your name</label><input id="f-name" name="name" autocomplete="name" required></div>
      <div class="field"><label for="f-email">Email</label><input id="f-email" name="email" type="email" autocomplete="email" required></div>
      <div class="field"><label for="f-phone">Phone</label><input id="f-phone" name="phone" type="tel" autocomplete="tel"></div>
      <div class="field"><label for="f-date">Event date</label><input id="f-date" name="event_date" type="date" required></div>
      <div class="field"><label for="f-type">Event type</label><select id="f-type" name="event_type">{opts}</select></div>
      <div class="field"><label for="f-guests">Guest count</label><input id="f-guests" name="guests" inputmode="numeric" placeholder="e.g. 180"></div>
      <div class="field full"><label for="f-venue">Venue & town</label><input id="f-venue" name="venue" placeholder="e.g. Union Trust, Philadelphia"></div>
      <div class="field full"><label for="f-msg">Anything we should know?</label><textarea id="f-msg" name="message" placeholder="Timeline, branding ideas, where you picture the carpet..."></textarea></div>
      <button class="btn btn-gold" type="submit">Send my date</button>
      <p class="form-note">No obligation. We never share your details.</p>
      <p class="form-status" role="status" hidden></p>
    </form>
  </div>
</section>"""


def cta_band(text="Your guests have done the 360. They've never been filmed by a robot.", button="Check your date"):
    return f"""<section class="cta-band"><div class="wrap">
  <h2>{text}</h2>
  <div class="actions"><a class="btn btn-gold" href="book.html">{button}</a><a class="btn btn-ghost" href="glambot-pricing.html">See pricing</a></div>
</div></section>"""


def faq_html(items):
    out = []
    for q, a in items:
        out.append(f"<details><summary>{e(q)}</summary><div class=\"answer\">{a}</div></details>")
    return f'<div class="faq">{"".join(out)}</div>'


def faq_schema(items):
    import re
    def plain(s):
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()
    return {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": html.unescape(plain(a))}} for q, a in items],
    }


def breadcrumb_schema(trail):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": name, "item": url(slug)} for i, (slug, name) in enumerate(trail)]}


def crumbs(trail):
    parts = []
    for i, (slug, name) in enumerate(trail):
        if i == len(trail) - 1:
            parts.append(f'<span aria-current="page">{e(name)}</span>')
        else:
            parts.append(f'<a href="{slug}.html">{e(name)}</a><span aria-hidden="true">/</span>')
    return f'<nav class="crumbs" aria-label="Breadcrumb">{"".join(parts)}</nav>'


BUSINESS = {
    "@context": "https://schema.org",
    "@type": "EntertainmentBusiness",
    "@id": f"{C['domain']}/#business",
    "name": C["site_name"],
    "alternateName": C["brand_line"],
    "url": f"{C['domain']}/",
    "logo": f"{C['domain']}/media/logo.png",
    "image": f"{C['domain']}/media/bride.jpg",
    "email": C["email"],
    "description": "Robotic slow-motion red carpet video experience for weddings, galas, corporate events, mitzvahs and proms in Greater Philadelphia.",
    "priceRange": f"From {C['price_from']}",
    "address": {"@type": "PostalAddress", "addressLocality": "Norristown", "addressRegion": "PA", "addressCountry": "US"},
    "areaServed": ["Philadelphia, PA", "Montgomery County, PA", "Bucks County, PA", "Chester County, PA",
                   "Delaware County, PA", "Main Line, PA", "South Jersey, NJ", "Wilmington, DE"],
    "parentOrganization": {"@type": "Organization", "name": "PA Fun Company"},
}
if C["phone"]:
    BUSINESS["telephone"] = C["phone_e164"]


def service_schema(name, desc, slug):
    return {
        "@context": "https://schema.org", "@type": "Service", "name": name, "description": desc,
        "serviceType": "Robotic slow-motion video booth (GlamBot)", "url": url(slug),
        "provider": {"@id": f"{C['domain']}/#business"},
        "areaServed": "Greater Philadelphia",
        "offers": {"@type": "Offer", "priceCurrency": "USD", "price": C["price_from_number"],
                   "description": f"GlamBot experience, {C['package_hours']}"},
    }


def reel(src, poster, tag, caption, alt):
    return f"""<figure class="reel">
  <div class="reel-frame"><video src="media/{src}" poster="media/{poster}" autoplay muted loop playsinline preload="metadata" aria-label="{e(alt)}"></video><span class="reel-tag">{e(tag)}</span></div>
  <figcaption>{caption}</figcaption>
</figure>"""


def page(slug, title, desc, body, schema, current=None):
    return {"slug": slug, "head": head(title, desc, slug, schema), "body": header(current or slug) + body + footer()}


# --------------------------------------------------------------------------
# shared content blocks
# --------------------------------------------------------------------------

INCLUDED = [
    ("On-site director & host", "2 crew"),
    ("Slow-motion videos", "Unlimited"),
    ("Your logo on every video", "Included"),
    ("Instant text & email delivery", "On the spot"),
    ("Red carpet", "4′ × 12′"),
    ("LED video lighting", "Pro set"),
    ("Online video gallery", "Included"),
    ("Delivery, setup & takedown", "Included"),
]
VENUE_NEEDS = [
    ("Floor space", "12′ W × 12′ D"),
    ("Ceiling height", "10′ min"),
    ("Surface", "Hard floor only"),
    ("Power", "110V dedicated outlet"),
    ("Load-in", "Drive-up within 150′"),
    ("Internet", "For instant sharing"),
]


def callsheet(title, right, rows):
    r = "".join(f'<div class="row"><dt>{e(a)}</dt><dd>{e(b)}</dd></div>' for a, b in rows)
    return f'<div class="callsheet"><header><span>{e(title)}</span><span>{e(right)}</span></header><dl>{r}</dl></div>'


STEPS = [
    ("Hit your mark", "Guests step onto the red carpet. Our host lines up singles, couples and groups so the line keeps moving."),
    ("Get directed", "The director calls the pose: a hair flip, a dip, a jacket toss, a champagne cheers. Nobody has to know what to do."),
    ("The arm sweeps", "The robotic arm swings the camera around them in one smooth move, under real video lighting."),
    ("Watch it land", "The finished slow-motion clip, with your logo on it, goes straight to their phone by text or email."),
]


def steps_html():
    return '<div class="steps">' + "".join(
        f'<div class="step"><span class="num">STEP {i + 1}</span><h3>{e(t)}</h3><p>{e(d)}</p></div>'
        for i, (t, d) in enumerate(STEPS)) + "</div>"


def events_grid(exclude=None):
    cards = []
    for slug, _label, eyebrow, title, blurb, _ in EVENTS:
        if slug == exclude:
            continue
        cards.append(f'<a class="event-card" href="{slug}.html"><span class="eyebrow">{e(eyebrow)}</span>'
                     f'<h3>{e(title)}</h3><p>{e(blurb)}</p><span class="go">See how it works</span></a>')
    return '<div class="events">' + "".join(cards) + "</div>"


COMPARE_ROWS = [
    ("The camera", "A real robotic arm sweeps a pro camera around the guest", "A phone or small camera on a spinning arm"),
    ("Where guests stand", "On the floor, on a red carpet", "On a raised spinning platform"),
    ("The look", "Cinematic slow motion under LED video lighting, like a premiere", "A fast spin, usually with ring lights"),
    ("Who runs it", "A director who poses every guest, plus a host", "Usually one attendant"),
    ("Best for", "Grand entrances, black tie, brands, the hero moment of the night", "Dance-floor energy, big goofy groups"),
    ("How new it feels", "Most guests have never done it", "Most guests have done one this year"),
]


def compare_table():
    rows = "".join(f'<tr><th scope="row">{e(a)}</th><td class="us">{e(b)}</td><td class="them">{e(c)}</td></tr>'
                   for a, b, c in COMPARE_ROWS)
    return f"""<div class="table-scroll"><table class="compare">
<thead><tr><th scope="col"></th><th scope="col" class="us">GlamBot</th><th scope="col">360 photo booth</th></tr></thead>
<tbody>{rows}</tbody></table></div>"""


# The 360 question appears on several pages; keep the wording in one place.
FAQ_360 = ("Is a GlamBot the same as a 360 photo booth?",
           "<p>No. A 360 booth puts guests on a raised platform while a phone or small camera spins around them. A GlamBot is a robotic camera arm, the kind made famous on Hollywood red carpets. Guests stand on the floor, our director poses them, and the arm makes one smooth cinematic sweep that plays back in slow motion.</p>"
           "<p>360 booths had a great run, and now they show up at nearly every party. If you want the moment people haven't seen yet, that's the GlamBot. <a href=\"glambot-vs-360-photo-booth.html\">Here's the full comparison</a>.</p>")

FAQ_CORE = [
    ("What is a GlamBot?",
     "<p>A GlamBot is a robotic camera arm that sweeps around a guest and films a few seconds of motion, played back in dramatic slow motion. It's the same style of shot you've seen from red carpets at the Oscars, the Met Gala and the Grammys. We bring that setup to your event with a red carpet, pro lighting, a director and a host.</p>"),
    FAQ_360,
    ("How do guests get their videos?",
     "<p>Right away. Each clip is texted or emailed to the guest on the spot, so they can post it before they're back at their table. Every video also lands in an online gallery you can share after the event. Instant sharing needs an internet connection at the venue; we'll ask about Wi-Fi when we plan.</p>"),
    ("How much space and power do you need?",
     f"<p>A <strong>12′ wide × 12′ deep</strong> area with at least <strong>10′ of ceiling height</strong>, on a hard surface (no grass, dirt or sand). We need a standard <strong>110V dedicated outlet</strong>, and drive-up access within about 150′ of the setup spot. No outlet nearby? Battery power is available.</p>"),
    ("How much does a GlamBot cost?",
     f"<p>Packages start at <strong>{C['price_from']}</strong> for {C['package_hours']}, and that includes the director, host, red carpet, lighting, unlimited videos, your logo on every clip, instant sharing, the online gallery and delivery within {C['travel_radius']} of {C['travel_base']}. <a href=\"glambot-pricing.html\">See packages and add-ons</a>.</p>"),
]

# --------------------------------------------------------------------------
# pages
# --------------------------------------------------------------------------
PAGES = []

# ---- Home ----------------------------------------------------------------
home_faq = FAQ_CORE
home_body = f"""
<main id="main">
<section class="hero">
  <div class="wrap hero-grid">
    <div>
      <h1><span class="eyebrow" style="display:block;margin-bottom:18px">Philadelphia GlamBot rental</span>Give every guest a <em class="slow">red carpet</em> moment.</h1>
      <p class="lede">A robotic camera arm sweeps around your guests and films cinematic slow-motion video that lands on their phone in seconds. For weddings, galas, mitzvahs and brand events across Philadelphia, the Main Line, Bucks County and South Jersey.</p>
      <div class="actions"><a class="btn btn-gold" href="book.html">Check your date</a><a class="btn btn-ghost" href="#how">See how it works</a></div>
      <p class="hero-meta"><span><b>From {C['price_from']}</b> · {C['package_hours']}</span><span><b>Unlimited</b> videos</span><span><b>Director + host</b> on site</span></p>
    </div>
    {reel("bride.mp4", "bride.jpg", "Slow motion", "A real guest clip from one of our wedding events, with the logo watermark every client gets.", "Slow-motion GlamBot video of a bride laughing on the red carpet")}
  </div>
  <div class="carpet-band" aria-hidden="true"><div class="carpet"></div><div class="wrap"><span>4′ × 12′ red carpet</span><span>LED video lighting</span><span>Included in every booking</span></div></div>
</section>

<section class="proof"><div class="wrap">
  <span class="eyebrow">Recently on our carpet</span>
  <span class="venue">Fabrika</span><span class="venue">Monaco Philadelphia</span><span class="venue">Haverford College</span><span class="venue">Bridal showers, proms & private parties</span>
</div></section>

<section class="section"><div class="wrap split">
  <div class="stack">
    <p class="eyebrow">What is a GlamBot?</p>
    <h2>The red carpet camera, <em>at your event</em>.</h2>
    <p class="muted">You've seen the shot. A star turns, the camera swings around them, and every hair and sequin moves in slow motion. That's a GlamBot: a robotic camera arm built to make anyone look like they're arriving at a premiere.</p>
    <p class="muted">We're Philadelphia's dedicated GlamBot crew. We roll out the red carpet, light it like a film set, and a director poses every guest so even the shy ones end up with a clip they want to post. It's a real robotic arm, not a spinning platform with a phone on it.</p>
    <div class="actions"><a class="btn btn-ghost" href="glambot-vs-360-photo-booth.html">How it compares to a 360 booth</a></div>
  </div>
  <div class="duo">
    <div class="reel-frame"><img src="media/robot-arm.jpg" alt="The GlamBot robotic camera arm beside a red carpet" loading="lazy"><span class="reel-tag">The robot</span></div>
    <div class="reel-frame"><video src="media/hero-couple.mp4" poster="media/hero-couple.jpg" autoplay muted loop playsinline preload="none" aria-label="Couple dancing in a slow-motion GlamBot clip"></video><span class="reel-tag">Slow motion</span></div>
  </div>
</div></section>

<section class="section" id="how"><div class="wrap">
  <div class="section-head"><p class="eyebrow">How it works</p><h2>Carpet to camera roll in under a minute.</h2></div>
  {steps_html()}
</div></section>

<section class="section"><div class="wrap">
  <div class="section-head"><p class="eyebrow">Made for the big nights</p><h2>Pick your event.</h2><p class="muted">Every crowd uses the carpet differently. Here's how we run it for each one.</p></div>
  {events_grid()}
</div></section>

<section class="section"><div class="wrap stack-lg">
  <div class="stack" style="max-width:760px">
    <p class="eyebrow">GlamBot vs 360 booth</p>
    <h2>360 booths are everywhere. <em>This isn't.</em></h2>
    <p class="muted">The 360 booth was the hit of a few years ago, and now it's at every sweet 16, office party and wedding in the area. Plenty of 360 companies even call their spinner a "glambot." Ours is the real thing: a robotic arm, pro lighting and a director.</p>
    <div class="actions"><a class="btn btn-ghost" href="glambot-vs-360-photo-booth.html">Read the full comparison</a></div>
  </div>
  {compare_table()}
</div></section>

<section class="section"><div class="wrap split">
  {callsheet("Every booking includes", "From " + C['price_from'], INCLUDED)}
  <div class="stack">
    <p class="eyebrow">Pricing, out in the open</p>
    <h2>One package. <em>Everything</em> included.</h2>
    <p class="muted">Most GlamBot companies make you fill out a form to see a number. Ours starts at <strong>{C['price_from']}</strong> for {C['package_hours']}, with the crew, carpet, lighting and unlimited videos built in. Add a live TV display, custom branding or a custom backdrop if you want them.</p>
    <div class="actions"><a class="btn btn-gold" href="glambot-pricing.html">See pricing & add-ons</a></div>
  </div>
</div></section>

<section class="section"><div class="wrap split flip">
  {callsheet("Venue checklist", "Send to your coordinator", VENUE_NEEDS)}
  <div class="stack">
    <p class="eyebrow">For planners & venues</p>
    <h2>Fits in a 12′ square.</h2>
    <p class="muted">We need a hard floor, one dedicated outlet and a place to pull the van up. We arrive early, set up before guests walk in, and pack out without getting in the way of your breakdown. Travel is included within {C['travel_radius']} of {C['travel_base']}.</p>
    <div class="actions"><a class="btn btn-ghost" href="service-area.html">See our service area</a></div>
  </div>
</div></section>

<section class="section"><div class="wrap">
  <div class="section-head"><p class="eyebrow">Questions</p><h2>The short answers.</h2></div>
  {faq_html(home_faq)}
  <div class="actions" style="margin-top:28px"><a class="btn btn-ghost" href="faq.html">All FAQs</a></div>
</div></section>

{inquiry_form(heading="Is your date open?")}
</main>"""
PAGES.append(page(
    "index",
    "GlamBot Rental Philadelphia | Slow-Motion Red Carpet Video",
    f"Philadelphia's robotic slow-motion GlamBot for weddings, galas, mitzvahs and corporate events. Director, host, red carpet and unlimited videos from {C['price_from']}.",
    home_body,
    [BUSINESS, faq_schema(home_faq)],
))


# ---- Event pages ---------------------------------------------------------
def event_page(slug, *, title, desc, h1, lede, intro_h2, intro, timeline_h2, timeline, ideas_h2, ideas, notes_h2, notes,
               faq, media=("bride.mp4", "bride.jpg"), media_caption="", media_alt="", cta=None, extra=""):
    ev = next(x for x in EVENTS if x[0] == slug)
    label, form_value = ev[1], ev[5]
    trail = [("index", "Home"), (slug, label)]
    tl = "".join(f'<div class="moment"><span class="when">{e(w)}</span><h3>{e(t)}</h3><p>{e(d)}</p></div>' for w, t, d in timeline)
    idl = "".join(f"<li><b>{e(a)}</b><span>{e(b)}</span></li>" for a, b in ideas)
    notes_html = "".join(f"<p>{n}</p>" for n in notes)
    body = f"""
<main id="main">
<section class="page-hero"><div class="wrap split">
  <div>
    {crumbs(trail)}
    <h1>{h1}</h1>
    <p class="lede">{lede}</p>
    <div class="actions"><a class="btn btn-gold" href="#book">Check your date</a><a class="btn btn-ghost" href="glambot-pricing.html">From {C['price_from']}</a></div>
  </div>
  {reel(media[0], media[1], "Slow motion", media_caption, media_alt)}
</div></section>

<section class="section"><div class="wrap split">
  <div class="stack prose">
    <p class="eyebrow">Why it works</p>
    <h2>{intro_h2}</h2>
    {intro}
  </div>
  <div class="stack">
    <h2 style="font-size:var(--step-2)">{timeline_h2}</h2>
    <div class="timeline">{tl}</div>
  </div>
</div></section>
{extra}
<section class="section"><div class="wrap">
  <div class="section-head"><p class="eyebrow">Shot list</p><h2>{ideas_h2}</h2><p class="muted">Our director runs these on the night. You don't have to plan a thing.</p></div>
  <ul class="ideas">{idl}</ul>
</div></section>

<section class="section"><div class="wrap split">
  <div class="stack prose">
    <p class="eyebrow">Planning notes</p>
    <h2>{notes_h2}</h2>
    {notes_html}
  </div>
  {callsheet("Included", "From " + C['price_from'], INCLUDED)}
</div></section>

<section class="section"><div class="wrap">
  <div class="section-head"><p class="eyebrow">Questions</p><h2>{e(label)} FAQ</h2></div>
  {faq_html(faq)}
</div></section>

<section class="section"><div class="wrap">
  <div class="section-head"><p class="eyebrow">More events</p><h2>Other nights we bring the carpet to.</h2></div>
  {events_grid(exclude=slug)}
</div></section>

{inquiry_form(preset=form_value, heading=cta or "Check your date")}
</main>"""
    PAGES.append(page(slug, title, desc, body,
                      [BUSINESS, service_schema(f"{label} GlamBot", desc, slug), faq_schema(faq), breadcrumb_schema(trail)]))


event_page(
    "wedding-glambot-philadelphia",
    title="Wedding GlamBot Philadelphia | Slow-Motion Red Carpet",
    desc=f"Add a robotic slow-motion GlamBot to your Philadelphia, Main Line or Bucks County wedding. Red carpet, director, host and unlimited videos from {C['price_from']}.",
    h1="Wedding <em>GlamBot</em> for Philadelphia weddings",
    lede="Your guests dressed up for this. Give them a red carpet and a robotic camera, and they'll send their slow-motion clip to everyone they know before dessert.",
    intro_h2="The wedding moment guests <em>actually post</em>.",
    intro="""<p>Most wedding entertainment is something guests watch. The GlamBot is something every guest gets to do. Grandma in her best dress, the college crew in a line, the flower girl spinning: each one walks off with a cinematic clip on their phone.</p>
<p>It also gives you a second highlight reel. Your photographer and videographer cover the day. The GlamBot covers <strong>every single guest</strong>, and it all lands in one online gallery you can keep.</p>
<p>We work around your timeline, your planner and your DJ. Most couples open the carpet at cocktail hour and keep it running into the reception.</p>""",
    timeline_h2="Where it fits in the day",
    timeline=[
        ("Before the ceremony", "Getting-ready glam", "Wedding party clips while hair and makeup are fresh. Perfect for the bridal party reveal post."),
        ("Cocktail hour", "Doors open on the carpet", "Guests head straight for it with a drink in hand. The best time to catch everyone looking sharp."),
        ("Reception", "After the first dance", "The couple's hero clip, then the carpet stays open between dance sets."),
        ("Late night", "Last call on the carpet", "Jackets off, sneakers on. The funniest clips of the night happen here."),
    ],
    ideas_h2="Wedding shots we love",
    ideas=[
        ("The veil toss", "Fabric floating in slow motion is the whole reason this camera exists."),
        ("The dip", "A classic for the couple and every couple who's been married 40 years."),
        ("Bridal party lineup", "Everyone in a row, one sweep, matching dresses mid-twirl."),
        ("Champagne cheers", "Bubbles and clinks, slowed down so you can see every drop."),
        ("Groomsmen jacket flip", "The shot the groomsmen will pretend they didn't rehearse."),
        ("Grandparents' moment", "The clip that ends up on the slideshow at the next anniversary."),
    ],
    notes_h2="What your venue needs to know",
    notes=[
        "We need a 12′ × 12′ spot on a hard floor with 10′ of height, one dedicated outlet and drive-up access. Ballrooms, barns with wood floors, tented terraces and patios all work. Grass lawns don't.",
        "Your logo watermark can be your monogram or wedding date. We'll match the colors to your invitation suite if you send it over.",
        "Weddings are where dates go first. If you already have your venue booked, it's worth checking our availability now.",
    ],
    faq=[
        ("When during the wedding should we have the GlamBot?",
         "<p>Cocktail hour into the reception is the sweet spot. Guests are fresh, dressed up and waiting for something to do. If you have a long reception, keep the carpet open between dance sets so the dance floor never empties all at once.</p>"),
        ("Will it get in the way of our photographer or videographer?",
         "<p>No. We stay in our 12′ square and work around them. Photographers usually love it, because guests are already posed and lit when they walk by.</p>"),
        ("Can the videos have our names or monogram?",
         "<p>Yes. Every video carries your logo watermark, and for weddings that's usually your monogram, names or date. Custom intro and outro overlays are available as an add-on.</p>"),
        FAQ_360,
        ("Does it work for an outdoor wedding?",
         "<p>It works outdoors on a hard, level surface like a patio, deck or tent floor, with power nearby. It can't sit on grass or be left in the rain, so we'll plan a covered spot with you.</p>"),
    ],
    media_caption="Real bride, real reception. Every clip carries your watermark.",
    media_alt="Slow-motion GlamBot clip of a bride laughing on the red carpet",
    cta="Check your wedding date",
)

event_page(
    "gala-fundraiser-glambot",
    title="Gala & Fundraiser GlamBot | Philadelphia Red Carpet Video",
    desc=f"Turn your Philadelphia gala arrivals into a red carpet premiere. Robotic slow-motion GlamBot with sponsor branding, director and host from {C['price_from']}.",
    h1="A red carpet arrival for your <em>gala</em>",
    lede="Black tie deserves better than a step-and-repeat and a phone. The GlamBot films every arriving guest like they're walking into a premiere, with your sponsors on every clip.",
    intro_h2="Give donors a reason to <em>post about your cause</em>.",
    intro="""<p>Galas live and die by the room's energy and the buzz afterward. A GlamBot at the entrance sets the tone the moment guests arrive, and every clip that gets shared carries your event name, your logo or your sponsor's.</p>
<p>That makes it more than entertainment. It's a <strong>sponsorship you can sell</strong>. "Red Carpet presented by" puts a sponsor's brand on hundreds of videos that travel well past the ballroom.</p>
<p>Our host keeps the line moving during arrivals, and the director makes sure the board chair and the honorees get their moment too.</p>""",
    timeline_h2="How the night runs",
    timeline=[
        ("Arrivals", "The premiere entrance", "Guests walk the carpet on the way in. The busiest, most dressed-up hour of the night."),
        ("Cocktail reception", "Honorees and VIPs", "Our host pulls honorees, sponsors and the board for their own clips."),
        ("Program", "Live on screen", "With the Live TV Display add-on, clips play near the bar while the program runs."),
        ("After-party", "Round two", "Once the speeches are done, the line comes back."),
    ],
    ideas_h2="Gala shots that land",
    ideas=[
        ("The gown turn", "A slow spin that shows the whole silhouette. The gala classic."),
        ("Tux & bow tie straighten", "One small move, filmed like a movie poster."),
        ("Honoree spotlight", "A solo sweep for every honoree to post the next morning."),
        ("Sponsor table group", "A thank-you clip for the people who bought the table."),
        ("Paddle raise", "Shot during the cocktail hour, played during the appeal."),
        ("Committee lineup", "The volunteers who planned it all, finally on the carpet themselves."),
    ],
    notes_h2="Notes for event chairs",
    notes=[
        "Branding: your logo watermark is included. The enhanced branding package adds custom colors and your event name to the download gallery and the text messages guests receive.",
        "Placement: the entrance or the cocktail-hour foyer works best. We need 12′ × 12′ of hard floor, 10′ of height and one dedicated outlet.",
        "Many Philadelphia galas fall on the same spring and fall weekends. Lock the date in once your venue is confirmed.",
    ],
    faq=[
        ("Can a sponsor's logo go on the videos?",
         "<p>Yes. The watermark on every clip can be your event logo, your sponsor's, or both. The enhanced branding package carries that branding through to the online gallery and the texts guests receive.</p>"),
        ("Will it slow down arrivals?",
         "<p>Our host manages the line and the director keeps each shot quick, so guests flow through. If your arrival window is tight, we'll place the carpet just past check-in so nobody backs up at the door.</p>"),
        ("Can you show the videos in the room?",
         f"<p>Yes. The Live TV Display add-on ({C['addon_tv']}) plays clips on a screen as they're made. It's a great way to fill the room during cocktails.</p>"),
        FAQ_360,
    ],
    media=("hero-couple.mp4", "hero-couple.jpg"),
    media_caption="One sweep of the arm, played back in slow motion.",
    media_alt="Couple dancing in a slow-motion GlamBot clip",
    cta="Check your gala date",
)

DEMO_STRIP = """<section class="section"><div class="wrap">
  <div class="section-head"><p class="eyebrow">At brand events</p><h2>Stadiums, rooftops, <em>product launches</em>.</h2><p class="muted">Stills from GlamBot activations: sponsor walls, fire performers, stadium concourses and rooftop parties. Your backdrop and logo go wherever the carpet goes.</p></div>
  <div class="demo-grid">""" + "".join(
    f'<img src="media/demo-{i}.jpg" alt="Guest posing for the GlamBot at a brand activation" loading="lazy" width="540" height="360">' for i in (2, 3, 4, 1, 6, 5)) + """</div>
</div></section>"""

event_page(
    "corporate-event-glambot",
    title="Brand Activation & Corporate Event GlamBot | Philadelphia",
    desc=f"Branded robotic slow-motion video for product launches, conferences, client events and brand activations in Philadelphia. Logo on every clip, from {C['price_from']}.",
    h1="Brand activations that people <em>line up</em> for",
    lede="A GlamBot turns your logo into content guests want to share. Product launches, conferences, client appreciation nights and employee events across Greater Philadelphia.",
    intro_h2="Your brand on <em>every share</em>.",
    intro="""<p>Most activations hand out swag that ends up in a drawer. A GlamBot hands out a video that ends up on Instagram, with your logo watermarked on it and your colors in the gallery and text message that delivers it.</p>
<p>It pulls people across a trade show floor, gives employees a reason to dress up for the company party, and makes a client night feel like an event instead of a dinner.</p>
<p>Our director and host are on site the whole time. Your team doesn't staff it, troubleshoot it or carry it.</p>""",
    timeline_h2="Where companies use it",
    timeline=[
        ("Product launch", "The reveal moment", "Guests pose with the product or in front of your branded backdrop."),
        ("Conference & trade show", "Booth traffic", "A line at your booth is the best ad on the floor."),
        ("Client appreciation", "VIP treatment", "Make your best clients feel like the stars of the night."),
        ("Employee events", "Culture you can post", "Holiday parties, awards nights and summer outings."),
    ],
    ideas_h2="Branded shots that work",
    ideas=[
        ("Product hero", "The guest, the product, one sweeping move."),
        ("Team lineup", "Departments, sales teams and award winners, filmed like a band."),
        ("Award winner walk", "Give your honorees a proper red carpet."),
        ("Mascot or swag toss", "Confetti, branded merch, a mascot cameo."),
        ("Executive cameo", "The CEO clip that gets shared internally for a month."),
        ("Custom backdrop", "Your brand wall behind every shot."),
    ],
    notes_h2="What marketing teams ask for",
    notes=[
        f"Branding options: logo watermark included; custom intro and outro overlays ({C['addon_overlay']}); enhanced branding of the gallery and text messages ({C['addon_branding']}); custom printed backdrop (quoted per design).",
        "Venue needs: 12′ × 12′ hard floor, 10′ height, one dedicated 110V outlet and internet for instant delivery. Convention centers and hotel ballrooms are easy.",
        "We can send a certificate of insurance and a W-9 to your venue or procurement team.",
    ],
    faq=[
        ("Can we put our branding on the videos and the delivery?",
         "<p>Yes. Your logo is on every video. With the enhanced branding package, the download gallery and the text message guests receive carry your colors and name too. Custom intro and outro overlays are available.</p>"),
        ("Do you work trade shows and conferences?",
         "<p>Yes, as long as there's a 12′ × 12′ footprint, 10′ of height and a dedicated outlet. Let us know your booth size and we'll tell you how it fits.</p>"),
        ("Can you provide a COI for our venue?",
         "<p>Yes. Send us the venue's requirements and we'll get a certificate of insurance over before the event.</p>"),
        FAQ_360,
    ],
    media_caption="Your logo rides along on every clip guests share.",
    media_alt="Slow-motion clip from a GlamBot event",
    cta="Plan your activation",
    extra=DEMO_STRIP,
)

event_page(
    "holiday-party-glambot",
    title="Holiday Party GlamBot | Philadelphia Office Party Idea",
    desc=f"The holiday party idea your team will talk about all year. Robotic slow-motion red carpet video for Philadelphia office and holiday parties from {C['price_from']}.",
    h1="The <em>holiday party</em> everyone dresses up for",
    lede="Give the office party a red carpet. Coworkers get a slow-motion clip, you get a team that finally wants to be in the photos, and December dates are going fast.",
    intro_h2="Holiday party entertainment that <em>isn't a raffle</em>.",
    intro="""<p>Every holiday party has the same problem: people stand around the bar waiting for something to happen. The GlamBot is the something. Teams line up together, the director gets them laughing, and the clips run in the company Slack for weeks.</p>
<p>It works for 40-person offices and 600-person ballroom parties alike, and it's just as good at a private New Year's Eve party.</p>
<p>December weekends fill first. If you've booked your venue, check your date with us now.</p>""",
    timeline_h2="How the party goes",
    timeline=[
        ("Arrivals", "Ugly sweaters or black tie", "Either way, everyone walks in past the carpet."),
        ("Cocktails", "Team by team", "Our host calls up departments so everybody gets a group clip."),
        ("Awards", "Winner walk", "Honorees get a solo red carpet moment."),
        ("Late night", "The fun clips", "Santa hats, confetti and the people who stayed for one more."),
    ],
    ideas_h2="Holiday shots",
    ideas=[
        ("Confetti or snow toss", "Slow motion was made for falling things."),
        ("Department lineup", "Accounting finally gets its moment."),
        ("The ugly sweater reveal", "A slow, dramatic unzip."),
        ("Champagne pop", "New Year's Eve in slow motion."),
        ("Boss & team", "The leadership clip that goes in the year-end recap."),
        ("Gift exchange chaos", "Wrapping paper mid-air."),
    ],
    notes_h2="Booking holiday season",
    notes=[
        "December Fridays and Saturdays go first. Thursday and weekday parties often have more flexibility.",
        "Branding the clips with your company logo is included. Add a holiday overlay or custom intro for a few dollars more.",
        "We need 12′ × 12′ of hard floor, 10′ of height and a dedicated outlet. Restaurant private rooms with low ceilings can be tight, so send us the space.",
    ],
    faq=[
        ("How far ahead should we book for December?",
         "<p>As soon as your venue is set. Holiday weekends book up first, and we only have so many crews.</p>"),
        ("Is it a good fit for a smaller office party?",
         f"<p>Yes. Everyone gets multiple turns, and the package price starts at {C['price_from']} for {C['package_hours']} no matter how many videos you make.</p>"),
        ("Can we use it for a New Year's Eve party?",
         "<p>Absolutely. Champagne and confetti are made for slow motion.</p>"),
        FAQ_360,
    ],
    media=("hero-couple.mp4", "hero-couple.jpg"),
    media_caption="Every guest leaves with a clip worth posting.",
    media_alt="Couple dancing in a slow-motion GlamBot clip",
    cta="Check your holiday date",
)

event_page(
    "bar-bat-mitzvah-glambot",
    title="Bar & Bat Mitzvah GlamBot | Philadelphia & Main Line",
    desc=f"The bar and bat mitzvah entertainment teens haven't seen at every party. Robotic slow-motion GlamBot for Philadelphia and Main Line mitzvahs from {C['price_from']}.",
    h1="The mitzvah moment <em>nobody else</em> has had",
    lede="By seventh grade, kids have done the 360 booth at every party. A real robotic camera arm and a red carpet is new, and it works just as well for the adults' table.",
    intro_h2="Teens go all in. <em>So do grandparents.</em>",
    intro="""<p>Bar and bat mitzvah guests span three generations, and the GlamBot is one of the few things all of them line up for. Teens bring the choreography. Adults bring the dip. Grandparents steal the show.</p>
<p>Our director keeps it fast and fun for the kids and makes the adults feel like celebrities. The mitzvah teen gets their own hero clip, and the family gets a gallery of everyone who celebrated.</p>
<p>We work hand in hand with your DJ or MC so the carpet opens and closes around the hora, candle lighting and the big dance sets.</p>""",
    timeline_h2="Where it fits in the party",
    timeline=[
        ("Cocktail hour", "Adults first", "Parents and grandparents get their moment while the kids are in their own room."),
        ("Kids' entrance", "The grand arrival", "Teens hit the carpet in groups. Instant clips mean instant posting."),
        ("Between dance sets", "Keep the floor fresh", "We open when the DJ takes a break, so nobody misses the party."),
        ("Late night", "Last looks", "Sneakers out, ties off, the best clips of the night."),
    ],
    ideas_h2="Mitzvah shots we run",
    ideas=[
        ("The guest of honor", "A solo hero clip for the mitzvah teen."),
        ("Friend squad", "Ten kids, one sweep, choreography rehearsed in the bathroom."),
        ("Parents' dip", "The one they'll pretend to be embarrassed about."),
        ("Grandparents' turn", "The clip that ends up as the family group chat profile picture."),
        ("Theme props", "Sports jerseys, a Broadway bow, whatever your theme is."),
        ("Siblings lineup", "The family shot that's actually fun."),
    ],
    notes_h2="Planning with your DJ and venue",
    notes=[
        "DJs and motivators love working with us. We stay out of the dance floor's way and take cues from your MC. DJs can also offer the GlamBot under their own brand; see our <a href=\"dj-planner-partners.html\">partner page</a>.",
        "Your logo watermark can be the mitzvah logo or monogram your designer already made.",
        "We need 12′ × 12′ of hard floor, 10′ of height and one dedicated outlet.",
    ],
    faq=[
        ("Is the GlamBot safe around a lot of kids?",
         "<p>Guests stand on the floor on our red carpet. There's no platform to step onto or fall off. The robotic arm runs on a set path, and our director controls it the whole time while our host manages the line.</p>"),
        ("Can we use the mitzvah logo on the videos?",
         "<p>Yes. Send us the logo or monogram from your invitations and it goes on every clip.</p>"),
        ("Will it pull kids off the dance floor?",
         "<p>We coordinate with your DJ so the carpet is busiest during cocktails and DJ breaks, not during the big sets.</p>"),
        FAQ_360,
    ],
    media_caption="Every guest, every age, gets their slow-motion moment.",
    media_alt="Slow-motion GlamBot clip",
    cta="Check your mitzvah date",
)

event_page(
    "prom-sweet-16-quinceanera-glambot",
    title="Prom, Sweet 16 & Quinceañera GlamBot | Philadelphia",
    desc=f"A red carpet grand entrance for proms, formals, sweet 16s and quinceañeras in Greater Philadelphia. Robotic slow-motion video with instant sharing from {C['price_from']}.",
    h1="The grand entrance, in <em>slow motion</em>",
    lede="Proms, college formals, sweet 16s and quinceañeras are all about the entrance. We give every guest a red carpet and a robotic camera to make it.",
    intro_h2="They spent months on the look. <em>Film it right.</em>",
    intro="""<p>The dress, the suit, the hair: for a prom or a quinceañera, the arrival is the main event. The GlamBot captures it the way red carpets do, then sends each clip straight to the guest's phone so it's posted before the first song.</p>
<p>We've run the carpet for high school proms and college formals, including Haverford College's drag ball. Schools like that the robot runs on a fixed path, our crew is on site the whole time, and nobody climbs onto a spinning platform.</p>
<p>For sweet 16s and quinces, the birthday star gets a solo hero clip, the court gets their lineup, and the family gets theirs.</p>""",
    timeline_h2="How the night flows",
    timeline=[
        ("Arrivals", "Red carpet entrance", "Every guest walks the carpet on the way in."),
        ("Court or crew", "Group clips", "Prom courts, quince courts and friend groups get their lineup."),
        ("Big reveal", "The star's moment", "Quinceañera, birthday girl or prom royalty gets a solo sweep."),
        ("Dance breaks", "Second round", "The line comes back once shoes come off."),
    ],
    ideas_h2="Entrance shots",
    ideas=[
        ("The gown twirl", "Full skirt, full spin, full slow motion."),
        ("Promposal pose", "Couples, best friends and the whole group chat."),
        ("Court lineup", "Damas and chambelanes in one sweep."),
        ("Tiara moment", "Quinceañera crown and shoe change, filmed like a coronation."),
        ("Hair flip", "Every prom's most requested shot."),
        ("Crown & sash", "Prom royalty gets the premiere treatment."),
    ],
    notes_h2="Notes for schools & families",
    notes=[
        "Schools and PTOs: we can provide a certificate of insurance and work with your chaperone plan. Our director and host stay with the GlamBot for the entire booking.",
        "Need the videos kept private? We can turn off public gallery sharing and send clips only to the guest's own phone.",
        "We need 12′ × 12′ of hard floor, 10′ of height and one dedicated outlet. Gyms, ballrooms and banquet halls all work.",
    ],
    faq=[
        ("Is it safe for a school event?",
         "<p>Yes. Guests stand on the floor on a red carpet with no platform to climb onto. The robotic arm moves on a fixed path, and our director controls it and keeps the area clear for the entire event.</p>"),
        ("Can you do a quinceañera with a big court?",
         "<p>Yes. We'll film the full court together and then smaller groups, and the quinceañera gets her own solo clip.</p>"),
        ("Can the school or family logo go on the videos?",
         "<p>Yes. Your logo, crest or monogram goes on every clip at no extra cost.</p>"),
        FAQ_360,
    ],
    media_caption="Built for big dresses and bigger entrances.",
    media_alt="Slow-motion GlamBot clip of a guest in a gown",
    cta="Check your date",
)

# ---- GlamBot vs 360 ---------------------------------------------------------
vs_trail = [("index", "Home"), ("glambot-vs-360-photo-booth", "GlamBot vs 360 Booth")]
vs_faq = [
    FAQ_360,
    ("Are 360 photo booths still popular?",
     "<p>Yes, and that's the problem if you want something memorable. 360 booths went from novelty to standard over the last few years. The national median rental is now around $750, which means you'll find one at sweet 16s, office parties and most weddings. Your guests have probably stood on one recently.</p>"),
    ("Is a GlamBot worth it compared to a 360 booth?",
     f"<p>If the event is a dress-up night (a wedding, gala, mitzvah, prom or launch), the GlamBot fits the mood better and gives guests something they haven't done. It costs more than a basic 360, starting at {C['price_from']}, because you get a robotic arm, pro lighting and two crew members instead of one attendant with a phone rig.</p>"),
    ("Some 360 companies call their booth a glambot. What's the difference?",
     "<p>A true GlamBot is a robotic arm that moves a camera around a guest standing on the floor. A 360 booth is a platform guests stand on while a camera spins around them. If the listing shows a round platform, it's a 360 booth no matter what it's called.</p>"),
    ("Can we have both a GlamBot and a photo booth?",
     "<p>Sure. A print photo booth and a GlamBot do different jobs: one makes the photo strip, the other makes the hero video. Plenty of events run both. We'd just skip doubling up with a 360, since it covers the same ground as the GlamBot.</p>"),
]
vs_body = f"""
<main id="main">
<section class="page-hero"><div class="wrap">
  {crumbs(vs_trail)}
  <h1>GlamBot vs 360 photo booth: <em>which one</em> is right for your event?</h1>
  <p class="lede">Both make videos. Only one makes your guests feel like they're walking into a premiere. Here's an honest look at the difference, from people who chose the robot.</p>
</div></section>

<section class="section"><div class="wrap">
  <div class="section-head"><p class="eyebrow">Side by side</p><h2>The short version</h2></div>
  {compare_table()}
</div></section>

<section class="section"><div class="wrap split">
  <div class="stack prose">
    <p class="eyebrow">The honest take</p>
    <h2>360 booths aren't bad. They're just <em>everywhere</em>.</h2>
    <p>A few years ago, a 360 booth was the most exciting thing at a party. Then everybody got one. Today the typical 360 rental runs around $750, and it shows up at nearly every sweet 16, office party and wedding in the area. Event planners now treat it as expected, not special.</p>
    <p>That's fine for a backyard birthday. But if you're planning a wedding, a black-tie gala or a mitzvah you've been saving for, "the same booth as last weekend" isn't the feeling you're after.</p>
    <h3>Where the 360 falls short at a dress-up event</h3>
    <ul>
      <li><strong>The platform.</strong> Guests in gowns and heels climb onto a raised, spinning platform. Many 360 operators ask clients to sign waivers for falls, and plenty of guests skip it entirely.</li>
      <li><strong>The camera.</strong> Most 360 rigs use a phone on a spinning arm. Fine for a fun spin, not for footage that flatters a gown.</li>
      <li><strong>The look.</strong> Fast spins and ring lights read "party." Formal events call for something closer to the Oscars red carpet.</li>
      <li><strong>The name game.</strong> Some 360 companies now call their spinner a "glambot." If there's a platform, it's a 360.</li>
    </ul>
    <h3>What a GlamBot does differently</h3>
    <ul>
      <li><strong>Guests stay on the floor.</strong> No platform. Just a red carpet and a mark to stand on.</li>
      <li><strong>A real robotic arm.</strong> It sweeps a pro camera around the guest in one smooth, repeatable move.</li>
      <li><strong>Film-set lighting and a director.</strong> Every guest is posed and lit, so even the camera-shy look great.</li>
      <li><strong>Slow motion.</strong> A few seconds of motion becomes a cinematic clip, and guests get it on their phone right away.</li>
    </ul>
  </div>
  <div class="stack">
    {reel("hero-couple.mp4", "hero-couple.jpg", "Slow motion", "One sweep of the arm, played back slow. No platform, no spinning.", "Couple dancing in a slow-motion GlamBot clip")}
    <p class="note">Industry trade shows have been calling robotic arms the next big thing after the 360. Philadelphia has very few dedicated GlamBot crews, so your guests likely haven't done one yet.</p>
  </div>
</div></section>

<section class="section"><div class="wrap">
  <div class="section-head"><p class="eyebrow">Questions</p><h2>GlamBot vs 360 FAQ</h2></div>
  {faq_html(vs_faq)}
</div></section>
{cta_band()}
</main>"""
PAGES.append(page("glambot-vs-360-photo-booth",
                  "GlamBot vs 360 Photo Booth: Which Is Better?",
                  "360 photo booths are everywhere now. See how a robotic slow-motion GlamBot compares on look, safety, staffing and price, and which fits weddings, galas and mitzvahs.",
                  vs_body, [BUSINESS, faq_schema(vs_faq), breadcrumb_schema(vs_trail)]))

# ---- Pricing --------------------------------------------------------------
pr_trail = [("index", "Home"), ("glambot-pricing", "Pricing")]
pr_faq = [
    ("How much does a GlamBot rental cost in Philadelphia?",
     f"<p>Our GlamBot experience starts at <strong>{C['price_from']}</strong> for {C['package_hours']}. That includes the director, host, red carpet, LED lighting, unlimited videos, your logo on every clip, instant text and email sharing, an online gallery and travel within {C['travel_radius']} of {C['travel_base']}.</p>"),
    ("Why do other GlamBot companies not list prices?",
     "<p>We can't speak for them, but we'd rather you know up front.</p>"),
    ("Do you charge for travel?",
     f"<p>Travel within {C['travel_radius']} of {C['travel_base']} is included. That covers Philadelphia, most of the Main Line, Montgomery, Bucks, Chester and Delaware Counties, and nearby South Jersey. Beyond that it's {C['travel_fee']}.</p>"),
    ("Can we add more time?",
     f"<p>Yes. Extra time is {C['extra_30']} per 30 minutes or {C['extra_60']} per hour, and it's easiest to add when you book.</p>"),
    ("Is there a limit on how many videos guests can make?",
     "<p>No. Every package includes unlimited videos for the length of your booking.</p>"),
]
addons = [
    ("Live TV Display", C["addon_tv"], "A screen that plays every clip as it's made. Great near the bar or the entrance."),
    ("Enhanced branding", C["addon_branding"], "Your colors, logo and name on the download gallery and the text message every guest receives."),
    ("Intro & outro overlays", C["addon_overlay"], "A custom animated open or close on every video: names, date, sponsor, event title."),
    ("Custom backdrop", C["addon_backdrop"], "A printed backdrop designed for your event, behind every shot."),
    ("Soundtrack", "Free", "Royalty-free music on every clip, picked to match your night."),
    ("Extra time", f"{C['extra_30']} / 30 min", f"Or {C['extra_60']} per additional hour."),
]
addon_html = "".join(f'<div class="addon"><b>{e(a)}</b><span class="amt">{e(b)}</span><p>{e(c)}</p></div>' for a, b, c in addons)
pkg_items = "".join(f"<li>{e(a)}</li>" for a, _ in INCLUDED)
pr_body = f"""
<main id="main">
<section class="page-hero"><div class="wrap">
  {crumbs(pr_trail)}
  <h1>GlamBot pricing, <em>out in the open</em>.</h1>
  <p class="lede">One package with everything that makes it work, plus a few add-ons if you want to go further. No mystery quote form required to see a number.</p>
</div></section>

<section class="section"><div class="wrap">
  <div class="packages">
    <div class="package featured">
      <p class="eyebrow">The GlamBot Experience</p>
      <p class="price">{C['price_from']}<small>{C['package_hours']}</small></p>
      <p class="muted">Three hours inside your venue, from cocktail hour through the reception. Most weddings, galas and mitzvahs book this.</p>
      <ul>{pkg_items}</ul>
      <a class="btn btn-gold" href="book.html">Check your date</a>
    </div>
    <div class="package">
      <p class="eyebrow">Travel & venue</p>
      <p class="price" style="font-size:var(--step-2)">Included within {C['travel_radius']}</p>
      <p class="muted">Measured from {C['travel_base']}. Beyond that, {C['travel_fee']}.</p>
      {callsheet("Venue needs", "Send to your coordinator", VENUE_NEEDS)}
    </div>
  </div>
</div></section>

<section class="section"><div class="wrap">
  <div class="section-head"><p class="eyebrow">Add-ons</p><h2>Make it yours.</h2></div>
  <div class="addons">{addon_html}</div>
</div></section>

<section class="section"><div class="wrap">
  <div class="section-head"><p class="eyebrow">Questions</p><h2>Pricing FAQ</h2></div>
  {faq_html(pr_faq)}
</div></section>
{inquiry_form(heading="Get your exact quote", sub="Send your date, venue and guest count and we'll reply with availability and a final number.")}
</main>"""
PAGES.append(page("glambot-pricing", "GlamBot Cost Philadelphia | Pricing & Packages",
                  f"How much does a GlamBot cost? Philadelphia GlamBot packages start at {C['price_from']} for {C['package_hours']} with director, host, red carpet, lighting and unlimited videos.",
                  pr_body, [BUSINESS, service_schema("GlamBot Experience", "Robotic slow-motion red carpet video experience", "glambot-pricing"), faq_schema(pr_faq), breadcrumb_schema(pr_trail)]))

# ---- FAQ -----------------------------------------------------------------
faq_trail = [("index", "Home"), ("faq", "FAQ")]
faq_groups = [
    ("The experience", [
        FAQ_CORE[0], FAQ_360,
        ("Is this the GlamBot from the Oscars?",
         "<p>No. The camera used on TV red carpets is a custom broadcast rig that isn't realistically rentable for private events. We bring the same style of experience, a robotic arm sweeping a camera around each guest in slow motion, built for real events and real budgets.</p>"),
        ("How long is each video?",
         "<p>Short and made for social media: a few seconds of real motion, slowed down into a dramatic clip. Long enough to show the twirl, short enough that people watch it ten times.</p>"),
        ("Do guests need to know what to do?",
         "<p>Not at all. Our director poses every guest and calls the move. Shy guests get coached; hams get turned loose.</p>"),
        ("Can groups go together?",
         "<p>Yes. Singles, couples and small groups all work. Our director sets up each shot so everyone fits in the frame.</p>"),
    ]),
    ("Videos & branding", [
        FAQ_CORE[2],
        ("Is there a limit on videos?", "<p>No. Unlimited videos for the length of your booking.</p>"),
        ("Can we put our logo on the videos?",
         "<p>Yes, a logo watermark is included on every clip. Weddings often use a monogram or date; brands and galas use their logo or a sponsor's. Custom intro and outro overlays and enhanced branding of the gallery and text messages are available as add-ons.</p>"),
        ("Can guests watch the videos at the event?",
         f"<p>Yes, with the Live TV Display add-on ({C['addon_tv']}). It plays every clip as it's made.</p>"),
        ("Is there music on the videos?", "<p>Yes. Royalty-free soundtracks are included at no cost.</p>"),
    ]),
    ("Venue & logistics", [
        FAQ_CORE[3],
        ("Can the GlamBot go outside?",
         "<p>Yes, on a hard, level surface like a patio, deck or tent floor, with power nearby and cover from rain. It can't go on grass, dirt or sand.</p>"),
        ("Is it safe?",
         "<p>Guests stand on the floor on our red carpet, with no platform to climb onto or fall off. The robotic arm moves on a set path, and our director runs it and keeps the area clear for the whole event.</p>"),
        ("Do you need internet?",
         "<p>Instant text and email delivery needs an internet connection. If venue Wi-Fi is unreliable, tell us ahead of time and we'll plan around it.</p>"),
        ("Who runs it?", "<p>Our own crew: an on-site director and an on-site host for every booking. You don't need to provide staff.</p>"),
        ("Can you send a certificate of insurance?", "<p>Yes. Send us your venue's requirements and we'll get it over before the event.</p>"),
    ]),
    ("Booking & pricing", [
        FAQ_CORE[4],
        ("How far do you travel?",
         f"<p>Travel within {C['travel_radius']} of {C['travel_base']} is included: Philadelphia, the Main Line, Montgomery, Bucks, Chester and Delaware Counties, and nearby South Jersey. Farther out is {C['travel_fee']}. <a href=\"service-area.html\">See our service area</a>.</p>"),
        ("How far in advance should we book?",
         "<p>As soon as your venue and date are set. Saturdays in wedding season, spring and fall gala weekends and December holiday parties book first.</p>"),
        ("How do we reserve our date?",
         "<p>Send us your details through the form. We'll confirm availability and send a quote and booking link; a deposit holds your date.</p>"),
        ("Can DJs or planners offer the GlamBot to their clients?",
         "<p>Yes. We partner with DJs, planners and venues, including white-label options. <a href=\"dj-planner-partners.html\">See partner details</a>.</p>"),
    ]),
]
all_faq = [qa for _, items in faq_groups for qa in items]
groups_html = "".join(f'<div class="faq-group"><h2>{e(g)}</h2>{faq_html(items)}</div>' for g, items in faq_groups)
faq_body = f"""
<main id="main">
<section class="page-hero"><div class="wrap">
  {crumbs(faq_trail)}
  <h1>GlamBot <em>questions</em>, answered.</h1>
  <p class="lede">Everything couples, planners and event chairs ask us, from how the robot works to how much floor space you need.</p>
</div></section>
<section class="section"><div class="wrap">{groups_html}</div></section>
{cta_band("Still wondering if it fits your night?", "Ask us about your date")}
</main>"""
PAGES.append(page("faq", "GlamBot FAQ | How It Works, Space & Pricing",
                  "Answers about the GlamBot robotic slow-motion camera: how it works, how it differs from a 360 booth, space and power needs, branding, travel and pricing in Philadelphia.",
                  faq_body, [BUSINESS, faq_schema(all_faq), breadcrumb_schema(faq_trail)]))

# ---- Service area --------------------------------------------------------
sa_trail = [("index", "Home"), ("service-area", "Service Area")]
ids = {"Philadelphia": "philadelphia", "Montgomery County & Main Line": "main-line", "Bucks County": "bucks",
       "Chester & Delaware Counties": "chester-delco", "South Jersey & Delaware": "south-jersey"}
area_html = "".join(f'<div id="{ids[k]}"><h3>{e(k)}</h3><ul>{"".join(f"<li>{e(t)}</li>" for t in v)}</ul></div>' for k, v in AREAS.items())
sa_body = f"""
<main id="main">
<section class="page-hero"><div class="wrap">
  {crumbs(sa_trail)}
  <h1>GlamBot rental across <em>Greater Philadelphia</em></h1>
  <p class="lede">We're based in Montgomery County and bring the red carpet to Philadelphia, the Main Line, Bucks County, Chester and Delaware Counties, South Jersey and Wilmington.</p>
</div></section>
<section class="section"><div class="wrap">
  <div class="section-head"><p class="eyebrow">Travel included within {C['travel_radius']} of {C['travel_base']}</p><h2>Where we go</h2><p class="muted">Don't see your town? If you're within about an hour of Philadelphia, we probably cover it. Farther out is {C['travel_fee']}.</p></div>
  <div class="areas">{area_html}</div>
</div></section>
<section class="section"><div class="wrap split">
  <div class="stack prose">
    <p class="eyebrow">Venues</p>
    <h2>Ballrooms, barns, museums and <em>everything in between</em>.</h2>
    <p>If a venue has 12′ × 12′ of hard floor, 10′ of ceiling and an outlet, the GlamBot fits. That covers Center City hotel ballrooms, Main Line estates, Bucks County barns with wood floors, South Jersey banquet halls, museums, rooftops and corporate offices.</p>
    <p>Recent stops include <strong>Fabrika</strong>, <strong>Monaco Philadelphia</strong> and <strong>Haverford College</strong>.</p>
  </div>
  {callsheet("Venue checklist", "Send to your coordinator", VENUE_NEEDS)}
</div></section>
{inquiry_form()}
</main>"""
PAGES.append(page("service-area", "GlamBot Rental Near Me | Philadelphia & Suburbs",
                  "GlamBot Philly serves Philadelphia, the Main Line, Bucks, Montgomery, Chester and Delaware Counties, South Jersey and Wilmington. Travel included nearby.",
                  sa_body, [BUSINESS, breadcrumb_schema(sa_trail)]))

# ---- Partners ------------------------------------------------------------
pt_trail = [("index", "Home"), ("dj-planner-partners", "DJs & Planners")]
pt_body = f"""
<main id="main">
<section class="page-hero"><div class="wrap">
  {crumbs(pt_trail)}
  <h1>Add a GlamBot to <em>your</em> packages.</h1>
  <p class="lede">For DJs, planners and venues across Greater Philadelphia. Offer a premium red carpet video experience to your clients, under your brand or ours, without buying or running any equipment.</p>
</div></section>
<section class="section"><div class="wrap split">
  <div class="stack prose">
    <p class="eyebrow">How it works</p>
    <h2>You sell it. <em>We run it.</em></h2>
    <ul>
      <li><strong>Your brand, if you want it.</strong> We can present the experience under your company name, with your logo on the videos and the sharing page.</li>
      <li><strong>We handle everything on site.</strong> Equipment, setup, the director and host, and takedown. Your team stays focused on music and the timeline.</li>
      <li><strong>You earn on every booking.</strong> Partners earn a referral commission on the events they bring in.</li>
      <li><strong>A better package for your clients.</strong> A premium add-on that helps you win the booking and gets your name on hundreds of shared videos.</li>
    </ul>
    <p>Ask us for the partner pricing guide and a short agreement.</p>
  </div>
  {reel("bride.mp4", "bride.jpg", "Slow motion", "Every clip can carry your brand instead of ours.", "Slow-motion GlamBot clip")}
</div></section>
{inquiry_form(preset="Other", heading="Become a partner", sub="Tell us about your business and the events you work. We'll send the partner guide.")}
</main>"""
PAGES.append(page("dj-planner-partners", "GlamBot for DJs, Planners & Venues | Partner Program",
                  "DJs, planners and venues in Greater Philadelphia can offer a robotic slow-motion GlamBot under their own brand. We run it; you earn on every booking.",
                  pt_body, [BUSINESS, breadcrumb_schema(pt_trail)]))

# ---- Book ----------------------------------------------------------------
bk_trail = [("index", "Home"), ("book", "Check your date")]
bk_body = f"""
<main id="main">
<section class="page-hero"><div class="wrap">
  {crumbs(bk_trail)}
  <h1>Let's put your guests on the <em>red carpet</em>.</h1>
  <p class="lede">Send your date and a few details. We'll confirm availability and send a quote, usually the same day.</p>
</div></section>
{inquiry_form(heading="Your event")}
</main>"""
PAGES.append(page("book", "Book a GlamBot | Check Availability | GlamBot Philly",
                  f"Check GlamBot availability for your Philadelphia-area wedding, gala, mitzvah or corporate event. Packages from {C['price_from']}.",
                  bk_body, [BUSINESS, breadcrumb_schema(bk_trail)]))


# ---- 404 -----------------------------------------------------------------
nf_body = """
<main id="main">
<section class="page-hero"><div class="wrap">
  <p class="eyebrow">404 · Off the carpet</p>
  <h1>This page <em>walked off</em> the red carpet.</h1>
  <p class="lede">The link may be old or mistyped. Here's where most people are headed.</p>
  <div class="actions"><a class="btn btn-gold" href="index.html">Back to home</a><a class="btn btn-ghost" href="glambot-pricing.html">Pricing</a><a class="btn btn-ghost" href="book.html">Check your date</a></div>
</div></section>
<section class="section"><div class="wrap">""" + events_grid() + """</div></section>
</main>"""
NOT_FOUND = page("404", "Page Not Found | GlamBot Philly", "This page isn't here. Find GlamBot pricing, event pages and availability for Philadelphia events.", nf_body, [BUSINESS], current="")

HEADERS = """/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN
  Permissions-Policy: camera=(), microphone=(), geolocation=()

/assets/*
  Cache-Control: public, max-age=86400

/media/*
  Cache-Control: public, max-age=2592000
"""

# Old Webflow/Wix-style paths people may have bookmarked. Extend once the old
# site's URLs are known (Google Search Console > Pages lists them).
REDIRECTS = """/home / 301
/index / 301
/weddings /wedding-glambot-philadelphia 301
/wedding /wedding-glambot-philadelphia 301
/corporate /corporate-event-glambot 301
/events /corporate-event-glambot 301
/pricing /glambot-pricing 301
/packages /glambot-pricing 301
/contact /book 301
/book-now /book 301
/faqs /faq 301
"""


# --------------------------------------------------------------------------
# write
# --------------------------------------------------------------------------
import re

SLUGS = sorted({p["slug"] for p in PAGES} | {"404"}, key=len, reverse=True)


def clean_links(doc):
    """Cloudflare Pages serves /page for page.html; link there directly and
    use root-absolute asset paths so the 404 page works at any depth."""
    doc = re.sub(r'(href|src|poster)="(assets|media)/', r'\1="/\2/', doc)
    doc = re.sub(r'href="index\.html(#[\w-]+)?"', lambda m: f'href="/{m.group(1) or ""}"', doc)
    for slug in SLUGS:
        doc = re.sub(rf'href="{re.escape(slug)}\.html(#[\w-]+)?"', lambda m: f'href="/{slug}{m.group(1) or ""}"', doc)
    return doc

def full_doc(p):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{p['head']}
</head>
<body>
{p['body']}
</body>
</html>
"""


def write_site(out, artifact=False):
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(SRC, out)
    for p in PAGES + ([] if artifact else [NOT_FOUND]):
        name = "index.html" if p["slug"] == "index" else f"{p['slug']}.html"
        if artifact and p["slug"] == "index":
            # The artifact host wraps its main page in its own document skeleton.
            doc = p["head"] + "\n" + p["body"] + "\n"
        else:
            doc = full_doc(p) if artifact else clean_links(full_doc(p))
        (out / name).write_text(doc, encoding="utf-8")
    if not artifact:
        urls = "".join(f"  <url><loc>{url(p['slug'])}</loc></url>\n" for p in PAGES)
        (out / "sitemap.xml").write_text(
            f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
        (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {C['domain']}/sitemap.xml\n")
        (out / "_headers").write_text(HEADERS)
        (out / "_redirects").write_text(REDIRECTS)


if __name__ == "__main__":
    write_site(DIST)
    print(f"wrote {len(PAGES)} pages to {DIST}")
    if "--artifact" in sys.argv:
        target = Path(sys.argv[sys.argv.index("--artifact") + 1]) if len(sys.argv) > sys.argv.index("--artifact") + 1 else ROOT / "artifact"
        write_site(target, artifact=True)
        print(f"wrote artifact build to {target}")
