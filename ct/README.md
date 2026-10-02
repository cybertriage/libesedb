# libesedb for Cyber Triage

This fork builds the `esedbexport` that Cyber Triage runs to export ESE
databases, such as the IE and Edge `WebCacheV01.dat`, as text. `esedbinfo` ships
beside it as a diagnostic.

Work happens on the `ct` branch. `main` tracks upstream
[libyal/libesedb](https://github.com/libyal/libesedb) unchanged.

## What differs from upstream

- The libyal dependencies are pinned in `ct/dependencies.txt`.
  `synclibs.sh` and `synclibs.ps1` check out those versions, not the latest
  tags. `libfcache` has no tags, so it is pinned by commit.
- `.github/workflows/ct_release.yml` builds the binaries Cyber Triage ships.

The library and the tools are upstream's, unchanged.

## Getting the binaries

Do not build locally. Download a release from this repository's Releases page.
Each release has:

| File | Contents |
|---|---|
| `esedbexport-<tag>-windows-x64.zip` | `esedbexport.exe`, `esedbinfo.exe`, `libesedb.dll`, `vcruntime140.dll` |
| `esedbexport-<tag>-linux-x86_64.tar.gz` | `esedbexport` and `esedbinfo`, statically linked |
| `SHA256SUMS` | SHA-256 of both archives |

Both archives also carry `COPYING`, `COPYING.LESSER`, `dependencies.txt` and a
`SOURCE.txt` naming the exact source commit and build.

The Windows build needs the Universal C Runtime, which ships with Windows 10 and
later.

Every push to `ct` builds the same archives and keeps them as workflow
artifacts for the run. Only a tag publishes a release.

## Making a release

1. Make sure the `ct_release` workflow passes on `ct`.
2. Tag the commit `ct-<upstream version>.<n>`, for example `ct-20260923.1`.
   The upstream version is the `AC_INIT` version in `configure.ac`.
3. Push the tag. The workflow publishes the release.

Never move or reuse a tag. Cyber Triage pins a release by its SHA-256.

## Updating a dependency

Change its line in `ct/dependencies.txt` in its own commit, then release.

## Updating from upstream

```
git fetch upstream
git switch main && git merge --ff-only upstream/main && git push origin main
git switch ct && git rebase main
```

Then check that the `ct_release` workflow passes, and release.

## Licence

LGPL-3.0-or-later, the same as upstream. The source for every release is this
repository at the commit named in its `SOURCE.txt`.
