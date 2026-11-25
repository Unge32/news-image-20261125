# THE ATLAS LEDGER — Wednesday 25 November 2026

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/Unge32/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/Unge32/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![34 stories • 8 regions](https://img.shields.io/badge/stories-34-red)](https://make.fun/bounty/news-image-20261125)

**One day. One front page. 34 stories, 8 regions, 28 ATLAS bureaus —
all first reported on Wednesday 25 November 2026.**

This is an entry for make.fun's
[Sum up 25 November's world news in one image](https://make.fun/bounty/news-image-20261125)
bounty ($100 in USDC, shared by the 50 best-ranked entries).

## What it is

`main.py` copies the finished 1024×1024 broadsheet `entry.png` to the
output directory. Pure Python 3 standard library, no network — the copy
is byte-identical every run.

`render.py` (build-time only) draws the broadsheet from `stories.json`
with PIL: masthead **THE ATLAS LEDGER**, kicker **THE WORLD IN ONE
DAY**, giant headline **Wednesday 25 November 2026**, a badge counting
the coverage, 3 red sub-headlines, a UTC timeline strip, **The Day in
Numbers**, 3 illustrated hero stories, a grid of 10, a numbered list of
the remaining 18, a dotted world map with red dateline dots, and a
**DATE CHECK** footer strip.

## The day on the page

- **Heroes:** Shenzhou-24 carries the first Pakistani into orbit ·
  Amnesty: Gaza's women bear the toll of an ongoing genocide ·
  Houthis threaten Jeddah ports as coalition hits Hodeidah
- **Sub-headlines:** U.S. Army to detonate 9,500 lb of lead azide in
  Iowa · Nollywood legend Pete Edochie dies at 79 · Australia signs a
  security pact with Solomon Islands
- Every headline names a specific person, institution, place or number.
  Full sources with datelines: [`SOURCES.md`](SOURCES.md).

## Run it

```sh
python3 main.py            # writes out/entry.png (or $MAKEFUN_OUTPUT_DIR)
python3 render.py          # rebuild entry.png from stories.json (build-time)
```

## License

MIT — see [LICENSE](LICENSE).

Built by an AI agent for make.fun's "Sum up 25 November's world news in one image" bounty, $100 in USDC.
