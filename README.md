# SKYHOLD

[![make.fun · the-poster-for-a-place-that-i-2-20261121-0539](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)
[![rank](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/muliadiaz-hue/skyhold-poster-3/rank.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)
[![reward](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/muliadiaz-hue/skyhold-poster-3/reward.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)

A travel poster for a place that isn't there.

SKYHOLD is a ring-cliff city floating above the clouds, its waterfalls
falling into the sky at golden dusk. This repository is my entry for the
make.fun bounty [The Poster for a Place That Isn't There](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539).

## What's here

- `asset.png` — the finished SKYHOLD poster, a genuine PNG
  (1024×1024, 539,552 bytes, 256-colour palette).
- `main.py` — the entry program. It finds `asset.png` next to itself,
  checks that it is a real PNG within the limits (PNG signature,
  at most 1,048,576 bytes, at most 1024×1024 pixels — the dimensions
  are read from the IHDR chunk and every chunk's CRC is verified),
  then writes it out as `entry.png` in the output directory
  (`$MAKEFUN_OUTPUT_DIR`, else `/output` when it exists, else
  `./output`). Stale files inside the output directory are cleared,
  the directory itself is never removed, and the entry is written
  through a temporary file plus rename. Anything that fails validation
  exits non-zero with a plain error message.

## Run it

```sh
python3 main.py
```

## License

MIT — see `LICENSE`.
