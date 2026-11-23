# THE WORLD TODAY — 23 November 2026

A front-page-style image summing up Monday 23 November 2026's world news,
drawn entirely in code by `main.py` (Python 3.13, standard library only).

## The image

- **Masthead:** THE WORLD TODAY — MONDAY, 23 NOVEMBER 2026
- **Lead:** COP31 climate talks in Antalya collapse with no deal — the
  longest COP ever, the first to fail since Copenhagen 2009 — after the EU
  and small island states refuse a draft with no mention of fossil fuels.
- **Middle East:** Houthis claim a strike on Saudi Arabia's Rabigh oil
  refinery; two more tankers catch fire near Hormuz after hitting mines.
- **Ukraine:** a boy, 7, is pulled alive from rubble in Dymer, north of
  Kyiv, after a Russian drone strike; at least 11 killed in the region.
- **NATO:** emergency session in Brussels after three Russian objects
  enter Polish airspace; debris confirmed as Kh-101 cruise missiles.
- **United States:** Democrats win a 258th House seat — their biggest
  House majority in over three decades.
- **Markets:** stocks slump and oil holds near $92 as an AI sell-off
  spreads; Brent $92.29, WTI $83.26.
- **Pacific:** a deep magnitude 6.5 quake strikes off Vanuatu, 601 km
  down; no casualties, no tsunami warning.
- **Health:** the NHS begins the world's largest AI breast-screening
  trial — nearly 700,000 women at 30 sites.
- **Sport:** Alcaraz beats Zverev to win the ATP Finals; Liverpool beat
  ten-man Manchester United 4-0.
- **Culture (sidebar):** Shuri Castle's restored main hall reopens in
  Okinawa, seven years after the 2019 fire.

## How it works

`main.py` draws the 1024x1024 page with a tiny built-in 5x7 bitmap font
(uppercase A-Z, digits, punctuation) and a pure-stdlib PNG encoder
(zlib, fixed settings). No network, no downloaded assets, no timestamps,
no randomness — two runs produce byte-identical output.

Run it:

```
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

## License

MIT — see LICENSE.
