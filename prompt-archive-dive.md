# archive-dive monthly routine

Write the monthly archive-dive post. You are checked out in kearney108/archive-dive.
This repo contains the raw finds in `finds/YYYY-MM/` AND the published editorial volumes.

---

## Step 1 — Determine the month

```bash
python3 -c "
from datetime import date, timedelta
d = date.today().replace(day=1) - timedelta(days=1)
print('MONTH:', d.strftime('%Y-%m'))
print('LABEL:', d.strftime('%B %Y'))
print('MONTH_UPPER:', d.strftime('%B').upper())
print('YEAR:', d.strftime('%Y'))
print('VOL_INT:', len([f for f in __import__('pathlib').Path('.').glob('vol-*.md')]))
"
```

## Step 2 — Read the finds

Read ALL `metadata.md` files from `finds/{MONTH}/`. Also read the first 600 chars of
`content.txt` for each find. Build a full picture: title, creator, year, source archive,
subjects, any striking snippet.

## Step 3 — Read the template

Read `vol-01-may-2026.md`. This is the exact format you must follow.
Count `vol-*.md` files to get the next volume number (zero-padded: 02, 03, …).

## Step 4 — Pick a plate and generate the banner

Based on the finds' themes and subjects, search Wikimedia Commons for a relevant
public-domain plate — natural history illustration, manuscript, scientific diagram,
anatomical plate, old map, BHL plate, etc. Use WebFetch on:
`https://commons.wikimedia.org/wiki/Special:Search?search={theme}&ns6=1`
or WebSearch for `site:commons.wikimedia.org {theme} illustration public domain`.

Find the direct 1280px thumbnail URL (format:
`https://upload.wikimedia.org/wikipedia/commons/thumb/X/XX/Filename.jpg/1280px-Filename.jpg`).

Then run:
```bash
pip install Pillow -q 2>/dev/null || true
python3 gen_banner.py "{PLATE_URL}" {VOL_INT} {MONTH_UPPER} {YEAR} vol-{NN}-banner.png
```

## Step 5 — Write the editorial post

Create `vol-{NN}-{month-lowercase}-{year}.md` following the vol-01 template exactly.

Start with the banner:
```html
<p align="center">
  <img src="vol-{NN}-banner.png" alt="Archive-Dive Vol. {NN} — {one-line description}" width="100%" />
</p>
```

Then: opener, asterism dividers, numbered finds, bandeau ornament, tail-piece, colophon.

**Voice:** Direct and curious. Never academic. Each find: where you found it / what it is /
why it matters. 2–4 sentences. Short sentences. No hedging. No "interestingly."
Pull-quote only if there's a genuinely sharp line from the actual content.
Opener reads like a letter, not a table of contents.

**Curation:** Pick 3–5 finds. Prefer finds with real content.txt material. A strange title
with a real year beats a vague subject-tagged item. BBS-era textfiles are fair game —
treat them as artifacts from a weirder internet.

## Step 6 — Update README.md

Insert a new row at the top of the volumes table (newest first):
```
| `vol·{NN}` | [**What Surfaced — {Label}**](vol-{NN}-{month}-{year}.md) — *{MONTH_UPPER} · {YEAR} · 108* |
```

## Step 7 — Commit and push

```bash
git config user.email "johndanielkearney@gmail.com"
git config user.name "John Kearney"
git add vol-{NN}-banner.png vol-{NN}-*.md README.md
git commit -m "archive-dive vol·{NN} — {Label}"
git push
```

If push fails, stop and report the exact error.
