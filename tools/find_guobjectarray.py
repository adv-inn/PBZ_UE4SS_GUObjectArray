# Read-only check of PBZ.exe for the UE4SS GUObjectArray signature.
# Usage: python find_guobjectarray.py "<path to PBZ.exe>"
#
# 1. Finds every match of the wildcard signature used by UE4SS_Signatures/GUObjectArray.lua
#    and reports where they point. One single target = the signature still works.
# 2. Independently finds the most-referenced "mov rax,[rip+x]; mov rcx,[rax+rcx*8]" target,
#    which is &TUObjectArray.Objects; the FUObjectArray head is that address - 0x18.
# 3. Prints unique 7-byte fallback signatures in case the wildcard ever becomes ambiguous.
import collections, re, struct, sys

data = open(sys.argv[1], "rb").read()
pe = struct.unpack_from("<I", data, 0x3C)[0]
nsec = struct.unpack_from("<H", data, pe + 6)[0]
opt = struct.unpack_from("<H", data, pe + 20)[0]
stamp = struct.unpack_from("<I", data, pe + 8)[0]
sections = []
for i in range(nsec):
    off = pe + 24 + opt + i * 40
    vsize, va, rsize, raw = struct.unpack_from("<IIII", data, off + 8)
    chars = struct.unpack_from("<I", data, off + 36)[0]
    sections.append((va, raw, rsize, chars & 0x20000000))
exec_ranges = [(raw, raw + rsize, va) for va, raw, rsize, x in sections if x]
print(f"PE TimeDateStamp {stamp}")


def scan(pattern):
    hits = []
    for lo, hi, va in exec_ranges:
        for m in pattern.finditer(data, lo, hi):
            rva = va + m.start() - lo
            disp = struct.unpack_from("<i", data, m.start() + 3)[0]
            hits.append((m.start(), rva, rva + 7 + disp))
    return hits


wild = scan(re.compile(rb"\x48\x8B\x05....\x48\x8B\x0C\xC8\x48\x8D\x04\xD1", re.S))
wild_targets = collections.Counter(t for _, _, t in wild)
print(f"wildcard signature: {len(wild)} matches, {len(wild_targets)} distinct target(s)")
for tgt, n in wild_targets.most_common(5):
    print(f"  &Objects RVA 0x{tgt:08X} x{n}  -> head RVA 0x{tgt - 0x18:08X}")

loads = scan(re.compile(rb"\x48\x8B\x05....\x48\x8B\x0C\xC8", re.S))
if not loads:
    sys.exit("no object-array loads found; the code section may be packed")
objects = collections.Counter(t for _, _, t in loads).most_common(1)[0][0]
print(f"most-referenced &Objects: RVA 0x{objects:08X} -> head RVA 0x{objects - 0x18:08X}")

ok = len(wild_targets) == 1 and objects in wild_targets
print("RESULT:", "OK, the wildcard signature works on this build" if ok else "MISMATCH, use a fallback below")
if not ok:
    unique = (data[off:off + 7] for off, _, tgt in loads if tgt == objects)
    unique = [s for s in unique if sum(data.count(s, lo, hi) for lo, hi, _ in exec_ranges) == 1]
    for sig in unique[:5]:
        print("  fallback 7-byte signature:", " ".join(f"{b:02X}" for b in sig))
