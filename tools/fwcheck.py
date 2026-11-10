#!/usr/bin/env python3
"""fwcheck: compare an official Pioneer DJ firmware file with a modified one.

Shows what a firmware mod actually changes, without trusting the mod's own
tools: whether the boot/recovery region and the front-panel firmware are
untouched, how many places in the stock code are edited, and whether new
code went into empty space or over stock content.

Supported files:
  XDJ-700   XDJ700.UPD   (MAIN + PANEL container, S-records, LZSS application)
  CDJ-2000  C2KMAIN.UPD  (S-records, LZSS application)
            C2KGUI.UPD   (raw image)

Usage:
  python3 fwcheck.py OFFICIAL.UPD MODIFIED.UPD
  python3 fwcheck.py --identify FILE.UPD [FILE.UPD ...]

Python 3.8 or later, standard library only. Reads the two files and writes
nothing. It does not judge whether a mod's code is safe: it only shows where
the changes are.
"""

import argparse
import hashlib
import sys

# Files with a known identity, by SHA-256.
KNOWN = {
    "73edec9802da51672257c2599efc04209dc92478fcbaa1a0425b3b122e33f99c": "XDJ-700 official firmware 1.15",
    "84f7f0653a4c66cf5b902edf1d837989e443ab5ab3462aa0ffed8b6530076f56": "XDJ-700 PLUS V0.90 mod (low trust society)",
    "d71006018c8e2889be5517b0b1c853cea92b6373196c8c2f7040c25c822b0a09": "XDJ-700 PLUS V0.90 stock restore file",
    "49f7efcd08e5eae3678a438d3af49e03608aacb11838180fa67faa81132c11fb": "CDJ-2000 official MAIN 4.33",
    "93d59ab81ece45e684a6d1228cf6b5a557a53e0baf29dfb03725ab1ef2b20c78": "CDJ-2000 official GUI 4.20",
    "cfc86dc0f0e6bc48373fca4bee0acf4a421f29823c96fbd249549e528ad5a9e4": "CDJ-2000 Raft Tone v1.1 MAIN",
    "c61ebb87ebf9285bb420946f479a62fb67ccb9027a1bd9bf5f929049091de023": "CDJ-2000 Raft Tone v1.1 GUI",
    "a6a5e99da35f42289f5817b4948c756478742452cf1f5c21a2573293edaa8a76": "CDJ-2000 Raft Tone v1.1 way-back GUI",
}

BOOT_END = 0x40000            # boot code and emergency updater: the first 256 KB of a MAIN image
APP_OFFSET = 0x40000          # the packed application starts here in a MAIN image
APP_BASE = 0x08000000         # where the application runs, for readable addresses
XDJ_FLASH_END = 0x7E0000      # XDJ-700: the error log's flash sector starts here
SMALL_EDIT = 64               # a change of at most this many bytes counts as a small edit (a hook)
ADDRESS_BYTES = {"1": 2, "2": 3, "3": 4}

GREEN, RED, YELLOW, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[0m"
COLOUR = sys.stdout.isatty()


def mark(kind, text):
    colours = {"PASS": GREEN, "FAIL": RED, "NOTE": YELLOW, "INFO": ""}
    tag = "[%s]" % kind
    if COLOUR and colours[kind]:
        tag = colours[kind] + tag + RESET
    print("  %-6s %s" % (tag, text))


def sha256(data):
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------- file formats

def detect(data):
    """Return (kind, parts): kind is 'xdj700', 'cdj-main' or 'cdj-gui'."""
    if data.startswith(b"CDJ-2000 MAIN"):
        return "cdj-main", {"MAIN": data}
    if data.startswith(b"CDJ-2000 GUI"):
        return "cdj-gui", {"GUI": data}
    try:
        first, second, rest = data.split(b"\r\n", 2)
        a, b = int(first), int(second)
    except ValueError:
        raise SystemExit("not a supported firmware file (XDJ700.UPD, C2KMAIN.UPD or C2KGUI.UPD)")
    if a + b != len(rest) or not rest.startswith(b"XDJ-700"):
        raise SystemExit("XDJ-700 container is damaged or not an XDJ-700 file")
    return "xdj700", {"MAIN": rest[:a], "PANEL": rest[a:]}


def parse_srecords(component):
    """A 32-byte text header, then S-records. Returns header, {address: byte}, bad checksum count, entry."""
    start = component.index(b"S0")
    header = component[:start]
    memory, bad, entry = {}, 0, None
    for line in component[start:].split(b"\r\n"):
        if not line.startswith(b"S"):
            continue  # an empty line, or the component's 2-byte trailer
        raw = bytes.fromhex(line[2:].decode("ascii"))
        if raw[0] != len(raw) - 1:
            raise SystemExit("S-record length mismatch")
        if sum(raw) & 0xFF != 0xFF:
            bad += 1
        kind = chr(line[1])
        if kind in ADDRESS_BYTES:
            size = ADDRESS_BYTES[kind]
            address = int.from_bytes(raw[1:1 + size], "big")
            for offset, value in enumerate(raw[1 + size:-1]):
                if address + offset in memory:
                    raise SystemExit("overlapping S-records at %#x" % (address + offset))
                memory[address + offset] = value
        elif kind in "789":
            entry = int.from_bytes(raw[1:-1], "big")
    return header, memory, bad, entry


def flat(memory):
    image = bytearray(b"\xff" * (max(memory) + 1))
    for address, value in memory.items():
        image[address] = value
    return bytes(image)


def unlzss(source):
    """Okumura-style LZSS: 4 KB ring, 18-byte matches, flag bits LSB first."""
    ring = bytearray(b" " * 4078 + b"\0" * 18)
    cursor, output, position = 4078, bytearray(), 0
    while position < len(source):
        flags = source[position]
        position += 1
        for bit in range(8):
            if position >= len(source):
                break
            if flags >> bit & 1:
                value = source[position]
                position += 1
                output.append(value)
                ring[cursor] = value
                cursor = (cursor + 1) & 0xFFF
            else:
                if position + 2 > len(source):
                    raise SystemExit("LZSS data is truncated")
                low, high = source[position], source[position + 1]
                position += 2
                where, length = low | (high & 0xF0) << 4, (high & 0x0F) + 3
                for index in range(length):
                    value = ring[(where + index) & 0xFFF]
                    output.append(value)
                    ring[cursor] = value
                    cursor = (cursor + 1) & 0xFFF
    return bytes(output)


def application(image):
    """Little-endian length, LZSS data, little-endian 16-bit sum. Returns (app, checksum_ok)."""
    length = int.from_bytes(image[APP_OFFSET:APP_OFFSET + 4], "little")
    end = APP_OFFSET + 4 + length
    if end + 2 > len(image):
        raise SystemExit("packed application runs past the image")
    stored = int.from_bytes(image[end:end + 2], "little")
    ok = stored == sum(image[APP_OFFSET:end]) & 0xFFFF
    return unlzss(image[APP_OFFSET + 4:end]), ok


# ---------------------------------------------------------------- comparing

def changed_ranges(a, b, gap=3):
    """Byte ranges where a and b differ; ranges closer than gap are joined."""
    ranges = []
    for index in range(min(len(a), len(b))):
        if a[index] != b[index]:
            if ranges and index <= ranges[-1][1] + gap:
                ranges[-1][1] = index
            else:
                ranges.append([index, index])
    return ranges


def what_was_there(chunk):
    if chunk.count(0xFF) == len(chunk):
        return "empty (FF)"
    if chunk.count(0) == len(chunk):
        return "empty (00)"
    return "stock content"


def summarise_changes(stock, mod, base, label, verbose):
    ranges = changed_ranges(stock, mod)
    small = [r for r in ranges if r[1] - r[0] + 1 <= SMALL_EDIT]
    large = [r for r in ranges if r[1] - r[0] + 1 > SMALL_EDIT]
    small_bytes = sum(e - s + 1 for s, e in small)
    into_empty = sum(e - s + 1 for s, e in large if what_was_there(stock[s:e + 1]) != "stock content")
    over_stock = sum(e - s + 1 for s, e in large if what_was_there(stock[s:e + 1]) == "stock content")
    appended = max(0, len(mod) - len(stock))

    mark("INFO", "%s: %d bytes stock, %d bytes modified" % (label, len(stock), len(mod)))
    mark("INFO", "small edits (hooks, values): %d places, %d bytes" % (len(small), small_bytes))
    if into_empty:
        mark("INFO", "new data in space that was empty: %d bytes" % into_empty)
    if appended:
        mark("INFO", "new data appended after the stock image: %d bytes" % appended)
    if over_stock:
        mark("NOTE", "larger blocks written over stock content: %d bytes (check what they replace)" % over_stock)
    else:
        mark("PASS", "no larger block overwrites stock content")
    if len(mod) < len(stock):
        mark("FAIL", "the modified image is shorter: %d stock bytes are gone" % (len(stock) - len(mod)))
    if verbose:
        for s, e in ranges:
            kind = "edit" if e - s + 1 <= SMALL_EDIT else what_was_there(stock[s:e + 1])
            print("         %#010x..%#010x %7d bytes  %-14s %s -> %s" % (
                base + s, base + e, e - s + 1, kind, stock[s:s + 8].hex(), mod[s:s + 8].hex()))


def compare_main(stock, mod, xdj, verbose):
    sh, smem, sbad, sentry = parse_srecords(stock)
    mh, mmem, mbad, mentry = parse_srecords(mod)
    mark("INFO", "header: %s -> %s" % (sh.decode("ascii", "replace").strip("\0 "), mh.decode("ascii", "replace").strip("\0 ")))
    mark("PASS" if mbad == 0 else "FAIL", "S-record checksums: %d bad" % mbad)
    mark("PASS" if sentry == mentry else "FAIL", "start address: %#x -> %#x" % (sentry, mentry))

    boot = sum(1 for a in range(BOOT_END) if smem.get(a) != mmem.get(a))
    mark("PASS" if boot == 0 else "FAIL", "boot and recovery region (first 256 KB): %s" % (
        "unchanged" if boot == 0 else "%d bytes changed" % boot))
    missing = sum(1 for a in smem if a not in mmem)
    mark("PASS" if missing == 0 else "FAIL", "stock addresses missing from the mod: %d" % missing)
    if xdj:
        high = sum(1 for a in mmem if a >= XDJ_FLASH_END)
        mark("PASS" if high == 0 else "FAIL", "error-log sector (0x7E0000 and up): %s" % (
            "not written" if high == 0 else "%d bytes written" % high))

    sapp, sok = application(flat(smem))
    mapp, mok = application(flat(mmem))
    mark("PASS" if sok and mok else "FAIL", "packed application checksum: stock %s, mod %s" % (
        "ok" if sok else "BAD", "ok" if mok else "BAD"))
    summarise_changes(sapp, mapp, APP_BASE, "unpacked application", verbose)


def compare_raw(stock, mod, verbose):
    mark("INFO", "header: %s -> %s" % (stock[:32].decode("ascii", "replace").strip(), mod[:32].decode("ascii", "replace").strip()))
    ranges = changed_ranges(stock, mod)
    first = ranges[0][0] if ranges else None
    # A raw image keeps its version text and a 2-byte checksum in its last 34 bytes.
    beyond_header = [r for r in ranges if r[1] >= 32 and r[0] < len(stock) - 34]
    if beyond_header:
        mark("INFO", "first change after the header at offset %#x; everything before it is unchanged" % beyond_header[0][0])
    elif first is not None:
        mark("PASS", "only the header (version) and the checksum trailer differ")
    summarise_changes(stock, mod, 0, "image", verbose)


def identify(path, data):
    digest = sha256(data)
    print("%s\n  sha256 %s\n  %s" % (path, digest, KNOWN.get(digest, "not a file fwcheck knows")))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[1], formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="+", help="OFFICIAL.UPD MODIFIED.UPD, or files to identify")
    parser.add_argument("--identify", action="store_true", help="only print each file's SHA-256 and what it is")
    parser.add_argument("-v", "--verbose", action="store_true", help="list every changed place")
    args = parser.parse_args(argv)

    if args.identify:
        for path in args.files:
            identify(path, open(path, "rb").read())
        return 0
    if len(args.files) != 2:
        parser.error("give two files: the official one first, then the modified one")

    stock_path, mod_path = args.files
    stock, mod = open(stock_path, "rb").read(), open(mod_path, "rb").read()
    for path, data in ((stock_path, stock), (mod_path, mod)):
        identify(path, data)
    skind, sparts = detect(stock)
    mkind, mparts = detect(mod)
    if skind != mkind:
        raise SystemExit("the two files are of different kinds (%s, %s)" % (skind, mkind))
    if stock == mod:
        print("\nThe files are identical.")
        return 0

    for name in sparts:
        print("\n== %s ==" % name)
        s, m = sparts[name], mparts[name]
        if s == m:
            mark("PASS", "byte-for-byte unchanged")
        elif skind in ("xdj700", "cdj-main") and name == "MAIN":
            compare_main(s, m, skind == "xdj700", args.verbose)
        elif name == "PANEL":
            mark("FAIL", "the front-panel firmware is changed")
            compare_raw(s, m, args.verbose)
        else:
            compare_raw(s, m, args.verbose)
    print("\nfwcheck shows where a mod changes the firmware, not whether its code is safe.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
