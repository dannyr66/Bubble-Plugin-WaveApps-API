# glambotphilly.com

The website for GlamBot Philly (The Philly Glam Experience). It is a 13-page static site with an SEO landing page for each event type, pricing and FAQ pages, and a "GlamBot vs 360 booth" page. It is hosted on Cloudflare Pages.

```
python3 build.py                  # writes dist/  (what Cloudflare serves)
python3 build.py --artifact out/  # optional preview build with .html links
```

Edit `CONFIG` at the top of `build.py` for prices, phone, email and the form endpoint, then commit. Cloudflare rebuilds on every push to `main`. All copy is in `build.py`, and the styles are in `src/assets/site.css`. The build needs no dependencies, only Python 3.

## Cloudflare Pages setup (one time)

1. Go to **Workers & Pages → Create → Pages → Connect to Git** and pick this repo.
2. Build settings:
   - **Framework preset:** None
   - **Build command:** `python3 build.py`
   - **Build output directory:** `dist`
   - **Production branch:** `main`
3. Once the glambotphilly.com zone is active in Cloudflare, add **both** custom domains, `www.glambotphilly.com` and `glambotphilly.com`, under **Custom domains**. Then add a redirect rule from the apex to `www`. Canonical URLs use `www`.
4. The build also writes these Cloudflare files:
   - `_headers`: caching and security headers
   - `_redirects`: 301s from likely old URLs such as `/pricing` and `/contact`
   - `404.html`

   Pages serves `/wedding-glambot-philadelphia` for `wedding-glambot-philadelphia.html`, and every internal link already uses those clean URLs.

## Current domain state (Oct 13, 2026)

- **DNS:** glambotphilly.com is an active zone on Cloudflare (Danny's account). The registrar is still Porkbun, in a separate Porkbun login.
- **Email:** hello@glambotphilly.com uses Porkbun email forwarding. The Cloudflare zone has the matching records:
  - MX `fwd1.porkbun.com` (priority 10)
  - MX `fwd2.porkbun.com` (priority 20)
  - SPF TXT `v=spf1 include:_spf.porkbun.com ~all`
  - DMARC TXT `v=DMARC1; p=none;`

  Keep these records when you change anything else.
- **Holding page:** a Cloudflare Worker named `glambotphilly-holding` serves a branded holding page on `glambotphilly.com/*` and `www.glambotphilly.com/*`. It returns status 503 with Retry-After, so Google doesn't index it.

  **When the Pages site is ready:**
  1. Delete both Worker routes and the two placeholder `AAAA 100::` records, which are labeled "Placeholder for holding-page Worker" in the DNS comments.
  2. Add both hostnames as custom domains on the Pages project.
  3. Delete the Worker.

## Page map and target searches

| Page | Primary searches | Secondary |
|---|---|---|
| `/` | glambot rental philadelphia, glambot philadelphia, glam bot near me | robotic camera booth, slow motion video booth |
| `/wedding-glambot-philadelphia` | wedding glambot, slow motion wedding video booth | unique wedding entertainment ideas, red carpet wedding, luxury wedding photo booth philadelphia |
| `/gala-fundraiser-glambot` | gala entertainment ideas, red carpet for gala | fundraiser gala ideas, sponsor activation, step and repeat with video |
| `/corporate-event-glambot` | brand activation ideas philadelphia, branded video booth | product launch event ideas, trade show booth attraction |
| `/holiday-party-glambot` | corporate holiday party ideas philadelphia | office christmas party entertainment, NYE party entertainment |
| `/bar-bat-mitzvah-glambot` | bar mitzvah entertainment ideas, bat mitzvah party ideas | mitzvah photo booth philadelphia |
| `/prom-sweet-16-quinceanera-glambot` | prom red carpet ideas, quinceañera entertainment | sweet 16 party ideas, school dance photo booth |
| `/glambot-vs-360-photo-booth` | glambot vs 360 booth, 360 booth alternative | 360 photo booth rental philadelphia, luxury photo booth |
| `/glambot-pricing` | glambot cost, how much does a glambot cost | glambot rental price |
| `/faq` | what is a glambot, how does a glambot work | glambot space requirements |
| `/service-area` | glambot near me, glambot [town] | main line / bucks county / south jersey |
| `/dj-planner-partners` | DJ add-on services, white label glambot | — |
| `/book` | — (conversion page) | — |

### Built-in SEO
- Each page has a unique title and meta description, a canonical URL, and Open Graph tags.
- Structured data:
  - `EntertainmentBusiness` on every page
  - `Service` (with a starting price) on each event and pricing page
  - `FAQPage` on every page that has an FAQ
  - `BreadcrumbList` on inner pages
- `sitemap.xml` and `robots.txt` are generated with the site.
- Every page has one H1 with its target keyword, and every page links to the others.
- Videos and images are small. Videos are 720p and about 0.5–0.7 MB each, so pages load fast.

### Positioning choices (from the research)
- **Price shown up front.** Almost no Philly competitor publishes a price, so "From $2,995 for 3 hours" stands out. It also sits under the $3,500+ that published U.S. competitors charge.
- **"A real robotic arm."** Some 360 companies around Philly now sell a spinning platform as a "glambot." The site says plainly that ours is not one.
- **The 360 angle stays educational, not snarky.** 360 booths are now the default at every party (median rental is about $750). The site explains the differences that matter at dress-up events:
  - guests stay on the floor instead of climbing a spinning platform
  - a pro camera on a robotic arm instead of a phone
  - a director who poses each guest

## Before launch

1. **Connect the form.** Set `form_endpoint` in `CONFIG` to a Formspree, Basin or Tally webhook, or your Rally inquiry endpoint. Until it's set, the form tells visitors to email hello@glambotphilly.com.
2. **Redirect old URLs.** Add any of the old site's URLs that `_redirects` doesn't already cover. Search Console → Pages lists them. Add each one to `REDIRECTS` in `build.py` so you keep your rankings.
3. **Search setup:**
   - Submit `sitemap.xml` in Google Search Console.
   - Create or claim the **Google Business Profile** for GlamBot Philly. Use the "event entertainment" category and post clips weekly. This is the biggest lever for "glambot near me."
4. **Ask for reviews.** Every happy client should get a Google review link. We left reviews off the site until there are real ones to quote.

## Media we still need (from Google Drive)

The Drive connector caps downloads at about 4 MB per file, so most raw clips (13–20 MB) couldn't be pulled. Export 6–10 favorites as **720p MP4s under ~3 MB** and drop them into `src/media/`.

| Drive folder | Use on |
|---|---|
| Fabrika - Styled Shoot (50 clips) | Home gallery, weddings |
| Monaco - Tag @MonacoVenue | Galas, corporate |
| Haverford College Drag Ball | Proms & formals |
| Dominique's Bridal Shower | Weddings |
| Pemberton Twp High (*marked not for social*) | Do not use without permission |

Real event photos of the robot arm and red carpet setup would also help the "What is a GlamBot" section.

## Decisions on record

- **Pricing:** from $2,995 for 3 hours. Extra time is $500 per 30 minutes or $1,000 per hour. Add-ons are in `CONFIG`.
- **Phone:** the Glam Bot line in Quo, (267) 888-GLAM (4526).
- **Naming past events:** OK to name Fabrika, Monaco Philadelphia and Haverford College.
- **Manufacturer demo footage:** OK to use. This covers the couple clip, the robot-arm photo, and the brand-activation stills on the corporate page.
