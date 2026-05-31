# Snap (Snapchat) Embedded Linux Engineer — C Interview Prep

**Format:** 60-minute technical screen, coding in a shared IDE (often HackerRank), in C.
**Your situation:** ~1 week to prep, experienced in C but rusty.
**Goal of this doc:** one place to review concepts, drill the high-probability topics, and follow study links.

---

## 1. What to expect & how hard it is

Snap's coding rounds are **LeetCode medium-to-hard** level, comparable to Meta/Google on the problems themselves. Candidates rate the overall process around **3.3 / 5** on difficulty — challenging but fair, not an elite gauntlet.

For a 60-minute screen, the realistic bar is **one solid Medium done cleanly**, sometimes with a harder follow-up where talking through the approach and complexity is acceptable instead of fully coding it.

Two things that make it more passable than the raw difficulty suggests:

- Snap interviewers have said they **don't judge purely on completion** — they weigh how you collaborate, take hints, and communicate. Candidates have passed without fully coding the solution. Going silent or rigid fails more often than not finishing.
- For an **embedded** role, algorithm difficulty skews *lower* than the generic SWE loop: less graph/DP, more arrays, strings, bit manipulation, and buffers. The harder part is embedded-C depth, which is pure preparation.

**Your real risk** isn't problem difficulty — it's C rust slowing you down or causing bugs under time pressure. That's exactly what this week fixes.

> ⚠️ Embedded Linux interviews vary a lot by team and level. Some lean coding-heavy; others lean systems/driver knowledge with lighter algorithms. If your recruiter signaled a focus, weight accordingly.

---

## 2. The 7-day plan

The single most effective thing for "I forget when I'm not writing it": **write C by hand every day.** Reading feels productive but won't fix recall — typing will.

**Setup:** compile locally with the address sanitizer so memory bugs surface automatically:
```bash
gcc -Wall -Wextra -fsanitize=address -g prog.c -o prog
```

| Days | Focus |
|------|-------|
| **1–2** | **C reactivation.** Re-implement from memory: linked list (insert/delete/reverse/cycle), dynamic array with `realloc`, manual string fns. Fix every leak/overflow ASan flags. |
| **3** | **Bit manipulation** (the embedded differentiator) + start arrays/strings. Drill the canonical bit ops until automatic. |
| **4** | **Ring buffer** from scratch + more arrays/strings/hash. Embedded-C theory review (`volatile`, `static`, pointers, memory). |
| **5** | **Linked lists, stacks/queues, basic trees/recursion** in C. Systems topics (threads, mutexes, IPC) if your role needs them. |
| **6** | **2–3 timed mocks.** Unseen Medium, 35–40 min, narrate out loud. Surfaces what you still fumble. |
| **7** | **Light review** of your own notes. Sleep. |

Target ~4–6 problems/day on days 3–5, weighted toward arrays, strings, bit manipulation, linked lists.

---

## 3. C reactivation checklist

Be airtight on the things C makes you manage by hand:

- **Pointers:** pointer arithmetic, `**` (pointer-to-pointer), passing by reference, function pointers
- **Dynamic memory:** `malloc`/`calloc`/`realloc`/`free`; free what you allocate; no dangling/wild pointers
- **Strings:** null-terminated `char` arrays; the `\0` on every operation; `strlen` vs buffer size
- **Structs** and building node-based structures with them
- **Arrays vs pointers**, and why you pass length separately
- **Pitfalls:** buffer overflow, uninitialized memory, returning pointers to stack-local variables

**Litmus test:** write a linked list with insert/reverse/cycle-detection from scratch, correct `malloc`/`free`, no looking anything up. If you can, most C-mechanics risk is covered.

---

## 4. Bit manipulation (highest-value embedded topic)

Expect at least one. These are the canonical operations — know them cold.

```c
// Count set bits — Brian Kernighan's trick (clears lowest set bit each loop)
int count_set_bits(unsigned int n) {
    int count = 0;
    while (n) { n &= (n - 1); count++; }
    return count;
}

// Power of two? (only one bit set)
int is_power_of_two(unsigned int n) {
    return n != 0 && (n & (n - 1)) == 0;
}

// Single-bit operations on the i-th bit
int  get_bit  (int x, int i) { return (x >> i) & 1; }
int  set_bit  (int x, int i) { return x |  (1 << i); }
int  clear_bit(int x, int i) { return x & ~(1 << i); }
int  toggle_bit(int x, int i){ return x ^  (1 << i); }

// Parity: 1 if odd number of set bits
int parity(unsigned int x) {
    int r = 0;
    while (x) { r ^= 1; x &= (x - 1); }
    return r;
}

// Swap bytes (endianness) of a 32-bit value
uint32_t swap_bytes(uint32_t x) {
    return ((x & 0x000000FF) << 24) |
           ((x & 0x0000FF00) <<  8) |
           ((x & 0x00FF0000) >>  8) |
           ((x & 0xFF000000) >> 24);
}
```

Also be ready to: **reverse the bits** of an integer, build a **mask** like `(1 << i) - 1`, and explain **read-modify-write** on a hardware register (`reg = (reg & ~mask) | value;`).

---

## 5. Data structures that fit constrained systems

On resource-starved targets you often implement these yourself rather than pull from a library. Trees/graphs/heavy DP are *less* likely here — don't over-invest.

### Ring (circular) buffer — near-canonical embedded question

```c
typedef struct {
    int    *buf;
    size_t  head, tail, count, cap;
} ring_t;

int rb_init(ring_t *r, size_t cap) {
    r->buf = malloc(cap * sizeof(int));
    if (!r->buf) return -1;
    r->head = r->tail = r->count = 0;
    r->cap = cap;
    return 0;
}

int rb_push(ring_t *r, int val) {       // returns -1 if full
    if (r->count == r->cap) return -1;
    r->buf[r->head] = val;
    r->head = (r->head + 1) % r->cap;
    r->count++;
    return 0;
}

int rb_pop(ring_t *r, int *out) {       // returns -1 if empty
    if (r->count == 0) return -1;
    *out = r->buf[r->tail];
    r->tail = (r->tail + 1) % r->cap;
    r->count--;
    return 0;
}
```

Also practice from scratch: **linked list** (reverse, cycle detection via fast/slow pointers), **stack** and **queue**, and a simple **fixed-block / memory-pool allocator** as a discussion topic.

---

## 6. Embedded-C knowledge (where candidates pass or fail)

Generic LeetCode grind leaves you exposed here. Be ready to give the *deep* answer out loud.

- **`volatile`** — not just "stops the compiler optimizing." The real answer: memory-mapped hardware registers, variables modified by an **ISR**, and flags shared across execution contexts. The compiler must re-read from memory each access. *(This exact question has cost people offers.)*
- **`const`, `static`, `volatile` combinations** — including `const volatile` (a read-only hardware status register).
- **`static`** — file-scope linkage vs. persistent local storage.
- **Pointers (deep):** function pointers, pointer-to-pointer, wild vs dangling, pointer-to-volatile.
- **`struct` vs `union`** — unions overlap storage (type-punning / saving memory); **bit-fields** pack flags or model hardware registers bit-by-bit.
- **Memory layout:** stack vs heap; static vs dynamic trade-offs; *why dynamic allocation is often avoided* on embedded targets (fragmentation, determinism); struct **alignment & padding**.
- **ISRs:** keep them short; what you can't safely do inside one; share data with the main loop via `volatile`.
- **Preprocessor:** include guards (`#ifndef/#define/#endif`); fully-parenthesized function macros:
  ```c
  #define MIN(a, b) ((a) <= (b) ? (a) : (b))   // every arg parenthesized
  ```

---

## 7. Embedded Linux systems topics

How deep depends on team/seniority, but be conversant in:

- **Processes vs threads**; user space vs kernel space
- **Concurrency:** mutexes, semaphores, race conditions, deadlock
- **POSIX basics:** file descriptors, `fork`/`exec`, signals
- **IPC:** pipes, shared memory, message queues
- **Device drivers** at a high level (what they are, char vs block)

---

## 8. Suggested problem set (~20, ordered for the week)

Do all in C. Roughly in order:

**Warm-up / arrays & strings**
1. Two Sum
2. Reverse String (in place)
3. Valid Palindrome
4. Best Time to Buy and Sell Stock
5. Maximum Subarray (Kadane's)
6. Move Zeroes (in place)
7. Longest Substring Without Repeating Characters

**Bit manipulation**
8. Number of 1 Bits
9. Counting Bits
10. Single Number (XOR)
11. Reverse Bits
12. Power of Two

**Linked lists**
13. Reverse Linked List
14. Linked List Cycle
15. Merge Two Sorted Lists
16. Remove Nth Node From End of List

**Stacks / queues / design**
17. Valid Parentheses
18. Implement Queue using Stacks
19. Design Circular Queue *(ties straight to your ring buffer)*

**Trees / recursion (lighter for embedded)**
20. Maximum Depth of Binary Tree
21. Invert Binary Tree
22. *(stretch)* Serialize and Deserialize Binary Tree

---

## 9. Interview-day tips

- **Clarify first:** input constraints, ranges, edge cases — before coding.
- **Think out loud the whole time.** Snap weighs this heavily; silence reads as being stuck.
- **State complexity** (time & space) at the end — make it a reflex.
- **Test edge cases:** empty input, single element, `NULL`, overflow.
- **Free what you allocate** and mention it — clean memory handling reads as code quality in C.
- **If stuck, narrate options** rather than freezing. Take hints gracefully; that's literally part of the score.
- **Clean > clever.** Correct, readable code you can explain beats a slick solution you can't reason about.

---

## 10. Study links

**Practice platforms**
- NeetCode roadmap (problems grouped by pattern): https://neetcode.io/practice
- LeetCode Top Interview 150: https://leetcode.com/studyplan/top-interview-150/
- HackerRank (Snap often uses this environment): https://www.hackerrank.com/

**C refresher**
- Beej's Guide to C Programming (free, excellent): https://beej.us/guide/bgc/

**Embedded C interview prep**
- Embedded-C Interview Prep — Bit Manipulation: https://tonyfu97.github.io/Embedded-C-Interview-Prep/08_bit_manipulation/
- GeeksforGeeks — Top Embedded C Questions: https://www.geeksforgeeks.org/c/top-embedded-c-interview-questions-and-answers-for-2024/
- InterviewBit — Embedded C Questions: https://www.interviewbit.com/embedded-c-interview-questions/
- Adaface — 100 Embedded C Questions: https://www.adaface.com/blog/embedded-c-interview-questions/
- "Cracking the (embedded) Coding Interview" (Manasi Rajan): https://www.embeddedrelated.com/showarticle/1503.php
- Bit Manipulation Q&A (GitHub): https://github.com/Devinterview-io/bit-manipulation-interview-questions

**Snap-specific guides**
- Exponent — Snap SWE Interview Guide: https://www.tryexponent.com/guides/snap-software-engineer-interview
- Prepfully — Snap SWE Guide: https://prepfully.com/interview-guides/snap-software-engineer
- Glassdoor — Snap SWE interview reviews: https://www.glassdoor.com/Interview/Snap-Software-Engineer-Interview-Questions-EI_IE671946.0,4_KO5,22.htm

**Optional reference book**
- *Cracking the Coding Interview* (McDowell) — process + linked lists, stacks/queues, trees. Java examples, but concepts transfer.

---

*Built as a personal study reference. Priorities for your week, in order: (1) reactivate C by hand, (2) bit manipulation cold, (3) ring buffer + linked lists, (4) deep `volatile`/pointers/memory answers, (5) timed mocks narrating out loud.*
