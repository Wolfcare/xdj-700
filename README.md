# XDJ-700 PLUS: an analysis

Notes on [lowtrustsociety/XDJ-700-PLUS](https://github.com/lowtrustsociety/XDJ-700-PLUS), an unofficial firmware mod for the Pioneer DJ XDJ-700 (release PLUS V0.90, 2026-10-30, GPL-3.0). This repository holds only this analysis: no mod code, and no Pioneer firmware.

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
| Local rebuild | pending |

## Verdict

For a hobby firmware mod, it is unusually careful work: the changes are small and documented, the boot region is left alone, there are hash checks throughout, and the build is meant to be reproducible. The main thing a user trusts is the precompiled code in the patcher, which the build check above verifies.
