# PSO Drop Charts

Drop charts for Phantasy Star Online on Dreamcast, Nintendo GameCube, and Blue Burst.

The production site is [dropcharts.psohaven.com](https://dropcharts.psohaven.com/).

## Supported versions

- Blue Burst: Episodes 1, 2, and 4, including monster and box drops
- Nintendo GameCube: Episodes 1 and 2 monster drops
- Dreamcast: Episode 1 monster drops
- English, Japanese, and Chinese item data

## Development

Install Python 3.10 or later, [`uv`](https://docs.astral.sh/uv/), and Node.js. Then run:

```bash
npm test
```

Build a deployable static site in `_site` with:

```bash
npm run build
```

See [the update and deployment guide](docs/update.md) for the complete data pipeline.

## License

This project is licensed under the ISC License. See [LICENSE](LICENSE).
