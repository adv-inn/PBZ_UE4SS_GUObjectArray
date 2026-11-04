-- GUObjectArray signature for Phantom Blade Zero (UE4SS custom signature script)
-- Author: M4kis3Kurisu, License: MIT
--
-- Phantom Blade Zero uses a modified UE 5.7.4 where UE4SS's automatic scan cannot find
-- GUObjectArray, so a custom signature is required. Hardcoding the rip-relative
-- displacement breaks on every game update. This version wildcards the displacement and
-- matches only the shape of the object-lookup code:
--
--   48 8B 05 ?? ?? ?? ??   mov rax, [rip+disp]       ; &TUObjectArray.Objects
--   48 8B 0C C8            mov rcx, [rax+rcx*8]      ; chunk pointer
--   48 8D 04 D1            lea rax, [rcx+rdx*8]      ; FUObjectItem
--
-- Verified on the 2026-11-04 build: all 311 matches of this shape point to the same
-- address (&Objects = RVA 0xDE28C68), so whichever match UE4SS takes, the result is the same.
-- The FUObjectArray head is &Objects - 0x18 (TUObjectArray at +0x10, Objects at +0x08).

function Register()
    return "48 8B 05 ?? ?? ?? ?? 48 8B 0C C8 48 8D 04 D1"
end

function OnMatchFound(MatchAddress)
    local Offset = DerefToInt32(MatchAddress + 3)
    local ObjectsAddress = MatchAddress + 7 + Offset
    return ObjectsAddress - 0x18
end
