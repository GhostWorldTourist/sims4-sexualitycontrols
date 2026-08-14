# Sims 4 - Sexuality Controls

Tools for deliberately controlling Sim sexuality instead of leaving it to chance.

## Make All Sims Heterosexual

Sets a heterosexual baseline for every adult human Sim **exactly once**, then
never touches them again - so any exception you set by hand afterwards sticks.

This exists for players who want to author their world's sexuality deliberately
rather than accept the game's randomisation. Set the baseline, then hand-pick
the Sims who differ.

* Applies to teen/YA/adult/elder **human** Sims only
* Skips any Sim already in a committed romance (engaged, married, going steady,
  promised, newlywed, secret lover) - converting them could invalidate a
  relationship you built
* Adds a hidden marker trait on conversion; both loots blacklist it, so a Sim is
  processed once and only once

### Requires

**Lot51 Core** (1.17+)

### Install

Download the `.package` from the [Releases](https://github.com/GhostWorldTourist/sims4-sexualitycontrols/releases) page
and drop it in `Documents/Electronic Arts/The Sims 4/Mods/`.

## Building from source

```bash
python build.py --audit
```

The `.package` is **not** committed. It is built by CI from this source and
attached to each release, so the file you download always matches the code here.

`tools/` contains a small DBPF writer and a SimData generator. Every resource in
the mod is generated - no other creator's binary data is copied or redistributed.
`--audit` fails the build if a foreign identifier appears in the output, and CI
runs it on every push.

## License

See [LICENSE](LICENSE). Free to use and share, never behind a paywall.
