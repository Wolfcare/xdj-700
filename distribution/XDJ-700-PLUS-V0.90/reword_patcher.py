#!/usr/bin/env python3
"""Reword the XDJ-700 PLUS V0.90 web patcher: text only, no code changes.

Takes the author's original xdj700_plus_patcher.html (the file from
https://github.com/lowtrustsociety/XDJ-700-PLUS/releases/tag/v0.90) and writes
a copy whose visible text is plainer, in sentence case, with jargon explained.
Every change is an exact text replacement listed below. Each must match the
expected number of times, or nothing is written, so the output is the same
for everyone who runs this on the original file.

Usage:
  python3 reword_patcher.py ORIGINAL.html OUTPUT.html

The patcher is free software by low trust society under the GNU GPL v3; this
modified copy stays under the same licence.
"""

import hashlib
import sys

ORIGINAL_SHA256 = "4c64956982c447ce4d4b97981e2d3ce2fb7eb956b74f5ad940faf3747eb38781"

# (old text, new text, how many times it must occur)
CHANGES = [
    # ---- the notice that this copy is modified (GPL section 5a)
    ("  SPDX-License-Identifier: GPL-3.0-only\n\n  The font inside",
     "  SPDX-License-Identifier: GPL-3.0-only\n\n"
     "  MODIFIED COPY, 2026-11-10, by Wolfcare: visible wording only, made by\n"
     "  reword_patcher.py from the original V0.90 release file. No code, data or\n"
     "  check was changed.\n\n  The font inside", 1),

    # ---- step 1
    ('<h2 id="input-title">1. your official firmware</h2><span>UPD</span>',
     '<h2 id="input-title">1. Add Pioneer\'s official firmware</h2><span>version 1.15</span>', 1),
    ("<strong>drop your official XDJ-700 firmware version 1.15 UPD file here, or click to choose it</strong>",
     "<strong>Drop the official XDJ-700 firmware file (XDJ700.UPD, version 1.15) here, or click to choose it</strong>", 1),
    ("<span>you have to provide your own official XDJ-700 firmware version 1.15 UPD file.</span>",
     "<span>Download it from Pioneer DJ's support site. You can drop the zip it comes in, or the XDJ700.UPD file inside it.</span>", 1),
    ('<p class="need">you will also need a FAT32 USB stick with about 18 MB free.</p>',
     '<p class="need">You will also need a USB stick formatted as FAT32, with at least 18 MB free.</p>', 1),

    # ---- step 2
    ('<h2 id="build-title">2. build</h2><span>on this computer</span>',
     '<h2 id="build-title">2. Make the mod</h2><span>on this computer</span>', 1),
    ('build the mod <span class="bracket">[&gt;]</span>',
     'Make the mod <span class="bracket">[&gt;]</span>', 2),
    ('save the zip again <span class="bracket">[&gt;]</span></button>',
     'Download the zip again <span class="bracket">[&gt;]</span></button>', 1),
    ('steps and file check <span class="bracket">[?]</span>',
     'Next steps and stick check <span class="bracket">[?]</span>', 1),

    # ---- footer
    ("<p>the mod is meant to complement the stock player, not to change it: what the player already plays still goes through Pioneer's own code, untouched.</p>",
     "<p>The mod only adds formats. Files the player already plays (MP3, AAC, WAV, AIFF) still go through Pioneer's own code, unchanged.</p>", 1),
    ("<p>everything happens locally. this page cannot load or send anything: your firmware file never leaves your computer.</p>",
     "<p>Everything happens on your computer. This page is blocked from using the internet, so your firmware file is never uploaded.</p>", 1),
    ("<p>it contains no Pioneer code, only the mod's own code and the places where it goes.</p>",
     "<p>This page contains no Pioneer code: only the mod's own code and where it goes in the firmware.</p>", 1),
    ("<p>it refuses any file that is not the official XDJ-700 firmware version 1.15 UPD file.</p>",
     "<p>It only accepts the official XDJ-700 firmware 1.15, unchanged.</p>", 1),
    ("<p>free software under the gnu general public license, version 3. it includes dr_flac by david reid (public domain or mit no attribution).</p>",
     "<p>XDJ-700 PLUS by low trust society. Free software under the GNU General Public License, version 3. Includes dr_flac by David Reid (public domain or MIT No Attribution). Wording of this copy edited by Wolfcare; the original is at github.com/lowtrustsociety/XDJ-700-PLUS.</p>", 1),
    ('<p>mod: <span class="hash" id="mod-hash"></span><br>restore: <span class="hash" id="restore-hash"></span></p>',
     '<p>Mod file: <span class="hash" id="mod-hash"></span><br>Restore file: <span class="hash" id="restore-hash"></span></p>', 1),

    # ---- the risk notice
    ('<span id="notice-title">unofficial and experimental [!]</span>',
     '<span id="notice-title">Unofficial and experimental: read before you continue [!]</span>', 1),
    ("<h3>good to know</h3>", "<h3>Known limitations</h3>", 1),
    ("<span>i have read this and accept the risk.</span>",
     "<span>I have read this and accept the risk.</span>", 1),
    ('"warning": "FLASHING FIRMWARE IS AT YOUR OWN RISK. It can leave a player unusable. There is no warranty of any kind, and no one who made or shared it is responsible for any damage or loss."',
     '"warning": "FLASHING FIRMWARE IS AT YOUR OWN RISK. It can leave a player unusable. There is no warranty, and nobody who made or shared this mod is responsible for any damage or loss."', 1),
    ('"This is not a Pioneer DJ or AlphaTheta product. They have nothing to do with it, do not support it, and may refuse service on a modified player."',
     '"Never switch the player off or remove the stick during an update. An interrupted update can leave the player unusable, as with any firmware update."', 1),
    ('"It is free software under the GNU General Public License version 3, provided as is, with no warranty of any kind."',
     '"Keep the restore file this page makes. It puts the official firmware 1.15 back."', 1),
    ('"You use it entirely at your own risk. In no case is anyone who made or shared it responsible for any damage or loss, to your player, your media, your gig or anything else."',
     '"Try it at home before you rely on it at a gig. It has run very stably on the author\'s players in sessions of up to 18 hours, but it is experimental and that does not prove it works the same on yours."', 1),
    ('"It has been tested at length on the author\'s XDJ-700s, in sessions of up to 18 hours, and has been very stable. That is not proof that it works the same on yours. Treat it as experimental, and do not rely on it for a show before you have tried it yourself at home."',
     '"The part of the player that runs updates (the boot and recovery region) and the front panel firmware are not changed, so the player\'s own update mode can always put the official firmware back."', 1),
    ('"A failed or interrupted update can leave a player unusable, as with any firmware update. Never switch the player off during an update."',
     '"This is not a Pioneer DJ or AlphaTheta product. They do not support it and may refuse service on a modified player."', 1),
    ('"The boot and recovery region and the front panel firmware stay as Pioneer made them, so the player\'s own update can always put the official firmware back."',
     '"You use it entirely at your own risk, including any damage to your player, your music or your gig."', 1),
    ('"Keep the restore file that the patcher writes, in case you want to go back to stock."',
     '"Free software under the GNU General Public License version 3, provided as is, with no warranty."', 1),
    ('"Only for the XDJ-700, and only from your own official XDJ-700 firmware version 1.15 UPD file."',
     '"Only for the XDJ-700, and only made from the official firmware 1.15."', 1),

    # ---- the next-steps box
    ('<span id="steps-title">what\'s next</span>', '<span id="steps-title">Next steps</span>', 1),
    ('<b>open the zip.</b> <span class="what">extract <code id="zip-name"></code> once it is saved. if your computer says the zip is damaged, <a href="#" id="again-link">save it again <span class="bracket">[&gt;]</span></a></span>',
     '<b>Unzip the download.</b> <span class="what">Open <code id="zip-name"></code> from your downloads. If your computer says the zip is damaged, <a href="#" id="again-link">download it again <span class="bracket">[&gt;]</span></a></span>', 1),
    ('<b>copy the mod to the stick.</b> <span class="what">copy <code>1_mod/XDJ700.UPD</code> to the top folder of a FAT32 USB stick with about 18 MB free. keep the <code>2_stock_restore</code> folder on your computer: it holds the restore file, which puts the official firmware 1.15 back.</span>',
     '<b>Copy the mod to the USB stick.</b> <span class="what">Copy the file <code>XDJ700.UPD</code> from the <code>1_mod</code> folder onto the USB stick, directly, not inside a folder. Keep the <code>2_stock_restore</code> folder safe on your computer: it is your way back to the official firmware.</span>', 1),
    ('<b>eject the stick properly, then plug it back in.</b> <span class="what">this matters for the next step: without it the computer may answer from its own memory instead of reading the stick.</span>',
     '<b>Eject the stick, then plug it back in.</b> <span class="what">This makes sure the next check reads the file really written on the stick, not a copy your computer still has in memory.</span>', 1),
    ('<b>check the file on the stick.</b> <span class="what">drag XDJ700.UPD from the stick onto this box.</span>',
     '<b>Check the file on the stick.</b> <span class="what">Drag XDJ700.UPD from the stick onto the box below.</span>', 1),
    ("<strong>drag the XDJ700.UPD from the stick here, or click to choose it</strong>",
     "<strong>Drop XDJ700.UPD from the stick here, or click to choose it</strong>", 1),
    ("<span>flash only after it is confirmed</span>",
     "<span>Only update the player once this says the file is confirmed</span>", 1),
    ('<b>flash.</b> <span class="what">with the player switched off, put the stick in. hold IN and RELOOP/EXIT, switch the player on, and keep holding until the update screen appears. wait until the update has finished and the player has restarted. DO NOT SWITCH IT OFF before that.</span>',
     '<b>Update the player.</b> <span class="what">With the player switched off, put the stick in. Hold IN and RELOOP/EXIT, switch the player on, and keep holding until the update screen appears. Wait until the update finishes and the player restarts by itself. DO NOT SWITCH IT OFF OR REMOVE THE STICK before that.</span>', 1),
    ('<b>going back to stock.</b> <span class="what">the same steps with <code>2_stock_restore/XDJ700.UPD</code>. the check in step 4 recognises that file too. both files have the same name, so keep one at a time on the stick. the update screen shows <span id="mod-tag"></span> for the mod and <span id="restore-tag"></span> for the restore file: those numbers are only there so that the player accepts the file.</span>',
     '<b>Going back to the official firmware.</b> <span class="what">Do the same steps with <code>XDJ700.UPD</code> from the <code>2_stock_restore</code> folder. The check in step 4 recognises it too. Both files have the same name, so only have one of them on the stick at a time. The update screen shows version <span id="mod-tag"></span> for the mod and <span id="restore-tag"></span> for the restore file. Those numbers are only there so the player accepts the file; the player still reports 1.15 afterwards.</span>', 1),

    # ---- status messages on the page
    ('status("official-status", "reading " + file.name + "...");', 'status("official-status", "Reading " + file.name + "...");', 1),
    ('status("official-status", "checking...");', 'status("official-status", "Checking...");', 1),
    ('status("official-status", "official XDJ-700 firmware version 1.15 UPD file detected.", "ok");',
     'status("official-status", "Official XDJ-700 firmware 1.15 found. Now press Make the mod.", "ok");', 1),
    ('status("build-status", "building the mod...");', 'status("build-status", "Making the mod...");', 1),
    ('status("build-status", "packing the firmware...");', 'status("build-status", "Packing the firmware...");', 1),
    ('status("build-status", "checking the result...");', 'status("build-status", "Checking the result...");', 1),
    ('status("build-status", "done. both files were checked: the mod is byte for byte the tested build.", "ok");',
     'status("build-status", "Done. Both files were checked, and the mod is exactly the build that was tested on the player. The zip is in your downloads.", "ok");', 1),
    ('"stopped: " + message(error).replace(/\\.$/, "") + ". nothing was saved."',
     '"Stopped: " + message(error).replace(/\\.$/, "") + ". Nothing was saved."', 1),
    ('status("check-status", "checking " + file.name + "...");', 'status("check-status", "Checking " + file.name + "...");', 1),

    # ---- answers of the stick check
    ('"confirmed: this is the tested build ("', '"Confirmed: this is the tested build of the mod ("', 1),
    ('"). safe to flash."', '"). You can use it to update the player."', 1),
    ('"confirmed: this is the restore file (the official firmware 1.15). safe to flash to go back."',
     '"Confirmed: this is the restore file (the official firmware 1.15). You can use it to go back to stock."', 1),
    ('" but it is called " + name + " on the stick: rename it to XDJ700.UPD, or the player will not see it."',
     '" But it is called " + name + " on the stick: rename it to exactly XDJ700.UPD, or the player will not find it."', 1),
    ('"this is the official firmware 1.15 as Pioneer ships it, not a file made here. to install the mod, copy 1_mod/XDJ700.UPD from the zip or folder made here; to go back to stock, copy 2_stock_restore/XDJ700.UPD."',
     '"This is Pioneer\'s official firmware 1.15, not a file made by this page. To install the mod, copy XDJ700.UPD from the 1_mod folder; to go back to stock, copy XDJ700.UPD from the 2_stock_restore folder."', 1),
    ('"this file is not right. DO NOT flash it. "', '"This file is not right. DO NOT use it to update the player. "', 1),
    ('"copy XDJ700.UPD from the zip or folder made here to the top folder of your USB stick again, eject the stick, plug it back in and try again."',
     '"Copy XDJ700.UPD from the 1_mod folder onto the stick again (directly, not inside a folder), eject the stick, plug it back in, and check again."', 1),
]


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    original = open(sys.argv[1], "rb").read()
    digest = hashlib.sha256(original).hexdigest()
    if digest != ORIGINAL_SHA256:
        sys.exit("this is not the original V0.90 patcher (sha256 %s)" % digest)
    text = original.decode("utf-8")
    for old, new, count in CHANGES:
        found = text.count(old)
        if found != count:
            sys.exit("expected %d of: %s\nfound %d; nothing written" % (count, old[:90], found))
        text = text.replace(old, new)
    out = text.encode("utf-8")
    open(sys.argv[2], "wb").write(out)
    print("%d changes applied\nsha256 %s" % (len(CHANGES), hashlib.sha256(out).hexdigest()))


if __name__ == "__main__":
    main()
