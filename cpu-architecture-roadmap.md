---
created: 2026-09-16T09:29:29
source: claude-code
project: /src/notes
---

Reading order, official sources only, x86-64 → ARM64:

## Stage 1 — x86-64 registers + flags (start here)
**Intel SDM (Software Developer's Manual)** — official page, free PDFs:
https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html

- **Volume 1: Basic Architecture** — read these chapters only, in order:
  - Ch 3 *Basic Execution Environment* → GPRs, RIP, RFLAGS. Core of what you asked
  - Ch 4 *Data Types*
  - Ch 6 *Procedure Calls, Interrupts, Exceptions* → stack mechanics
- Don't read Vol 1 cover-to-cover. ~100 pages total from these chapters

**Alternative (many find it more readable):** AMD64 Architecture Programmer's Manual, **Volume 1: Application Programming** (doc #24592)
https://www.amd.com/en/resources/developer-guides-manuals.html

## Stage 2 — Intel-syntax assembly practice (parallel with Stage 1)
- **NASM manual** (NASM = Intel syntax by default): https://www.nasm.us/doc/ — Ch 2–3, then write tiny Linux programs
- Toolchain setup:
  - `nasm -f elf64 x.asm && ld x.o` — assemble/run
  - `gdb` → `set disassembly-flavor intel`
  - `objdump -d -M intel ./a.out`
- **Godbolt** https://godbolt.org — write C, see Intel-syntax asm live. Best feedback loop that exists
- **pwn.college** https://pwn.college — "Assembly Crash Course" module, graded exercises
- Instruction lookup while practicing: https://www.felixcloutier.com/x86/ (HTML mirror of SDM Vol 2 — faster than the PDF)

## Stage 3 — calling convention + stack (the ABI)
- **System V AMD64 psABI** (official spec): https://gitlab.com/x86-psABIs/x86-64-ABI — build/download PDF from repo
  - Read §3.2 only: registers, argument passing, stack frame, red zone

## Stage 4 — x86-64 reference volumes (use, don't read)
- **SDM Volume 2** — full instruction set A–Z. Keep open while reversing
- **SDM Volume 3** — only when you go OS-level: Ch 2–4 (protection, paging), interrupts

## Stage 5 — ARM64 (after x86-64 feels natural)
In this order:
1. **ARM Cortex-A Series Programmer's Guide for ARMv8-A** (DEN0024A) — the readable intro, ~300 pages:
   https://developer.arm.com/documentation/den0024/latest
   - Ch 4 registers, Ch 5–6 A64 instruction set, Ch 9 ABI
2. **Learn the Architecture — A64 ISA guide** (short, modern):
   https://developer.arm.com/documentation/102374/latest
3. **AAPCS64** (ARM's calling convention, = ARM's psABI):
   https://github.com/ARM-software/abi-aa/releases → `aapcs64.pdf`
4. **ARM ARM** (DDI 0487) — 12,000+ page reference. Lookup only, never linear:
   https://developer.arm.com/documentation/ddi0487/latest

## Rule of thumb
- 2 types of docs: **guides** (read linearly: SDM Vol 1 chapters, DEN0024A) and **references** (SDM Vol 2/3, ARM ARM — open on second monitor)
- Practice ratio: 1 hour reading → 2 hours writing/reversing asm
- You know Stage 1 is done when you can explain every flag ZF/SF/CF/OF after a `cmp` + why `jle` fires

Want this saved as a note in `inbox/`?
