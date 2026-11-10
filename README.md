# XDJ-700 PLUS: an analysis

Notes on [lowtrustsociety/XDJ-700-PLUS](https://github.com/lowtrustsociety/XDJ-700-PLUS), an unofficial firmware mod for the Pioneer DJ XDJ-700 (release PLUS V0.90, 2026-10-30, GPL-3.0). This repository holds only this analysis: no mod code, and no Pioneer firmware.

## Credits

**XDJ-700 PLUS is the work of [low trust society](https://github.com/lowtrustsociety)**, who designed, built and tested it over two months and more than 70 builds. All the mod's code, the patchers and the documentation are theirs. This repository only adds an independent review of their work and a verification package for passing their patcher on.

- Original project: [github.com/lowtrustsociety/XDJ-700-PLUS](https://github.com/lowtrustsociety/XDJ-700-PLUS)
- Support the author: [ko-fi.com/lowtrustsociety](https://ko-fi.com/lowtrustsociety)
- FLAC decoding: [dr_flac](https://github.com/mackron/dr_libs) by David Reid
- XDJ-700 and its firmware: Pioneer DJ / AlphaTheta. This project is not affiliated with them.

Bug reports and unplayable files go to the [original project's issues](https://github.com/lowtrustsociety/XDJ-700-PLUS/issues), not here.

## Verification package

[`distribution/XDJ-700-PLUS-V0.90/`](distribution/XDJ-700-PLUS-V0.90/) holds the author's patcher (unchanged, GPL-3.0), a copy with clearer wording, its hashes, this report, and step-by-step instructions for checking everything independently. Start with [`READ_ME_FIRST.txt`](distribution/XDJ-700-PLUS-V0.90/READ_ME_FIRST.txt). It contains no Pioneer firmware.

## Tools

- [`tools/fwcheck.py`](tools/fwcheck.py) compares an official firmware file with a modified one and shows what changed: boot and recovery region, front-panel firmware, small edits (hooks) in the stock code, and whether new code went into empty space or over stock content. It works with XDJ-700 (`XDJ700.UPD`) and CDJ-2000 (`C2KMAIN.UPD`, `C2KGUI.UPD`) files. Python 3.8 or later, standard library only; it only reads files.

      python3 tools/fwcheck.py OFFICIAL.UPD MODIFIED.UPD
      python3 tools/fwcheck.py --identify FILE.UPD

- [`tools/reword_patcher.py`](tools/reword_patcher.py) makes the reworded patcher page from the author's original V0.90 release file. It only does exact text replacements, all listed in the script, and refuses any other input, so anyone can reproduce the reworded page (SHA-256 `c5054fc2f402826b0d809f427463f7da8215ea1561f2762bdf515b6139251f38`). Tested: the reworded page's code, run on the official 1.15 firmware, makes exactly the tested mod and restore files.

## What the mod does

It patches the official XDJ-700 firmware 1.15 to play formats the stock player refuses:

- **FLAC**: 16 and 24-bit, 44.1 to 96 kHz, mono or stereo, at full depth
- **Hi-res WAV and AIFF**: 88.2 and 96 kHz
- **Extensible-header WAVs** (such as Bandcamp downloads) that the stock reader rejects
- Works from USB and over LINK, where only the player playing the track needs the mod
- Ignores the "unplayable" mark another player may have set on a track

88.2 and 96 kHz are halved to 44.1 and 48 kHz with a 47-tap half-band low-pass filter, because the player's audio output only runs at 44.1 and 48 kHz.

Everything the stock firmware already plays (MP3, AAC, 44.1 and 48 kHz WAV and AIFF) still goes through Pioneer's own code.

## How it works

The player has a Renesas SH-4A main processor and a TI C6000 audio processor. The mod appends its code after the end of the stock application and redirects a few places to it:

| Change | Where | What it does |
|---|---|---|
| Dispatcher hook | `src/dispatch_trampoline.S` | Sends file types 5 (FLAC), 11 (WAV) and 12 (AIFF) to the mod's adapter; everything else continues to the stock code |
| Adapter | `src/flac_adapter.c` (about 3,700 lines) | Presents each track to the player as plain stereo PCM, as the stock WAV reader would |
| 19 redirected calls | `src/pcm_route_trampolines.S` | Answer reads, seeks and end-of-file checks for the mod's tracks |
| Audio-processor FLAC | `src/chip_flac*.c`, `src/chip_flac_loader.c` | Copies the raw FLAC bytes into a ring buffer in the audio processor's free memory; small tags travel down the PCM path in place of audio; one entry of the stock converter table is pointed at a dr_flac-based converter. No instruction of the audio processor's program is changed |
| Fallback decoding | `src/dr_flac.h` | Decodes on the main processor when the audio-processor part isn't loaded, and for hi-res WAV and AIFF |
| Pacing | `src/flac_adapter.c` | Spreads decoding over each read-ahead burst so the screen doesn't stall |
| Panel guard | `src/panel_guard.c` | Hooks the 1 ms timer interrupt; if a front-panel exchange stalls (200 ms with the serial port's overrun flag set, or 2 s without), resets the port and transfer channels |
| Version label | `src/version_label.c` | Shows "PLUS V0.90" on screen; the version field stays 1.15 for the update check and LINK |

## Safety design

- The first 256 KB of the firmware (boot code and emergency updater) and the front-panel firmware stay byte-for-byte unchanged; the builder and the patcher both refuse to write a file otherwise. So the official updater can always restore stock firmware.
- Writes stop before `0x7E0000`, where the error-log flash sector starts.
- The patcher checks SHA-256 hashes at every step (input file, unpacked application, patched application, final mod, restore file) and only hands out a byte-exact copy of the tested build.
- The build is meant to be deterministic: pinned toolchains (GCC 14.2.0, binutils 2.43) plus `build.py` should reproduce the published hash.
- The web patcher makes no network calls; the only URLs in it are the GitHub issues link and the font licence.
- The restore file is tagged 1.17, so the player always accepts it.

## Concerns

- **One squashed commit.** The "70+ builds" of development aren't visible, so there is no history to audit.
- **Precompiled code in the patcher.** The patchers carry the mod's compiled bytes (`PATCH_DATA`). They can only be tied to the source by rebuilding and comparing hashes (see below).
- **Limited hardware testing:** two players; other hardware revisions are unknown.
- **Known edge cases:** 96 kHz 24-bit FLAC pitched above +50 % with MASTER TEMPO on, plus very fast jog spinning in vinyl mode, can cause short gaps or the player's emergency loop. FLAC files with 16,384-frame blocks behave similarly. ALAC, 32-bit, 176.4 kHz and 192 kHz are not supported.
- **Version lock:** the mod uses fixed addresses throughout, so it only works with firmware 1.15.
- **Warranty:** Pioneer DJ / AlphaTheta may refuse service on a modified player.

## Build check

Goal: rebuild the mod from source with the project's own toolchain scripts and compare the result with the hash the patcher is pinned to.

| Item | SHA-256 |
|---|---|
| Official firmware 1.15 `XDJ700.UPD` (input) | `73edec9802da51672257c2599efc04209dc92478fcbaa1a0425b3b122e33f99c`, matched |
| Published mod build (expected output) | `84f7f0653a4c66cf5b902edf1d837989e443ab5ab3462aa0ffed8b6530076f56` |
| Local rebuild (2026-11-09) | `84f7f0653a4c66cf5b902edf1d837989e443ab5ab3462aa0ffed8b6530076f56`, **matched** |

How it was done: both cross-compilers were built with the project's `toolchains/build_sh.sh` and `toolchains/build_c6x.sh` (GCC 14.2.0 and binutils 2.43 from ftp.gnu.org; gpg reported good signatures from the GCC and binutils maintainers), then `python3 build.py` was run on macOS. The output is byte-for-byte the published build, so the compiled code in the patcher comes from the published source.

## Security checks

Run on 2026-11-09 against the local rebuild above. The firmware comparisons used scripts written for this check, not the project's own tools.

### What the mod changes in the firmware file

| Check | Result |
|---|---|
| Boot and recovery region (first 256 KB) | **Unchanged**: 0 bytes differ below `0x40000` |
| Front-panel firmware component | **Unchanged**: byte-for-byte identical |
| Error-log flash sector (`0x7E0000` and up) | **Not written**: no data at or above it |
| S-record checksums, packed-application checksum | All valid; start address unchanged (`0xA0000000`) |
| Stock data removed | None: every stock address is still present |
| Header | Only the version tag changes, `1.15` to `1.16` |

Inside Pioneer's unpacked application (18.6 MB), **116 bytes change, in 23 places**. Each one matches a change the project documents:

| Address | Bytes | What it is |
|---|---|---|
| `0x080B8708` | 4 | 1 ms timer handler pointer, redirected to the panel guard |
| `0x080D6294`, `0x080D62A4` | 10 | The two "Ver " texts emptied for the version label |
| `0x08B74516` | 8 | The "unplayable" mark patch |
| `0x08BF6220` to `0x08BFAC34` | 19 places | The 19 redirected PCM read/seek/end-of-file calls |
| `0x08C01E78` | 12 | The jump at the playback dispatcher |
| `0x08DD1A84`, `0x08DD2FEC` | 8 | The two version-label routine pointers |

Every redirected pointer goes into the mod's own code, which is appended after the stock application (1,015,136 bytes, `0x091BD788` to `0x092B54E8`).

### The patchers

- **Regenerated from source:** running `tools/make_patcher.py` on the rebuild produced `patcher/xdj700_plus_patcher.html` and `patcher/xdj700_plus_patcher.py` byte-for-byte identical to the published ones.
- **Web page:** its Content-Security-Policy is `default-src 'none'; connect-src 'none'; form-action 'none'`, so the browser itself blocks it from loading or sending anything. No `eval`, `fetch`, storage or external resources.
- **Python script:** standard library only. It reads the file you name and writes only `XDJ700.UPD` files into its output folder. No network, no subprocess, no deletions. (`os.system("")` appears once; it's an empty call that turns on colour output in the Windows console.)

### Parsing untrusted files

The mod reads WAV, AIFF and FLAC files from USB sticks, and over LINK from other players. It runs with full access to the player's memory and there is no memory protection, so bugs in this parsing are the main risk.

- **WAV and AIFF headers** (`xdj_pcm_open`): every header read is capped to a fixed 40-byte buffer; chunk count (32), chunk sizes and the AIFF `SSND` skip field are bounds-checked; only 16/24-bit, mono/stereo, linear PCM at the expected rates is accepted, with the block alignment checked against bits and channels. Sample reads stay within fixed buffers (at most 2,048 frames of at most 6 bytes into a 12,288-byte buffer). No out-of-bounds read or write found.
- **FLAC decoding:** bundled dr_flac is **v0.13.3** (2026-01-17), the latest release. dr_flac is widely used and fuzzed upstream.
- **The mod's own FLAC seek** (`xdj_parse_header_bytes`, `xdj_scan_frames`): every header field read is checked against the bytes available; frame sizes and positions are checked against the stream info; scanning has a probe limit.
- **Audio-processor side** (`chip_flac.c`): ring-buffer reads are masked to the ring's size and refuse bytes the ring has already overwritten; the decoder's memory comes from a fixed arena that refuses oversized requests; each unit is capped at 640 frames.

**Low-severity note:** the audio processor recognises the mod's tags by bit pattern inside the PCM stream. A deliberately crafted 16-bit WAV could imitate a run of tags while a FLAC track is loaded. The worst outcome found is wrong audio or silence from that track: tag numbers are masked and reads stay inside the ring, so no memory corruption.

### The project's own test suite

`python3 -m unittest discover -s tests`, with sox, flac, ffmpeg and Node installed: **55 tests, all passed, 1 skipped**. These run the adapter, feed, converter and decoder code on the computer against models of the player's file calls and of the audio processor's memory, and compare the output with reference decodes. The one skip (`test_firmware_differential_invariants`) looks for a build file under an older name (`build/XDJ700_MOD_FLAC.UPD`); the independent firmware comparison above covers the same ground.

### Limits of these checks

- This was a focused review of the parsing paths, not a line-by-line audit of all ~10,000 lines of mod code, and not fuzzing.
- Stability under real use (the documented edge cases at high pitch and fast jog spinning) can only be tested on a player.

## Verdict

For a hobby firmware mod, it is unusually careful work: the changes are small and documented, the boot region is left alone, there are hash checks throughout, and the build is meant to be reproducible. The precompiled code in the patcher was the main open question, and the build check above settles it: a clean rebuild from source reproduces the published build exactly. What remains is the risk of any firmware flash, and the limited testing (two players).
