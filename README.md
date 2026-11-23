# THE WORLD TODAY — 23 November 2026 (v2)

A front-page-style image summing up Monday 23 November 2026's world news,
drawn entirely in code by `main.py` (Python 3, standard library only).
Rebuild in the 22 Nov mould: 7 items, boxed panels, one lead illustration
plus a small motif in every panel, every reading line at scale 3 or larger
in black ink — except the single scale-2 markets ticker.

## The image

- **Masthead:** THE WORLD TODAY — MONDAY, 23 NOVEMBER 2026
- **Lead:** COP31 climate talks in Antalya collapse with no deal — the
  longest COP ever, the first to fail since Copenhagen 2009 — after the EU
  and island states refuse a draft with no mention of fossil fuels.
- **Libya:** Ukraine sinks the Russian corvette Merkury off Benghazi,
  Kyiv says — seven sea drones, 2,400 km from the front; a Ka-27
  helicopter destroyed and the cargo ship MV Angara hit.
- **Ukraine:** a boy, 7, is pulled alive from rubble in Dymer, north of
  Kyiv, after a Russian drone strike; 11 killed in the town.
- **NATO:** emergency session in Brussels after three Russian Kh-101
  cruise missiles enter Polish airspace.
- **United States:** Democrats take a 258th House seat — their largest
  lead in 30 years.
- **Indonesia:** fire at a candy factory in Cikande, Banten, kills 24;
  about 30 still missing.
- **Markets (ticker):** Brent $92.29, WTI $83.26, AI sell-off.
- **Sport:** Alcaraz beats Zverev to win the ATP Finals; Liverpool beat
  ten-man Manchester United 4-0.

Cut from v2 for space (the 7-slot structure is proven; breadth beyond it
costs legibility): the Houthi claim (Gulf context lives in the oil
ticker), the Mexico cartel capture, the NHS AI trial, the Denmark plot,
the Vanuatu quake, and Shuri Castle.

## How it works

`main.py` draws the 1024x1024 page with a tiny built-in 5x7 bitmap font
(uppercase A-Z, digits, punctuation) and a pure-stdlib PNG encoder
(zlib, fixed settings). No network, no downloaded assets, no timestamps,
no randomness — two runs produce byte-identical output. Copy widths,
headline balance (shortest/longest line ≥ 0.60) and panel clearances are
asserted in code before drawing.

Run it:

```
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

## License

MIT — see LICENSE.
