# glambotphilly.com redesign

A 13-page static site for GlamBot Philly (The Philly Glam Experience). Each event type has its own SEO landing page, there are separate pricing and FAQ pages, and a "GlamBot vs 360 booth" page targets 360 searches.

```
python3 build.py          # writes dist/ (upload this folder to any static host)
```

Edit `CONFIG` at the top of `build.py` for prices, phone, email and the form endpoint. Then rebuild. All copy lives in `build.py`, and the styles are in `src/assets/site.css`.

## Page map and target searches

| Page | Primary searches | Secondary |
|---|---|---|
| `/` | glambot rental philadelphia, glambot philadelphia, glam bot near me | robotic camera booth, slow motion video booth |
| `/wedding-glambot-philadelphia.html` | wedding glambot, slow motion wedding video booth | unique wedding entertainment ideas, red carpet wedding, luxury wedding photo booth philadelphia |
| `/gala-fundraiser-glambot.html` | gala entertainment ideas, red carpet for gala | fundraiser gala ideas, sponsor activation, step and repeat with video |
| `/corporate-event-glambot.html` | brand activation ideas philadelphia, branded video booth | product launch event ideas, trade show booth attraction |
| `/holiday-party-glambot.html` | corporate holiday party ideas philadelphia | office christmas party entertainment, NYE party entertainment |
| `/bar-bat-mitzvah-glambot.html` | bar mitzvah entertainment ideas, bat mitzvah party ideas | mitzvah photo booth philadelphia |
| `/prom-sweet-16-quinceanera-glambot.html` | prom red carpet ideas, quinceañera entertainment | sweet 16 party ideas, school dance photo booth |
| `/glambot-vs-360-photo-booth.html` | glambot vs 360 booth, 360 booth alternative | 360 photo booth rental philadelphia, luxury photo booth |
| `/glambot-pricing.html` | glambot cost, how much does a glambot cost | glambot rental price |
| `/faq.html` | what is a glambot, how does a glambot work | glambot space requirements |
| `/service-area.html` | glambot near me, glambot [town] | main line / bucks county / south jersey |
| `/dj-planner-partners.html` | DJ add-on services, white label glambot | — |
| `/book.html` | — (conversion page) | — |

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
- **Price shown up front.** Almost no Philly competitor publishes a price, so showing "From $1,775" is a real differentiator.
- **"A real robotic arm."** Some 360 companies around Philly now sell a spinning platform as a "glambot." The site says plainly that ours is not one.
- **The 360 angle stays educational, not snarky.** 360 booths are now the default at every party (median rental is about $750). The site explains the differences that matter at dress-up events:
  - guests stay on the floor instead of climbing a spinning platform
  - a pro camera on a robotic arm instead of a phone
  - a director who poses each guest

## Before launch

1. **Connect the form.** Set `form_endpoint` in `CONFIG` to a Formspree, Basin or Tally webhook, or your Rally inquiry endpoint. Until it's set, the form tells visitors to email hello@glambotphilly.com.
2. **Add a phone number** to `CONFIG["phone"]` if you want one shown.
3. **Redirect old URLs.** Set up 301 redirects from the current site's pages to the new ones, so you keep the rankings you already have.
4. **Search setup:**
   - Submit `sitemap.xml` in Google Search Console.
   - Create or claim the **Google Business Profile** for GlamBot Philly. Use the "event entertainment" category and post clips weekly. This is the biggest lever for "glambot near me."
5. **Ask for reviews.** Every happy client should get a Google review link. We left reviews off the site until there are real ones to quote.

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

## Open questions

- **Pricing.** Three sources disagree:
  - The Jan 2026 pricing guide says $1,995 (2 hrs) / $2,995 (3 hrs), but that is the white-label partner sheet.
  - Danny's Aug 2026 client quote was **$1,775 for up to 3 hours**. The site uses that figure.
  - The custom backdrop is listed at ~$1,400 in the guide and $1,050 elsewhere. The site shows it as "quoted per design."
- **Trademark.** "GLAMBOT" is a registered trademark of Pixster Photobooth LLC (USPTO serial 97438011).
  - If your unit is an official Pixster Glambot®, say so on the site. It's a selling point.
  - If it isn't, consider leading with "The Philly Glam Experience" and descriptive terms ("robotic slow-motion camera").
- **Couple clip.** `hero-couple.mp4` (white studio, couple dancing) came from the Marketing Material folder. It has no watermark, and its file timestamp is March 2024, before launch. Confirm it's your footage, or swap it out.
- **Client names.** The site names Fabrika, Monaco Philadelphia and Haverford College as recent events. Confirm you're OK naming them.
