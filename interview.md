# Embedded-C Interview Question Bank (120+)

A consolidated reference of the embedded-C knowledge questions that recur across Arm, Snap, Qualcomm, Apple, NXP, and most firmware/embedded-Linux roles. Each question has a concise answer for fast review. Read the question, try to answer out loud, then check.

> **How to use:** Don't just read. Cover the answer, say yours aloud, then compare. The interview tests whether you can *explain* these, not recognize them.

---

## A. Data types, storage & qualifiers

**1. What are the typical sizes of `char`, `short`, `int`, `long`, `long long`?**
Implementation-defined, but commonly 1, 2, 4, 4/8, 8 bytes. The standard only guarantees `char` ≥ 8 bits, `short`/`int` ≥ 16, `long` ≥ 32, `long long` ≥ 64, and `sizeof(char) == 1`. On embedded targets `int` may be 16 bits.

**2. Why use fixed-width types like `uint8_t`, `int32_t`?**
Portability and predictability. Register widths and protocol fields need exact sizes; `int` varies by platform. They live in `<stdint.h>`.

**3. What's the difference between `signed` and `unsigned`, and what's the danger of mixing them?**
Unsigned can't be negative and wraps modulo 2^N; signed overflow is undefined behavior. Mixing in comparisons triggers implicit conversion — e.g. `-1 < 1u` is *false* because `-1` converts to a huge unsigned value.

**4. What is integer promotion?**
In expressions, types smaller than `int` (e.g. `char`, `short`) are promoted to `int` before the operation. This surprises people in bit operations on `uint8_t`.

**5. What does `static` mean? (two meanings)**
At file scope: internal linkage — the symbol is private to the translation unit. At block scope: the variable has static storage duration (persists across calls) but local visibility.

**6. What does `const` mean, and what does `const` on a pointer modify?**
`const` marks a value read-only. Position matters: `const int *p` = pointer to const data (data immutable, pointer movable); `int *const p` = const pointer (pointer fixed, data mutable); `const int *const p` = both fixed.

**7. What is `volatile` and when must you use it?**
It tells the compiler the variable may change outside normal program flow, so it must re-read from memory on every access (no caching in registers, no optimizing away). Use for: memory-mapped hardware registers, variables modified by an ISR, and flags shared between execution contexts.

**8. What does `const volatile` together mean?**
The program won't write it, but hardware might change it — e.g. a read-only status register. The compiler must re-read each access yet reject program writes.

**9. What is `register`, and is it still useful?**
A hint to keep a variable in a CPU register. Largely obsolete — modern compilers allocate registers better than the hint. You also can't take the address of a `register` variable.

**10. What is `extern`?**
Declares a symbol defined in another translation unit — it provides a declaration without allocating storage, resolved at link time.

**11. What's the difference between declaration and definition?**
A declaration introduces a name/type (no storage); a definition allocates storage / provides the body. You can declare many times, define once.

**12. What is the storage duration of a string literal, and can you modify it?**
Static storage duration; it lives for the program's lifetime. Modifying a string literal is undefined behavior — they're often in read-only memory.

**13. Difference between `++i` and `i++` performance-wise on embedded?**
For built-in `int` types they're identical after optimization. The historical claim that `++i` is faster matters mainly for C++ iterators/objects, not plain C scalars.

**14. What does `typedef` do, and how does it differ from `#define`?**
`typedef` creates a type alias handled by the compiler (respects scope, type-checked). `#define` is textual preprocessor substitution with no type awareness — error-prone for types (e.g. `#define PINT int*` then `PINT a, b;` makes only `a` a pointer).

---

## B. Pointers

**15. What is a pointer?**
A variable that stores a memory address. Its type tells the compiler how to interpret the pointed-to data and how pointer arithmetic scales.

**16. What is a null pointer vs an uninitialized (wild) pointer vs a dangling pointer?**
Null points to nothing (address 0, well-defined). Wild is uninitialized — points anywhere, undefined behavior. Dangling pointed to valid memory that has since been freed or gone out of scope.

**17. What is pointer arithmetic and how does it scale?**
Adding 1 to a `T*` advances by `sizeof(T)` bytes, not 1 byte. `p + n` = address + `n * sizeof(T)`.

**18. What is a `void *`?**
A generic pointer that can hold any object address. You can't dereference it directly or do arithmetic on it without casting; used by `malloc`, `memcpy`, generic APIs.

**19. What is a function pointer? Write its syntax.**
A pointer holding a function's address, enabling callbacks/jump tables. `int (*fp)(int, int) = &add;` then `fp(2, 3);`. Common in driver dispatch tables and RTOS callbacks.

**20. What is a pointer to a pointer (`**`) used for?**
To modify a pointer through a function (pass its address), or for dynamically allocated 2D arrays / arrays of strings.

**21. What's the difference between an array and a pointer?**
An array name is not a modifiable pointer — it's the block of elements (decays to a pointer to its first element in most expressions). `sizeof` an array gives total bytes; `sizeof` a pointer gives pointer size. Arrays can't be reassigned.

**22. What is array decay?**
When passed to a function, an array "decays" to a pointer to its first element — size information is lost, which is why you pass length separately.

**23. What is a `const` pointer to `volatile` data — when would you see it?**
`volatile int *const p` — a fixed pointer (e.g. to a fixed hardware register address) whose target may change in hardware. Extremely common for memory-mapped registers.

**24. How do you access a hardware register at a fixed address in C?**
Cast the address to a `volatile` pointer: `#define REG (*(volatile uint32_t *)0x40021000)` then read/write `REG`.

**25. What's wrong with returning the address of a local variable?**
The local lives on the stack and is destroyed when the function returns — the returned pointer dangles. Return heap memory, a static, or an out-parameter instead.

**26. What is the difference between `p++`, `*p++`, `(*p)++`, and `*++p`?**
`p++`: increment the pointer. `*p++`: dereference then increment pointer (`*` and postfix `++` — value is `*p`, then `p` moves). `(*p)++`: increment the pointed-to value. `*++p`: pre-increment pointer then dereference.

---

## C. Memory management & layout

**27. Describe the memory layout of a C program.**
Typically: text/code (read-only), initialized data (`.data`), uninitialized data (`.bss`, zeroed at startup), heap (grows up), stack (grows down). On embedded, also flash vs RAM mapping.

**28. Stack vs heap — differences?**
Stack: automatic, fast, LIFO, limited size, freed on scope exit. Heap: manual (`malloc`/`free`), flexible lifetime, slower, fragmentable, must be freed explicitly.

**29. Why is dynamic allocation (`malloc`) often avoided in embedded systems?**
Non-determinism (allocation time varies), heap fragmentation, risk of failure/leaks with no OS to recover, and limited RAM. Many systems use static allocation or fixed memory pools instead.

**30. `malloc` vs `calloc` vs `realloc`?**
`malloc(n)`: n bytes, uninitialized. `calloc(count, size)`: zero-initialized block. `realloc(p, n)`: resize an existing block, possibly moving it (returns new pointer; assign to a temp to avoid losing the original on failure).

**31. What happens if you `free` twice or `free` a non-heap pointer?**
Undefined behavior — typically heap corruption or a crash. Set pointers to `NULL` after freeing to make double-free safe (free(NULL) is a no-op).

**32. What is a memory leak and how do you detect one?**
Allocated memory never freed; usable memory shrinks over time. Detect with Valgrind, AddressSanitizer (`-fsanitize=address`), or static analysis.

**33. What is memory alignment and why does it matter?**
Data must often sit at addresses that are multiples of its size; misaligned access is slow or faults on some architectures (e.g. ARM). The compiler inserts padding to satisfy alignment.

**34. What is structure padding? How do you minimize it?**
Compilers insert unused bytes so members are aligned, enlarging the struct. Minimize by ordering members largest-to-smallest, or use `#pragma pack` / `__attribute__((packed))` (with a performance caveat).

**35. What does `__attribute__((packed))` do and what's the risk?**
Removes padding so the struct is as small as possible — used for wire/register layouts. Risk: unaligned member access, which is slow or faults on strict-alignment CPUs.

**36. What is a memory pool / fixed-block allocator and why use one?**
Pre-allocated fixed-size blocks handed out and returned in O(1) with no fragmentation and deterministic timing — ideal for embedded where `malloc` is risky.

**37. What is the difference between `.data` and `.bss`?**
`.data` holds initialized globals/statics (values stored in flash, copied to RAM at startup). `.bss` holds zero/uninitialized ones (no storage in the image — just zeroed at startup), saving flash space.

**38. What does the startup code do before `main()`?**
Sets the stack pointer, copies `.data` from flash to RAM, zeroes `.bss`, runs C runtime/constructor init, then calls `main`.

**39. What is `memcpy` vs `memmove`?**
Both copy bytes; `memmove` handles overlapping regions safely, `memcpy` does not (overlap is UB).

**40. How do you swap two values without a temp variable? Caveats?**
With XOR: `a ^= b; b ^= a; a ^= b;`. Caveat: fails (zeros the value) if both operands are the *same* variable, and it's not faster than using a temp on modern CPUs — interviewers ask to test understanding, not as best practice.

---

## D. Structs, unions, bit-fields

**41. `struct` vs `union` — key difference?**
A struct's members each have their own storage (size = sum + padding). A union's members share the same storage (size = largest member); only one is valid at a time.

**42. Give a real use for a union.**
Type punning / reinterpreting bytes (e.g. inspecting the bytes of a float), or saving memory when only one of several fields is active. Also handy for endianness checks.

**43. What is a bit-field and where is it used?**
A struct member with a specified bit width (`unsigned flag : 1;`), packing multiple small fields into bytes — used for hardware registers and flag sets to save memory.

**44. What are the portability problems with bit-fields?**
Bit ordering (which end fills first), packing, and alignment are implementation-defined, so bit-fields aren't portable across compilers/architectures for hardware layouts. Many shops prefer explicit masks/shifts instead.

**45. How do you check system endianness in C?**
Write a multibyte int and inspect its first byte:
```c
uint32_t x = 1;
int little = *(uint8_t *)&x;   // 1 = little-endian
```
Or via a union of `uint32_t` and `uint8_t[4]`.

**46. What is the `offsetof` macro?**
From `<stddef.h>`, gives the byte offset of a member within a struct — useful for serialization and container-of patterns.

**47. What is the `container_of` pattern (Linux kernel)?**
Given a pointer to a member, recover the pointer to the enclosing struct using `offsetof`. Foundational to Linux kernel linked lists and driver structures.

**48. Can a struct contain a pointer to its own type? Why?**
Yes — a self-referential struct, the basis of linked lists and trees. (It can't contain an *instance* of itself — that would be infinite size — but a pointer is fine.)

**49. What is a flexible array member?**
A trailing `type arr[];` in a struct, allocated with extra bytes so the array sizes dynamically within a single allocation. Common for variable-length packets.

---

## E. Bit manipulation

**50. Set, clear, toggle, and test bit `i`.**
Set: `x |= (1u << i)`. Clear: `x &= ~(1u << i)`. Toggle: `x ^= (1u << i)`. Test: `(x >> i) & 1`.

**51. Count set bits efficiently.**
Brian Kernighan: `while (n) { n &= (n - 1); count++; }` — each iteration clears the lowest set bit, so it loops once per set bit.

**52. Check if a number is a power of two.**
`n != 0 && (n & (n - 1)) == 0` — powers of two have exactly one set bit.

**53. Why use unsigned types for bit manipulation?**
Right-shifting a signed negative value is implementation-defined (may sign-extend), and signed overflow is UB. Unsigned has well-defined wraparound and logical shifts.

**54. What is the difference between logical and arithmetic right shift?**
Logical shift fills with 0 (unsigned). Arithmetic shift fills with the sign bit (signed, preserving sign). C's `>>` on signed negatives is implementation-defined.

**55. How do you implement multiply/divide by powers of 2 with shifts?**
`x << k` multiplies by 2^k; `x >> k` divides unsigned by 2^k. Only safe for division on unsigned (or non-negative signed) values.

**56. Swap two bits at positions i and j in an integer.**
Extract both; if they differ, flip both with a mask: `if (((x>>i)&1) != ((x>>j)&1)) x ^= (1u<<i)|(1u<<j);`.

**57. Reverse the bits in a byte/word.**
Iterate bit by bit building the reverse, or use a lookup table / divide-and-conquer swap of bit groups for speed.

**58. Read-modify-write a hardware register field.**
`reg = (reg & ~MASK) | (value << SHIFT);` — clear the field then OR in the new value, without disturbing other bits.

**59. How do you create a mask for the low `i` bits?**
`(1u << i) - 1`.

**60. Isolate the lowest set bit / clear the lowest set bit.**
Isolate: `x & (-x)`. Clear: `x & (x - 1)`.

---

## F. Preprocessor & macros

**61. What does the preprocessor do?**
Textual processing before compilation: `#include` file insertion, `#define` macro substitution, conditional compilation (`#if/#ifdef`), no type awareness.

**62. `#define` macro vs `inline` function — trade-offs?**
Macros: no type checking, no call overhead, but textual pitfalls (multiple evaluation, precedence). `inline` functions: type-safe, single evaluation, debuggable, while still avoiding call overhead. Prefer inline where available.

**63. Write a safe `MAX` macro.**
`#define MAX(a,b) ((a) > (b) ? (a) : (b))` — parenthesize *every* argument and the whole expression. Caveat: arguments are evaluated twice, so `MAX(i++, j)` misbehaves.

**64. What are include guards and why are they needed?**
`#ifndef HDR_H / #define HDR_H / ... / #endif` prevents a header being included twice in one translation unit (which would cause redefinition errors).

**65. What is `#pragma once`?**
A non-standard but widely supported alternative to include guards — one line, less error-prone, but slightly less portable.

**66. What do `#` and `##` do in macros?**
`#` stringizes an argument (`#x` → `"x"`); `##` is the token-paste operator, concatenating tokens to form new identifiers.

**67. How do you write a multi-statement macro safely?**
Wrap in `do { ... } while (0)` so it behaves as a single statement under `if/else` without a stray semicolon problem.

**68. What is conditional compilation used for in embedded?**
Selecting code per target/board, enabling debug builds, feature flags, and guarding platform-specific sections (`#if defined(STM32) ...`).

**69. What are common predefined macros?**
`__FILE__`, `__LINE__`, `__DATE__`, `__TIME__`, `__func__` (technically C99 identifier), and compiler/arch macros — useful in assert/logging.

**70. How would you implement a compile-time assert?**
`#define STATIC_ASSERT(c) typedef char _sa[(c) ? 1 : -1]` (pre-C11) or C11's `_Static_assert(cond, "msg")`.

---

## G. Interrupts & ISRs

**71. What is an interrupt? Polling vs interrupt-driven?**
A hardware/software signal that diverts the CPU to a handler. Polling repeatedly checks status (wastes CPU/power); interrupts notify on demand (efficient, lower latency).

**72. What is an ISR (Interrupt Service Routine) and what are the rules for writing one?**
The function run on an interrupt. Keep it short and fast; avoid blocking calls, dynamic allocation, and (often) `printf`/floating point; do minimal work and defer the rest to the main loop; re-entrancy and shared-data protection matter.

**73. Why can't an ISR return a value or take arguments?**
It's invoked by hardware, not called by code — there's no caller to pass args or receive a return. Communication is via shared (volatile) globals or queues.

**74. How do an ISR and main code share data safely?**
Mark shared variables `volatile`; for multi-byte/compound data, guard access (disable interrupts briefly or use a lock-free single-reader/single-writer ring buffer) to avoid torn reads.

**75. What is interrupt latency?**
Time from interrupt assertion to the first instruction of the ISR executing. Minimized by short critical sections, priorities, and not disabling interrupts for long.

**76. What is a critical section and how do you protect one?**
Code that must run atomically with respect to interrupts/other threads. Protect by briefly disabling interrupts (bare metal) or using a mutex/spinlock (with OS).

**77. What is interrupt nesting / priority?**
Higher-priority interrupts can preempt lower-priority ISRs. Requires careful stack budgeting and re-entrancy awareness.

**78. What is debouncing and where is it handled?**
Filtering spurious rapid transitions from mechanical switches — handled in software (timers/state) or hardware (RC filter), often triggered via interrupt then validated.

**79. Why might `printf` inside an ISR be dangerous?**
It's slow, may be non-reentrant, can block on I/O, and uses large stack — violating the "short ISR" rule and risking deadlock/corruption.

**80. What is a watchdog timer?**
A timer that resets the system if not periodically "kicked," recovering from hangs/lockups. The main loop or a health-check task refreshes it.

---

## H. Concurrency, RTOS & OS

**81. Process vs thread?**
A process has its own address space; threads share the parent process's address space and resources. Threads are lighter to create/switch but require synchronization on shared data.

**82. Mutex vs semaphore?**
A mutex provides mutual exclusion with ownership (only the locker unlocks), for protecting a resource. A semaphore is a counter for signaling/resource-counting, no ownership — a binary semaphore can signal between ISR and task.

**83. What is a race condition?**
When the result depends on unsynchronized timing of concurrent accesses to shared data — e.g. two threads incrementing a counter without a lock.

**84. What is a deadlock and the conditions for it?**
Threads stuck waiting on each other's resources forever. Coffman conditions: mutual exclusion, hold-and-wait, no preemption, circular wait. Break any one to prevent it (e.g. lock ordering).

**85. What is priority inversion and how is it solved?**
A high-priority task waits on a resource held by a low-priority task that's preempted by a medium task. Solved by priority inheritance or priority ceiling protocols.

**86. What is a context switch?**
Saving one task's CPU state (registers, PC, stack) and restoring another's so the scheduler can run a different task.

**87. Preemptive vs cooperative scheduling?**
Preemptive: scheduler can interrupt a running task at any time (responsive, needs locking). Cooperative: tasks yield voluntarily (simpler, but one bad task blocks all).

**88. What is reentrancy? What makes a function non-reentrant?**
A reentrant function can be safely interrupted and called again. Non-reentrant causes: static/global state, returning pointers to static buffers (e.g. `strtok`), non-atomic shared access.

**89. What is an atomic operation and why does it matter?**
An indivisible operation that can't be interrupted mid-way; needed for lock-free counters/flags. Use C11 `<stdatomic.h>` or arch primitives — a plain `count++` is not atomic.

**90. What is a spinlock and when is it appropriate?**
A lock that busy-waits instead of sleeping — cheap for very short critical sections on multicore, wasteful if held long or on single core.

---

## I. Embedded Linux specifics

**91. User space vs kernel space?**
Kernel space has full hardware privileges and runs the kernel/drivers; user space is restricted and accesses hardware via system calls. The boundary protects the system.

**92. What is a system call? Give examples.**
The controlled entry point from user to kernel space — `read`, `write`, `open`, `ioctl`, `mmap`, `fork`. It traps into the kernel.

**93. What is a device driver? Character vs block?**
Kernel code exposing hardware via a uniform interface. Character devices stream bytes (serial, sensors); block devices handle fixed-size random-access blocks (disks, flash).

**94. What is `mmap` and a common embedded use?**
Maps a file or device memory into a process's address space. Embedded use: `/dev/mem` mapping to access physical registers from user space.

**95. What are the IPC mechanisms in Linux?**
Pipes/FIFOs, message queues, shared memory, semaphores, sockets, signals. Shared memory is fastest (no copy) but needs synchronization.

**96. What is a signal? Name a few.**
Asynchronous notification to a process — `SIGINT`, `SIGTERM`, `SIGKILL` (uncatchable), `SIGSEGV`, `SIGCHLD`. Handled by registered handlers (which must be async-signal-safe).

**97. `fork()` vs `exec()` vs `vfork()`?**
`fork` duplicates the process (copy-on-write). `exec*` replaces the current image with a new program. `vfork` is a lighter fork sharing memory until exec (legacy/special use).

**98. What is the device tree?**
A data structure describing hardware (peripherals, addresses, IRQs) to the Linux kernel at boot, replacing hardcoded board files on ARM platforms.

**99. What is a kernel module?**
Code dynamically loaded/unloaded into the running kernel (`insmod`/`rmmod`) — drivers commonly ship as modules to avoid rebuilding the kernel.

**100. What is the difference between `/dev`, `/proc`, and `/sys`?**
`/dev`: device nodes. `/proc`: process/kernel info (virtual). `/sys`: sysfs, exposing kernel objects and driver attributes for configuration.

---

## J. Compiler, linker & build

**101. What are the stages of compilation?**
Preprocessing → compilation (to assembly) → assembly (to object) → linking (to executable). Embedded adds locating/flashing.

**102. What does the linker do?**
Resolves symbol references across object files/libraries, assigns final addresses, and combines sections into the output image per the linker script.

**103. What is a linker script and why does embedded need it?**
A file defining the memory map (flash/RAM regions) and where each section (`.text`, `.data`, `.bss`, stack) is placed — essential on bare metal where there's no OS loader.

**104. Static vs dynamic linking?**
Static: libraries baked into the binary (larger, self-contained — common on bare metal). Dynamic: shared libraries loaded at runtime (smaller binaries, shared code — common on Linux).

**105. What is a `.map` file?**
Linker output showing symbol addresses and section sizes — used to inspect memory usage and debug placement.

**106. What do `-O0`, `-O2`, `-Os` optimization levels mean?**
`-O0` none (best debugging). `-O2` aggressive speed. `-Os` optimize for size (often used in embedded with limited flash). Optimization can expose missing `volatile`.

**107. What is the difference between `inline` and `static inline`?**
`inline` suggests inlining; `static inline` (common in headers) gives each TU its own copy without external-linkage duplicate-symbol issues.

**108. What is name mangling and why does `extern "C"` exist?**
C++ encodes types into symbol names (mangling). `extern "C"` disables it so C++ can link against C symbols — important when mixing C and C++.

**109. What is a cross-compiler?**
A compiler running on one architecture (host, e.g. x86) producing code for another (target, e.g. ARM) — standard in embedded.

**110. What is the `volatile` interaction with compiler optimization?**
Without `volatile`, the optimizer may cache a value in a register or remove a "redundant" read of a hardware register or ISR-updated flag, breaking the program. `volatile` forces actual memory access.

---

## K. Tricky / gotcha questions

**111. What is undefined behavior? Give examples.**
Behavior the standard doesn't define — anything can happen. Examples: signed overflow, dereferencing NULL, out-of-bounds access, use-after-free, modifying a variable twice between sequence points (`i = i++`).

**112. What does `sizeof` return for `sizeof(char)`, and is it evaluated at compile or run time?**
`sizeof(char)` is always 1. `sizeof` is a compile-time operator (except for C99 VLAs) and its operand isn't evaluated.

**113. What's the output of `char c = 200; if (c > 100)` on a system with signed char?**
`c` overflows to a negative value, so the comparison is false. Illustrates signed/unsigned `char` pitfalls.

**114. Why is `if (x = 5)` a bug, and how do you guard against it?**
It assigns 5 to `x` (always true) instead of comparing. Guard with "Yoda" conditions `if (5 == x)` or rely on compiler warnings (`-Wall`).

**115. What is a sequence point?**
A point where all side effects of previous evaluations are complete (e.g. `;`, `&&`, `||`, comma, function call). Modifying a variable more than once between sequence points is UB.

**116. What's wrong with `char *s = "hello"; s[0] = 'H';`?**
`s` points to a string literal in (likely) read-only memory — writing is undefined behavior. Use `char s[] = "hello";` for a modifiable copy.

**117. Why might a loop counter need to be `volatile`?**
If it's modified by an ISR or hardware (e.g. a tick counter), the compiler might otherwise cache it and the main loop would never see updates.

**118. What's the difference between `NULL`, `'\0'`, and `0`?**
All often compare equal but differ semantically: `NULL` is a null pointer constant, `'\0'` is the null character (the value 0 as a `char`), `0` is the integer zero.

**119. What does `a[i]` actually mean in C, and why does `i[a]` also work?**
`a[i]` is defined as `*(a + i)`. Since addition commutes, `*(a + i) == *(i + a) == i[a]` — a famous quirk, never used in practice.

**120. What's the bug in `for (i = 0; i < n; i++) sum += arr[i];` if `i` is `uint8_t` and `n > 255`?**
`i` wraps at 256 and never reaches `n`, causing an infinite loop. Type-width awareness matters on small types.

**121. Why is `#define SQUARE(x) x*x` buggy, and what does `SQUARE(a+b)` expand to?**
It expands to `a+b*a+b` (precedence) — not `(a+b)²`. Fix with full parenthesization: `#define SQUARE(x) ((x)*(x))`.

**122. What does `volatile int *p` vs `int *volatile p` mean?**
`volatile int *p`: pointer to volatile data (the data is volatile). `int *volatile p`: a volatile pointer to ordinary data (the pointer itself is volatile — rare).

**123. What is strict aliasing, and how can it bite you?**
The compiler assumes pointers of different types don't alias the same memory, enabling optimization. Type-punning via incompatible pointer casts violates it (UB) — use a `union` or `memcpy` instead.

**124. What is the `restrict` keyword?**
A promise that a pointer is the only reference to its data within scope, letting the compiler optimize (no aliasing). Misusing it is UB.

---

## Quick self-test priorities (Arm/Snap favorites)

If you only have time to nail a handful, these come up most:
`volatile` (deep answer) · `const`/`static` meanings · pointer-to-const vs const-pointer · struct vs union · bit-fields & masks · set/clear/test a bit · power-of-two & count-bits · stack vs heap · why avoid malloc in embedded · ISR rules & ISR↔main sharing · mutex vs semaphore · race condition & deadlock · endianness check · structure padding/alignment · `do{}while(0)` macros · undefined behavior examples.

---

*Cover the answer, say yours aloud, then check. Knowing the deep "why" — especially on `volatile`, pointers, and memory — is what separates a pass from a fail in embedded interviews.*
