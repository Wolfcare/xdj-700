XDJ-700 PLUS V0.90: verification package
=========================================

An unofficial firmware mod for the Pioneer DJ XDJ-700 that adds FLAC
(16/24-bit, up to 96 kHz) and hi-res WAV/AIFF playback. Made by
"low trust society", not by Pioneer DJ / AlphaTheta.

    Source:  https://github.com/lowtrustsociety/XDJ-700-PLUS
    Commit:  154d6dcff2f300ea88eafe750355cf98507890d7  (release PLUS V0.90)

Flashing firmware is at your own risk. It is unofficial, tested on only a
couple of players, and Pioneer may refuse warranty service on a modified
player. Nothing in this package can promise it is safe for your player.

This package is set up so you don't have to trust the person who gave it to
you. Everything below can be checked independently.


WHAT IS IN THIS FOLDER
----------------------

  xdj700_plus_patcher_reworded.html  The patcher with clearer wording.
                                     Start here.
  xdj700_plus_patcher.html           The author's original patcher,
                                     unchanged
  xdj700_plus_patcher.py             The author's patcher as a Python 3
                                     script, unchanged
  reword_patcher.py                  Turns the original page into the
                                     reworded one (text only)
  fwcheck.py                         Shows what any modified firmware file
                                     changes compared with the official one
  LICENSE                            GNU GPL v3
  SHA256SUMS.txt                     Hashes of the files above
  VERIFICATION_REPORT.md             The checks that were run, and their
                                     results
  READ_ME_FIRST.txt                  This file

There is NO Pioneer firmware in here. You download the official firmware
yourself, and the patcher modifies it on your own computer.

Both web pages make exactly the same files. The reworded one only explains
things more plainly: same code, same checks, same result.


STEP 1: CHECK THE PATCHER IS THE PUBLISHED ONE
----------------------------------------------

macOS / Linux, in a terminal inside this folder:

    shasum -a 256 -c SHA256SUMS.txt

Windows (PowerShell), inside this folder:

    Get-FileHash * -Algorithm SHA256

Then don't trust SHA256SUMS.txt either. The easiest independent check is the
author's release page:

    https://github.com/lowtrustsociety/XDJ-700-PLUS/releases/tag/v0.90

GitHub shows a sha256 next to xdj700_plus_patcher.html there. It must be:

    4c64956982c447ce4d4b97981e2d3ce2fb7eb956b74f5ad940faf3747eb38781

You can also compare against the copies in the project's own repository at
the commit above:

    https://github.com/lowtrustsociety/XDJ-700-PLUS/blob/154d6dcff2f300ea88eafe750355cf98507890d7/patcher/xdj700_plus_patcher.html
    https://github.com/lowtrustsociety/XDJ-700-PLUS/blob/154d6dcff2f300ea88eafe750355cf98507890d7/patcher/xdj700_plus_patcher.py

Download them (the "Raw" button) and hash them the same way. If any hash
differs, stop and don't use this package.

To check the reworded page, make it yourself from the original:

    python3 reword_patcher.py xdj700_plus_patcher.html my_copy.html

It refuses anything but the original release file, and prints the hash of
the page it makes. That must be:

    c5054fc2f402826b0d809f427463f7da8215ea1561f2762bdf515b6139251f38

reword_patcher.py is short and readable: every change is an exact text
replacement listed in it, and none touches the page's code. If you'd rather
not trust it at all, use the original page instead.


STEP 2: GET THE OFFICIAL FIRMWARE YOURSELF
------------------------------------------

Download the XDJ-700 firmware version 1.15 from Pioneer DJ's support site
(pioneerdj.com, Support, Software & Firmware Updates, XDJ-700). Unzip it to
get XDJ700.UPD. Its SHA-256 must be:

    73edec9802da51672257c2599efc04209dc92478fcbaa1a0425b3b122e33f99c

The patcher checks this too and refuses any other file.


STEP 3: MAKE THE MOD
--------------------

Open xdj700_plus_patcher_reworded.html in a browser and drop your
XDJ700.UPD on it. Press "Make the mod", read the notice, tick the box and
press "Make the mod" again. It saves a zip with:

    1_mod/XDJ700.UPD             the mod
    2_stock_restore/XDJ700.UPD   official 1.15 again, to go back

Expected hashes of the results:

    mod      84f7f0653a4c66cf5b902edf1d837989e443ab5ab3462aa0ffed8b6530076f56
    restore  d71006018c8e2889be5517b0b1c853cea92b6373196c8c2f7040c25c822b0a09

The page only hands out the mod if it matches the first hash exactly.

The web page cannot go online: its Content-Security-Policy blocks all
network access, so your firmware never leaves your computer. You can test
this by switching off Wi-Fi before opening it.

If you prefer the terminal:

    python3 xdj700_plus_patcher.py /path/to/XDJ700.UPD

Optional: see for yourself what the mod changes.

    python3 fwcheck.py /path/to/official/XDJ700.UPD 1_mod/XDJ700.UPD

It should show the boot and recovery region and the front panel firmware
unchanged, 23 small edits to Pioneer's code, and the mod's own code added
after it.


STEP 4: UPDATE THE PLAYER
-------------------------

1. Keep 2_stock_restore/XDJ700.UPD safe, ideally on a second USB stick.
2. Copy XDJ700.UPD from the 1_mod folder onto a FAT32 USB stick, directly,
   not inside a folder.
3. Player off. Insert the stick. Hold IN + RELOOP/EXIT, switch on, keep
   holding until the update screen appears.
4. Wait until it restarts by itself. Never cut the power or remove the
   stick during an update.

UTILITY then shows PLUS V0.90. To go back to stock, do the same with the
restore file.


CREDITS
-------

XDJ-700 PLUS, including both patchers in this folder, is the work of
low trust society. They designed, built and tested it. This package passes
their patcher on unchanged, plus a copy with reworded text, a review, and
ways to check it.

    Project:   https://github.com/lowtrustsociety/XDJ-700-PLUS
    Support:   https://ko-fi.com/lowtrustsociety
    Bugs:      https://github.com/lowtrustsociety/XDJ-700-PLUS/issues

FLAC decoding uses dr_flac by David Reid. The XDJ-700 and its firmware are
Pioneer DJ / AlphaTheta's; neither is involved with this mod.

Verification package, reworded page, fwcheck.py and review: Wolfcare.


THE STRONGEST CHECK: BUILD IT YOURSELF
--------------------------------------

The build is deterministic. With the project's own toolchain scripts and
your own 1.15 file:

    git clone https://github.com/lowtrustsociety/XDJ-700-PLUS
    cd XDJ-700-PLUS
    git checkout 154d6dcff2f300ea88eafe750355cf98507890d7
    mkdir -p firmware/original
    cp /path/to/XDJ700.UPD firmware/original/
    sh toolchains/build_sh.sh        # about 20 minutes
    sh toolchains/build_c6x.sh       # about 20 minutes
    python3 build.py
    shasum -a 256 build/XDJ700.UPD   # must be 84f7f065...

That was done on 2026-11-09 and matched. See VERIFICATION_REPORT.md.
