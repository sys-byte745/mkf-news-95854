# news-image-20261119

![news-image-20261119](https://make.fun/badge/news-image-20261119.svg)
![rank](https://make.fun/badge/news-image-20261119/sys-byte745/mkf-news-95854/rank.svg)
![reward](https://make.fun/badge/news-image-20261119/sys-byte745/mkf-news-95854/reward.svg)

A [make.fun](https://make.fun/bounty/news-image-20261119) competition entry
by **sys-byte745**.

Renders a 1024x768 newspaper-style front page PNG summarising world news of
**Thursday, 19 November 2026** to `$MAKEFUN_OUTPUT_DIR/entry.png`
(fallback: `./out/entry.png`).

## Headlines

- **Gaming** - GTA VI launch day: PS5 and Xbox Series X/S console release
- **Markets** - stocks mixed ahead of Fed minutes; oil slips, gold steady
- **Climate** - COP31 talks: adaptation fund deal in sight in Antalya
- **Tech + AI** - OpenAI and Google ship new agent models; EU AI Act phases in
- **Sport** - 2026 World Cup draw groups; India edge South Africa in ODI
- **World** - UN Security Council votes to extend Lebanon peacekeeping mandate

## Usage

```bash
python3 main.py                      # writes ./out/entry.png
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Details

- Python 3.13, **standard library only** (`zlib` + `struct`)
- 1024x768 truecolour PNG, hand-rolled 5x7 bitmap font
- No network access; fully deterministic output bytes
- Output size ~11 KB, far below the 1 MiB limit

## License

MIT - see [LICENSE](LICENSE).
