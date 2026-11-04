# PBZ_UE4SS_GUObjectArray — UE4SS signature for Phantom Blade Zero

A `GUObjectArray` signature script that lets [UE4SS](https://github.com/UE4SS-RE/RE-UE4SS) start on **Phantom Blade Zero** again after a game update. It is designed to survive future updates.

[中文说明](#中文)

## The problem

Phantom Blade Zero runs on a modified UE 5.7.4, and UE4SS can't find `GUObjectArray` on its own. The UE4SS package used by PBZ Lua mods ships a custom `ue4ss\UE4SS_Signatures\GUObjectArray.lua` for this. That script hardcodes a single instruction, including its address offset, and the offset changes whenever the game is rebuilt.

After the 2026-11-04 game update (Steam build 26367565), that script no longer matched. UE4SS couldn't locate the object array and no Lua mods were loaded.

## The fix

This script matches the shape of the game's object-lookup code instead of one exact instruction:

```
48 8B 05 ?? ?? ?? ??   mov rax, [rip+disp]    ; &TUObjectArray.Objects
48 8B 0C C8            mov rcx, [rax+rcx*8]   ; chunk pointer
48 8D 04 D1            lea rax, [rcx+rdx*8]   ; FUObjectItem
```

On the current build this pattern matches 311 places, and all of them point to the same address. Whichever match UE4SS picks, the result is the same. The script returns the `FUObjectArray` head (`&Objects - 0x18`), which is the same value the previous script returned.

It was verified in game on build 26367565:

- `UE4SS.log` shows `GUObjectArray address: 0x14de28c50`.
- A 37-item compatibility check of the author's mods all passed.

## Which UE4SS this is for

Use this file only if your current `ue4ss\UE4SS_Signatures\GUObjectArray.lua` ends with `return ObjectsAddress - 0x18`. This means you have the UE4SS package that returns the `FUObjectArray` head.

Other UE4SS packages for this game return a different address, so **don't mix signature files between packages**. One example is the build-locked "UE4SS For Phantom Blade Zero" package. If you use one of those, wait for its author to update it.

## Installation

1. Back up `PBZ\platform\steam\ue4ss\UE4SS_Signatures\GUObjectArray.lua`.
2. Replace it with `UE4SS_Signatures\GUObjectArray.lua` from this repository.
3. Start the game. `ue4ss\UE4SS.log` should contain a line starting with `GUObjectArray address:`.

## After the next game update

Check whether the signature still works, without starting the game (needs Python 3, reads the file only):

```
python tools/find_guobjectarray.py "<path to PBZ.exe>"
```

`RESULT: OK` means the signature still works. Otherwise the tool prints fallback 7-byte signatures to use in `Register()`.

## Mods by the same author

- Undying Heroic Spirit Memory Flower Fix: https://www.nexusmods.com/phantombladezero/mods/259

## License

[MIT](LICENSE) © 2026 M4kis3Kurisu

This is an unofficial fan-made file. It is not affiliated with or endorsed by the developers of Phantom Blade Zero or by the UE4SS project.

---

## 中文

适用于《影之刃零》的 UE4SS `GUObjectArray` 签名脚本。游戏更新后 UE4SS 失效时，用它可以让 UE4SS 重新正常启动，以后游戏再更新也尽量不失效。

**问题**：《影之刃零》使用魔改的 UE 5.7.4，UE4SS 自己找不到 `GUObjectArray`。PBZ Lua mod 常用的那套 UE4SS 为此附带了一个自定义的 `ue4ss\UE4SS_Signatures\GUObjectArray.lua`。但这个脚本把某一条指令写死了，连同里面的地址偏移，而每次游戏重新编译这个偏移都会变。2026-11-04 游戏更新（Steam build 26367565）后它匹配不到了，UE4SS 定位不到对象表，所有 Lua mod 都无法加载。

**修复**：本脚本不再写死某一条指令，而是匹配游戏查找对象那段代码的“形状”，把偏移部分换成通配符。当前版本共有 311 处匹配，全部指向同一个地址，所以不管 UE4SS 取到哪一处，结果都一样。返回值是 `FUObjectArray` 头（`&Objects - 0x18`），和原脚本返回的是同一个值。已在 build 26367565 上实测：

- 日志显示 `GUObjectArray address: 0x14de28c50`；
- 作者 mod 的 37 项兼容性检查全部通过。

**适用范围**：只有当你现在的 `ue4ss\UE4SS_Signatures\GUObjectArray.lua` 以 `return ObjectsAddress - 0x18` 结尾时才适用，说明你装的是返回 `FUObjectArray` 头的那套 UE4SS。其他 UE4SS 整合包返回的地址不同，**不要把签名文件拿去混用**，例如锁定游戏版本的「UE4SS For Phantom Blade Zero」。用这类整合包的话，请等它的作者更新。

**安装**：

1. 备份 `PBZ\platform\steam\ue4ss\UE4SS_Signatures\GUObjectArray.lua`。
2. 用本仓库的 `UE4SS_Signatures\GUObjectArray.lua` 替换它。
3. 启动游戏，`ue4ss\UE4SS.log` 中应出现以 `GUObjectArray address:` 开头的一行。

**下次游戏更新后**：不用启动游戏，就能检查签名是否仍然有效。需要 Python 3，工具只读取文件，不做修改：

```
python tools/find_guobjectarray.py "<PBZ.exe 路径>"
```

输出 `RESULT: OK` 表示签名仍然有效；否则工具会给出可替换到 `Register()` 中的 7 字节备用签名。

**同作者的 mod**：不灭侠胆记忆修复 https://www.nexusmods.com/phantombladezero/mods/259

**许可证**：[MIT](LICENSE) © 2026 M4kis3Kurisu。本文件为非官方玩家作品，与《影之刃零》开发商及 UE4SS 项目无关。
