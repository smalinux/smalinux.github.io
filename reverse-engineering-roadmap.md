# Reverse Engineering Roadmap

## Foundations

1. ELF format
2. Understand program execution and program load
3. Stack & functions
4. Assembly
5. C language — most RE targets compiled C/C++. Read C, know how compilers translate it
6. Memory layout — heap, stack, globals, virtual memory, paging, ASLR
7. Calling conventions — SysV, stdcall, fastcall, how args/returns pass
8. CPU architecture — registers, flags, x86-64 first, then ARM64
9. Endianness, data types, structs in memory, alignment/padding

## Tooling

10. Disassemblers — Ghidra (free), IDA, Binary Ninja
11. Debuggers — GDB (+ pwndbg/GEF), x64dbg on Windows
12. `objdump`, `readelf`, `strings`, `nm`, `ltrace`, `strace`, `xxd`
13. Radare2/rizin — optional but good for scripting
14. Hex editors, patching binaries

## Core skills

15. Decompiler output reading — map pseudo-C back to asm
16. Recognize compiler patterns — loops, switch tables, inlined memcpy, optimizations
17. Static vs dynamic analysis — when to use each
18. Symbol stripping — RE without function names
19. Linking & loading — PLT/GOT, relocations, dynamic linker, `LD_PRELOAD`

## Intermediate

20. C++ RE — vtables, name mangling, STL patterns
21. Anti-debugging & obfuscation — detect + bypass (packers, `ptrace` tricks)
22. File formats beyond ELF — PE (Windows), Mach-O, firmware blobs
23. Syscalls & OS internals — Linux syscall table, kernel/user boundary
24. Crypto identification — spot AES/RSA/XOR constants in binaries

## Advanced / specialization

25. Vulnerability basics — buffer overflow, format string, UAF (helps understand what you read)
26. Scripting for RE — Python + Ghidra scripting / Capstone / pwntools
27. Emulation — QEMU, Unicorn engine
28. Symbolic execution — angr (optional, powerful)
29. Malware analysis OR embedded/firmware OR game hacking — pick a track

## Practice

- crackmes.one, picoCTF, pwn.college, Nightmare (guyinatuxedo) — do these in parallel from day 1, not after theory

Order matters less than practice volume. Your 1–4 + C + GDB + Ghidra = enough to start crackmes today.
