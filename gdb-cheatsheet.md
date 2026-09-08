# GDB Cheatsheet — الدليل الشامل لـ GDB

> Based on *Debugging with GDB* (Tenth Edition, GDB 19.x) — https://sourceware.org/gdb/current/onlinedocs/gdb
> الشرح بالعامية المصرية، والـ keywords والأوامر كلها English. الـ comments جوه الكود بإنجليزي بسيط (B1).
> علامة `#` جوه أي code block = comment. GDB نفسه بيعتبر `#` comment برضه.

---

## Table of Contents

1. [Quick Start](#1-quick-start)
2. [Invocation — Starting & Quitting GDB](#2-invocation--starting--quitting-gdb)
3. [GDB Commands — Syntax, Completion, Help](#3-gdb-commands--syntax-completion-help)
4. [Running Programs](#4-running-programs)
5. [Stopping & Continuing — Breakpoints, Watchpoints, Catchpoints](#5-stopping--continuing)
6. [Stepping & Skipping](#6-stepping--skipping)
7. [Signals](#7-signals)
8. [Threads, Inferiors, Forks, Checkpoints](#8-threads-inferiors-forks-checkpoints)
9. [Reverse Execution & Process Record](#9-reverse-execution--process-record)
10. [Examining the Stack](#10-examining-the-stack)
11. [Examining Source Files](#11-examining-source-files)
12. [Examining Data](#12-examining-data)
13. [Registers, Memory, Core Files](#13-registers-memory-core-files)
14. [Optimized Code, Macros](#14-optimized-code-macros)
15. [Tracepoints](#15-tracepoints)
16. [Overlays](#16-overlays)
17. [Languages](#17-languages)
18. [Symbols](#18-symbols)
19. [Altering Execution](#19-altering-execution)
20. [GDB Files, Separate Debug Info, debuginfod](#20-gdb-files-separate-debug-info-debuginfod)
21. [Targets & Remote Debugging (gdbserver)](#21-targets--remote-debugging-gdbserver)
22. [Configuration-Specific & Architecture Notes](#22-configuration-specific--architecture-notes)
23. [Controlling GDB — Settings](#23-controlling-gdb--settings)
24. [Extending GDB — Scripts, Python, Guile](#24-extending-gdb--scripts-python-guile)
25. [Interpreters, TUI, Emacs](#25-interpreters-tui-emacs)
26. [GDB/MI, DAP, Annotations, JIT, In-Process Agent](#26-gdbmi-dap-annotations-jit-in-process-agent)
27. [Command Line Editing & History](#27-command-line-editing--history)
28. [Maintenance Commands & Bug Reports](#28-maintenance-commands--bug-reports)
29. [Convenience Variables & Functions (Full List)](#29-convenience-variables--functions-full-list)
30. [Abbreviation Table](#30-abbreviation-table)

---

## 1. Quick Start

**بالعامية:** ده أسرع طريق تبدأ بيه. بتـ compile بـ `-g`، تفتح GDB، تحط `breakpoint`، تشغّل بـ `run`، وتمشي سطر سطر بـ `next` / `step`، وتشوف القيم بـ `print`.

```bash
gcc -g -O0 -o app app.c        # compile with debug info, no optimization
gdb ./app                      # open the program in GDB
gdb -q ./app                   # same, but without the copyright banner
gdb --args ./app arg1 arg2     # pass program arguments directly
gdb ./app core                 # open a core dump
gdb -p 1234                    # attach to a running process by PID
```

```gdb
(gdb) break main               # stop when main() starts
(gdb) run                      # start the program
(gdb) next                     # run one line, do not enter functions
(gdb) step                     # run one line, enter functions
(gdb) print x                  # show the value of x
(gdb) backtrace                # show the call stack
(gdb) continue                 # keep running until next stop
(gdb) quit                     # exit GDB
```

---

## 2. Invocation — Starting & Quitting GDB

### 2.1 Choosing Files

**بالعامية:** لما تشغّل `gdb` من الـ shell، تقدر تديله الـ executable، الـ core file، أو الـ PID. الـ options دي بتقوله يقرأ إيه من فين.

```bash
gdb program                    # load an executable
gdb program core               # executable + core dump
gdb program 1234               # executable + attach to PID 1234
gdb -p 1234                    # attach by PID only (program name optional)
gdb ./12345                    # "./" prefix: treat as file, not PID

gdb -s file  / --symbols=file  # read symbol table from this file only
gdb -e file  / --exec=file     # use this file as the executable
gdb -se file                   # symbols AND executable from same file
gdb -c file  / --core=file     # use this core dump
gdb -x file  / --command=file  # run GDB commands from a file (like "source")
gdb -ex 'cmd' / --eval-command # run one GDB command (repeatable)
gdb -ix file / -iex 'cmd'      # same, but BEFORE the program is loaded
gdb -eix file / -eiex 'cmd'    # very early init, before any output
gdb -d dir   / --directory=dir # add a source search directory
gdb -r / --readnow             # read ALL symbols now (slower start, faster later)
gdb --readnever                # never read debug info (fast attach/dump/detach)
```

### 2.2 Choosing Modes

**بالعامية:** الـ modes دي بتتحكم في *إزاي* GDB يشتغل: صامت، batch، TUI، MI للـ IDEs... إلخ.

```bash
gdb -n  / -nx                  # do not read ANY init files
gdb -nh                        # skip only the home-directory init file
gdb -q  / -quiet / -silent     # no banner
gdb -batch                     # run -x/-ex commands then exit (status 0 or error)
gdb -batch-silent              # same, and no stdout at all
gdb -return-child-result       # GDB exit code = debugged program exit code
gdb -nw / -nowindows           # command line only (no GUI)
gdb -w  / -windows             # use GUI if available
gdb -cd dir                    # start with this working directory
gdb -D dir / -data-directory   # where GDB looks for its data files
gdb -f / -fullname             # Emacs-style file:line output
gdb -annotate LEVEL            # annotation level 0..3 (old front-end protocol)
gdb --args prog a b c          # everything after prog = program args (escaped)
gdb --no-escape-args prog '*'  # same, but shell chars are NOT escaped
gdb -b BPS / -baud BPS         # serial line speed for remote debugging
gdb -l SECONDS                 # remote timeout
gdb -t DEV / -tty DEV          # program stdin/stdout on this device
gdb -tui                       # start with the Text User Interface
gdb -interpreter=mi            # GDB/MI mode (for IDEs); also mi3, mi2, mi1
gdb -write                     # open exec/core read-write (= "set write on")
gdb -statistics                # print time/memory after each command
gdb -version                   # print version and exit
gdb -configuration             # print build configuration and exit
gdb -binary-output             # MS-Windows only: binary stdout/stderr
gdb -help / -h                 # list all options
```

### 2.3 Startup Order & Init Files

**بالعامية:** GDB وهو بيقوم بيقرأ ملفات init بترتيب معيّن. لو عايز settings دايمة حطها في `~/.gdbinit` أو `~/.config/gdb/gdbinit`. الـ early init (`gdbearlyinit`) مسموح فيه بس أوامر `set` و `source` اللي بتتحكم في الـ startup.

```text
Order of startup:
 1. early init file: $XDG_CONFIG_HOME/gdb/gdbearlyinit | ~/.config/gdb/gdbearlyinit | ~/.gdbearlyinit
    (macOS: ~/Library/Preferences/gdb/gdbearlyinit)
 2. -eiex / -eix options
 3. interpreter setup
 4. system.gdbinit  and  system.gdbinit.d/*.gdb|*.py|*.scm  (alphabetical)
 5. home init file: $XDG_CONFIG_HOME/gdb/gdbinit | ~/.config/gdb/gdbinit | ~/.gdbinit
    (macOS: ~/Library/Preferences/gdb/gdbinit)
 6. -iex / -ix options
 7. command-line operands (program, core, pid)
 8. ./.gdbinit  (only if "set auto-load local-gdbinit on" and dir != home)
 9. auto-loaded scripts for the program / shared libs
10. -ex / -x options
11. command history file
```

```gdb
# Useful in ~/.gdbinit
set startup-quietly on          # like -q (early-init file only)
set confirm off                 # do not ask "are you sure?"
set pagination off              # no "--Type <RET>--" pauses
set print pretty on             # nice struct printing
set history save on             # keep command history between sessions
set auto-load safe-path /       # allow local .gdbinit anywhere (careful!)
```

### 2.4 Quitting, Shell Commands, Logging

**بالعامية:** `quit` أو `exit` أو `Ctrl-d` بيقفلوا GDB. `Ctrl-c` مش بيقفل GDB، بيوقف الأمر الشغّال بس. تقدر تشغّل أوامر shell من جوه GDB بـ `shell` أو `!`، وتعمل `pipe` لـ output أي أمر لأمر shell.

```gdb
quit [EXPR]     / q / exit     # exit GDB; EXPR = exit code
Ctrl-c                         # interrupt current command / running program
detach                         # release an attached process, keep GDB open

shell CMD       / !CMD         # run a shell command (no space needed after !)
make ARGS                      # same as "shell make ARGS"
pipe CMD | SHELLCMD            # send GDB command output to a shell command
| CMD | SHELLCMD               # short form of pipe
|| SHELLCMD                    # repeat last command, pipe to shell
pipe -d DELIM CMD DELIM SHELL  # custom delimiter when CMD contains "|"
p $_shell("ls -l")             # run shell from an expression, returns exit code
p $_shell_exitcode             # exit code of last shell/make/pipe
p $_shell_exitsignal           # signal that killed the last shell command

set logging enabled on|off     # start / stop logging
set logging file FILE          # default: gdb.txt
set logging overwrite on|off   # overwrite instead of append
set logging redirect on|off    # on = output goes ONLY to the file
set logging debugredirect on   # same for debug output
show logging                   # show logging settings
```

---

## 3. GDB Commands — Syntax, Completion, Help

**بالعامية:** أي أمر ممكن تختصره لأول كام حرف طالما مفيش لبس (`b` = `break`, `c` = `continue`). لو ضغطت `Enter` على سطر فاضي، بيكرر آخر أمر (ما عدا أوامر خطيرة زي `run`). `TAB` بيكمّلك الأمر أو اسم الـ symbol. `#` = comment.

```gdb
step 5                         # commands take arguments
s                              # abbreviations work when unique
<RET>                          # empty line = repeat last command (not run/attach)
Ctrl-o                         # accept line AND fetch next history line (operate-and-get-next)
# this is a comment            # from "#" to end of line is ignored

# --- Settings ---
set print elements 10          # change a setting
show print elements            # see a setting
info set                       # show ALL settings (same as "show")
print -elements 10 -- arr      # override a setting for one command
with print pretty on -- p var  # temporarily set for one command
w print elements 5             # "w" = with; no command = repeat last command
with language ada -- with print elements 10 -- p x   # nest "with"

# --- Completion ---
info bre<TAB>                  # completes to "info breakpoints"
b make_<TAB><TAB>              # list all matches
M-?                            # (ESC ?) list matches without TAB TAB
p 'func<<TAB>                  # quote ' to complete C++ templates/operators
p var.<TAB>                    # completes struct fields
set max-completions 200        # limit (0 = disable, "unlimited")
show max-completions

# --- Filenames with spaces ---
file /path/with\ spaces/prog   # escape with backslash (file, symbol-file, exec-file)
symbol-file "/path/with spaces/prog"   # or quote it
add-auto-load-safe-path /path with spaces/  # most commands take raw text, no quoting

# --- Command options ---
print -pretty -- *ptr          # "--" ends options when argument may start with "-"
p -o -p 0 -e u -- *myptr       # options abbreviate; on/off/1/0/yes/no/enable/disable
print -<TAB><TAB>              # list options of a command

# --- Help ---
help            / h            # list command classes
help CLASS                     # e.g. help breakpoints, help running, help data
help COMMAND                   # e.g. help break
apropos REGEX                  # search all commands + docs
apropos -v REGEX               # verbose, highlights matches
complete TEXT                  # list completions for TEXT (used by Emacs)
info ...        / i            # info about the PROGRAM (args, registers, ...)
show ...                       # info about GDB itself (settings)
show version                   # GDB version
show configuration             # how GDB was built
show copying / show warranty   # license text
```

---

## 4. Running Programs

### 4.1 Compiling for Debugging

**بالعامية:** لازم تـ compile بـ `-g` عشان يبقى فيه debug info. `-g3` بيضيف macros. الأفضل DWARF أحدث version. `-O0` بيخلي الـ debugging أسهل، بس GCC بيسمح بـ `-g -O2` مع بعض.

```bash
gcc -g app.c                   # basic debug info (DWARF)
gcc -g3 app.c                  # + preprocessor macro info (needed for "macro" cmds)
gcc -g -O0 app.c               # no optimization = easiest debugging
gcc -g -O2 app.c               # optimized but still debuggable (harder)
gcc -ggdb3 app.c               # max GDB-specific debug info
gcc -g -fno-omit-frame-pointer # better backtraces in optimized code
```

### 4.2 Starting the Program

**بالعامية:** `run` بيشغّل البرنامج. `start` = temporary breakpoint على `main` + `run`. `starti` بيقف عند **أول instruction** خالص (قبل `main`، مفيد للـ elaboration / static constructors).

```gdb
run       / r                  # start the program (uses saved args)
run ARGS                       # start with these args (shell expands *, $, <, >)
run < in.txt > out.txt         # redirect program I/O
start                          # temp breakpoint at main + run
start ARGS                     # same with args
starti                         # stop at the very first instruction
set exec-wrapper env 'LD_PRELOAD=libx.so'   # launch through a wrapper program
unset exec-wrapper / show exec-wrapper
set startup-with-shell off     # start program directly, not via $SHELL
set auto-connect-native-target off  # "run" will not auto-connect to native target
target native                  # connect to native target explicitly
disconnect                     # disconnect from target
set disable-randomization off  # keep ASLR on (default: GDB disables ASLR)
show disable-randomization
```

### 4.3 Arguments, Environment, Working Directory, I/O

**بالعامية:** `set args` بيحدد الـ arguments للمرة الجاية. `set environment` بيغيّر env variables للبرنامج بس، مش لـ GDB. `set cwd` بيغيّر working directory البرنامج، `cd` بيغيّر بتاع GDB نفسه. `tty` بيحوّل input/output البرنامج لـ terminal تاني.

```gdb
set args ARGS                  # arguments for the next run
set args                       # clear arguments
set args "ab                   # multi-line arg: GDB shows ">" secondary prompt
show args

path DIR                       # add DIR to front of program's PATH
show paths
show environment [VAR]  / show env
set environment VAR [=VALUE] / set env VAR=VALUE   # set for the PROGRAM
unset environment VAR          # remove VAR completely (not just empty)

set cwd DIR                    # program's working directory (next run)
set cwd                        # reset: inherit GDB's cwd
show cwd
cd [DIR]                       # change GDB's own working directory
pwd                            # print GDB's working directory
info proc cwd                  # actual cwd of the running debuggee (Linux)

info terminal                  # terminal modes the program uses
tty /dev/pts/3                 # program I/O on another terminal
set inferior-tty /dev/pts/3    # same as tty
set inferior-tty               # reset to GDB's terminal
show inferior-tty
```

### 4.4 Attach / Detach / Kill

**بالعامية:** `attach PID` بيعلّق GDB على process شغّال. `detach` بيسيبه يكمّل من غيرك. `kill` بيقتله. لازم يكون عندك permission (على Linux شوف `ptrace_scope`).

```gdb
attach PID                     # attach to a running process
attach -f PID                  # (some targets) force
detach                         # let the process continue without GDB
kill      / k                  # kill the debugged process
info files                     # show active targets
```

```bash
# Linux: if attach is denied
echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope
```

---

## 5. Stopping & Continuing

### 5.1 Breakpoints — Setting

**بالعامية:** الـ breakpoint بيوقّف البرنامج عند مكان معيّن (location). تقدر تحطه على function، سطر، address، أو بشرط (condition). `tbreak` = temporary (بيتمسح بعد أول hit). `rbreak` بيحط breakpoints على كل الـ functions اللي بتطابق regex. `hbreak` = hardware breakpoint.

```gdb
break     / b                  # at current line (or next instruction in frame)
break LOCATION                 # see "Location Specifications" below ⭐
break main                     # at function
break file.c:42                # file:line
break 42                       # line in current file
break *0x401234                # at an address
break +2 / break -3            # offset from current line
break func if x > 5            # conditional breakpoint
break file.c:42 thread 3       # only for thread 3
break func inferior 2          # only for inferior 2
break func task 4              # Ada task-specific
break -force-condition func if bad_cond   # keep condition even if it can't be evaluated now
break -qualified ns::func      # exact match only, no wildcard/namespace search
break -source f.c -line 10     # explicit location
break -function foo -label L1  # explicit: function + label
tbreak LOCATION  / tb          # temporary breakpoint (deleted after first hit)
hbreak LOCATION  / hb          # hardware breakpoint (needs target support)
thbreak LOCATION / thb         # temporary hardware breakpoint
rbreak REGEX                   # break on ALL functions matching regex
rbreak file.c:REGEX            # limit to one file
rbreak ^foo_                   # all functions starting with foo_
info breakpoints / info break / i b   # list all breakpoints
info breakpoints 3             # only #3
info break 3-5                 # range of breakpoint numbers
maint info breakpoints         # includes GDB's internal breakpoints

set breakpoint pending on|off|auto   # what to do if location is not found yet
set breakpoint always-inserted on    # keep breakpoints inserted while stopped
set breakpoint auto-hw on|off        # auto choose hw breakpoints when needed
set breakpoint condition-evaluation host|target|auto
set multiple-symbols all|ask|cancel  # what to do when a name is ambiguous
show breakpoint pending
```

**Location Specifications (locspec):** بتتقبل في `break`, `list`, `until`, `advance`, `jump`, `tbreak`, `dprintf`, `edit`, `info scope`, `info line`, `trace`...

```text
LINESPEC:
  LINENUM                        # line in current file
  -OFFSET / +OFFSET              # relative to current line
  FILENAME:LINENUM               # file:line
  FUNCTION                       # start of function (after prologue)
  FUNCTION:LABEL                 # a C label inside the function
  FILENAME:FUNCTION              # function in a specific file
  *ADDRESS                       # exact address, e.g. *0x401000, *main+4
  'file.c'::func                 # quoted when names have special chars

EXPLICIT:
  -source FILE  -function FUNC  -line N  -label L  -qualified

Wildcards: "break foo" matches foo, ns::foo, A::foo unless -qualified.
```

### 5.2 Watchpoints

**بالعامية:** الـ watchpoint بيوقّف البرنامج لما **قيمة** expression تتغيّر (مش لما تعدّي على سطر). `watch` = write، `rwatch` = read، `awatch` = read أو write. الـ hardware watchpoints سريعة، الـ software بطيئة جدًا. `-l` / `-location` بيراقب الـ address مش الـ expression (مفيد لـ locals هتطلع من scope).

```gdb
watch EXPR                     # stop when EXPR's value changes (write)
watch -l EXPR / watch -location *ptr   # watch the ADDRESS of EXPR
watch var if var > 100         # conditional watchpoint
watch var thread 2             # thread-specific
watch var mask 0xffff00        # masked watchpoint (some targets)
rwatch EXPR                    # stop when EXPR is READ
awatch EXPR                    # stop on read OR write
info watchpoints               # list watchpoints (subset of info break)
set can-use-hw-watchpoints 0   # force software watchpoints
show can-use-hw-watchpoints
```

### 5.3 Catchpoints

**بالعامية:** الـ catchpoint بيوقّف عند **event** مش مكان: exception، syscall، signal، fork، library load... مفيد جدًا لما متعرفش الكود بيقع فين.

```gdb
catch throw [REGEX]            # C++ exception thrown
catch rethrow [REGEX]          # C++ exception rethrown
catch catch [REGEX]            # C++ exception caught
tcatch EVENT                   # temporary catchpoint
catch exception [NAME]         # Ada exception (or all)
catch exception unhandled      # Ada unhandled exception
catch handlers [NAME]          # Ada exception handler entered
catch assert                   # Ada failed assertion
catch exec                     # program calls exec()
catch fork                     # fork()
catch vfork                    # vfork()
catch load [REGEX]             # shared library loaded
catch unload [REGEX]           # shared library unloaded
catch syscall                  # ANY syscall (entry and return)
catch syscall write            # by name
catch syscall 1                # by number
catch syscall group:network    # by group (network, process, file, ...)
catch syscall g:file
catch signal [SIG...]          # signal delivered (e.g. catch signal SIGUSR1)
catch signal all               # including SIGTRAP/SIGINT used by GDB
info breakpoints               # catchpoints are listed here too
```

### 5.4 Deleting, Disabling, Enabling

**بالعامية:** `delete` بيمسح، `disable` بيطفّي مؤقتًا، `enable once` بيشغّله لمرة واحدة، `enable delete` = يتحول لـ temporary، `enable count N` = N مرات وبعدين يتطفّي.

```gdb
clear                          # delete breakpoints at current line
clear FUNCTION / clear file:line   # delete breakpoints at that location
delete [BPS]     / d           # delete breakpoints (all if no args, asks confirm)
delete 2 4-6                   # by number and ranges
delete bookmark N              # (checkpoints) - see section 8
disable [BPS]    / dis         # turn off but keep
enable  [BPS]    / en          # turn on
enable once BPS                # enable, disable again after 1 hit
enable count N BPS             # enable for N hits
enable delete BPS              # enable, delete after 1 hit (= tbreak)
disable/enable 3.1             # a single location of multi-location bp #3
```

### 5.5 Conditions, Ignore Counts, Command Lists

**بالعامية:** `condition` بيضيف أو يمسح شرط. `ignore N COUNT` = تجاهل الـ breakpoint COUNT مرة. `commands` بيخلّيك تكتب أوامر تتنفذ أوتوماتيك كل ما الـ breakpoint يتضرب (لازم تختم بـ `end`). `silent` كأول أمر بيخفي الرسالة العادية.

```gdb
condition 2 x == 10            # add/change condition on bp 2
condition 2                    # remove condition
condition -force 2 badexpr     # keep even if it cannot be evaluated now
ignore 2 5                     # skip bp 2 the next 5 times
info break                     # shows "breakpoint already hit N times"

commands [BPS]                 # attach command list (default: last bp)
  silent                       # do not print the normal stop message
  printf "x=%d\n", x
  continue                     # auto-continue
end
commands 2-3                   # same list for several breakpoints
commands                       # with no args: last breakpoint created
$bpnum                         # number of the last breakpoint set
$_hit_bpnum / $_hit_locno      # bp number / location number just hit
```

### 5.6 Dynamic Printf (dprintf)

**بالعامية:** `dprintf` = breakpoint بيطبع رسالة ويكمّل، من غير ما توقف. كأنك حطيت `printf` في الكود بس من غير recompile. `set dprintf-style` بتختار مين ينفّذ الـ printf: GDB، أو الـ program نفسه (call), أو الـ agent على gdbserver.

```gdb
dprintf LOCATION,"FORMAT",ARGS...
dprintf file.c:42,"x=%d y=%s\n", x, y
set dprintf-style gdb|call|agent    # who does the printing
set dprintf-function fprintf         # for "call" style
set dprintf-channel stderr           # first arg for the function
set disconnected-dprintf on|off      # keep dprintf running after disconnect (agent)
```

### 5.7 Saving Breakpoints, Static Probes

**بالعامية:** `save breakpoints FILE` بيحفظ كل الـ breakpoints في ملف تقدر تعمله `source` بعدين. الـ static probes (SystemTap / DTrace `USDT`) عبارة عن markers جوه الكود تقدر تحط عليها breakpoints.

```gdb
save breakpoints bps.gdb       # save all bps/wps/catchpoints/dprintf/tracepoints
source bps.gdb                 # restore them
info probes [stap|dtrace] [PROVIDER [NAME [OBJFILE]]]
info probes all
break -probe-stap provider:name       # break on a SystemTap probe
break -probe-dtrace provider:name
break -probe provider:name            # any probe type
enable/disable probes [PROVIDER [NAME]]   # DTrace probes only
$_probe_argc, $_probe_arg0..$_probe_arg11 # probe arguments
$_probe_arg0                    # first argument of the probe
```

### 5.8 Common Breakpoint Errors

**بالعامية:** "Cannot insert breakpoints" غالبًا بيبقى عشان GDB معملش detach صح، أو لأن الـ memory read-only (استخدم `hbreak`). "Breakpoint address adjusted" بتحصل على بعض الـ architectures لما الـ address مش على بداية instruction bundle.

```text
Cannot insert breakpoints:      # another process debugs the target, or memory is read-only
  -> try hbreak, or "set breakpoint always-inserted", or check mem regions (section 13)
Breakpoint address adjusted...  # GDB moved the bp to a valid instruction boundary
```

---

## 6. Stepping & Skipping

### 6.1 Continuing and Stepping

**بالعامية:** `continue` بيكمّل لحد stop تاني. `next` بيمشي سطر ويعدّي على الـ function calls، `step` بيدخل جوّه الـ functions. `finish` بيكمّل لحد ما الـ function الحالية ترجع ويطبع الـ return value. `until` بيكمّل لحد سطر أعلى (مفيد للخروج من loops). `advance` زي `until` بس بـ location. الـ `-i` versions بتشتغل على مستوى الـ instruction.

```gdb
continue [N] / c / fg          # continue; N = ignore this bp N-1 more times
next [N]     / n               # step over (one source line, skip calls) ⭐
step [N]     / s               # step into
stepi [N]    / si              # one machine instruction, step into ⭐
nexti [N]    / ni              # one machine instruction, step over calls ⭐
finish       / fin             # run until current function returns, print value ⭐
set print finish on|off        # print the return value on finish
until        / u               # next line, but do not go BACK in loops
until LOCATION                 # run until LOCATION or current frame returns
advance LOCATION               # run until LOCATION (stops also if frame returns)
display/i $pc                  # auto-show current instruction after each step ⭐

set step-mode on               # step INTO functions without debug info
set step-mode off              # (default) step OVER functions without line info
set range-stepping on|off      # let gdbserver do range stepping (faster)
show step-mode
```

### 6.2 Skipping Functions & Files

**بالعامية:** `skip` بيقول لـ `step` متدخلش في functions أو files معيّنة (زي `std::` أو headers). مفيد جدًا في C++.

```gdb
skip FUNCTION                  # never step into this function
skip -function REGEX_OR_NAME
skip -rfunction ^std::         # regex on function name
skip -file FILE                # skip whole file
skip -gfile *.h                # glob on file name
skip -gfile /usr/include/*     # skip system headers
skip file [FILE]               # old syntax
skip function [FUNC]           # old syntax
info skip                      # list skips
skip delete [N...]             # delete
skip enable  [N...]
skip disable [N...]
```

---

## 7. Signals

**بالعامية:** `info signals` بيوريك GDB بيعمل إيه مع كل signal: يوقف (Stop)، يطبع (Print)، يبعته للبرنامج (Pass). `handle` بيغيّر ده. مثال شائع: `handle SIGPIPE nostop noprint pass`. `signal SIG` بيكمّل البرنامج ويبعتله signal، `signal 0` بيكمّل من غير الـ signal اللي كان واقف عشانه. `queue-signal` بيحط الـ signal في الطابور من غير ما يكمّل.

```gdb
info signals / info handle     # table of all signals and actions
info signals SIGINT            # one signal
handle SIG KEYWORDS...         # change actions; SIG can be name, number, range, "all"
  # keywords: stop / nostop, print / noprint, pass / nopass (= ignore)
handle SIGUSR1 nostop noprint pass   # ignore SIGUSR1 completely
handle SIGSEGV stop print nopass
handle 14-15 nostop
signal SIG                     # continue program and deliver SIG
signal 0                       # continue WITHOUT delivering the pending signal
queue-signal SIG               # queue a signal, do not resume
$_siginfo                      # convenience var: full siginfo of last signal
p $_siginfo._sifields._sigfault.si_addr   # faulting address on SIGSEGV
```

Note: `handle` on a thread-specific signal in non-stop mode applies to the whole program.

---

## 8. Threads, Inferiors, Forks, Checkpoints

### 8.1 Inferiors, Connections & Programs

**بالعامية:** الـ inferior = البرنامج/الـ process اللي GDB بيـ debug فيه. GDB بيقدر يـ debug أكتر من inferior في نفس الوقت (أكتر من process، ممكن على targets مختلفة). كل inferior ليه `program space` (address space) و `connection`.

```gdb
info inferiors                 # list inferiors (* = current)
inferior N                     # switch to inferior N
add-inferior [-copies N] [-exec FILE] [-no-connection]   # create new inferior
clone-inferior [-copies N] [ID]   # clone current inferior
remove-inferiors N...          # remove exited inferiors
detach inferiors N...          # detach
kill inferiors N...            # kill
info connections               # list target connections
info program-spaces / maint info program-spaces
set schedule-multiple on       # resume all inferiors, not just current
set follow-exec-mode new|same  # exec(): new inferior or reuse
show schedule-multiple

$_inferior                     # number of current inferior
break foo inferior 2           # inferior-specific breakpoint
```

### 8.2 Threads

**بالعامية:** `info threads` بيوريك كل الـ threads. `thread N` بينقّلك لـ thread تاني. `thread apply all bt` بيعمل backtrace لكل الـ threads. `set scheduler-locking` بيتحكم مين يتحرّك لما تعمل `step`. الـ all-stop mode (default): لما أي thread يقف، الكل بيقف. الـ non-stop mode: بس الـ thread اللي وقف بيقف.

```gdb
info threads [ID...]           # list threads (* = current); -gid shows global id
thread N          / t N        # switch to thread N
thread 1.2                     # inferior 1, thread 2
thread                         # show current thread
thread apply all CMD           # run CMD on every thread
thread apply all bt            # backtrace of all threads
thread apply all -ascending bt # oldest first
thread apply 1 3-5 CMD         # on some threads
thread apply all -s CMD        # -s: silent on errors/empty output
thread apply all -c CMD        # -c: continue on error
thread apply all -q CMD        # -q: quiet (no thread header)
taas CMD                       # = thread apply all -s CMD
tfaas CMD                      # = thread apply all -s frame apply all -s CMD
thread name NAME               # name the current thread
thread find REGEX              # find threads by name/id/target id
thread apply all -- -p         # "--" if CMD starts with "-"

set print thread-events on|off # print "[New Thread...]" messages
set libthread-db-search-path PATH
set auto-load libthread-db on
maint check libthread-db

# --- scheduling ---
set scheduler-locking off|on|step|replay
  # off: all threads run when you step / continue
  # on:  only the current thread runs
  # step: only current thread runs while stepping; "continue" resumes all
  # replay: (default) like "on" only during replay
show scheduler-locking
set schedule-multiple on|off

# --- all-stop vs non-stop ---
set non-stop on                # must be set BEFORE run/attach
set pagination off             # recommended with non-stop
set target-async on            # old name; async is the default now
show non-stop
continue &                     # run in the background ("&" = async)
run &  / step &  / next &  / attach &   # background versions
interrupt                      # stop the current thread (non-stop)
interrupt -a                   # stop all threads
continue -a                    # resume all threads in non-stop

break foo thread 3             # thread-specific breakpoint
$_thread                       # current thread number
$_gthread                      # global thread number
$_inferior_thread_count        # number of threads in current inferior

# --- interrupted syscalls ---
# In all-stop, a stopped thread's syscall may return EINTR when GDB
# stops it; program should handle EINTR properly.

# --- observer mode (do not modify the target) ---
set observer on|off            # implies may-write-registers/memory off etc.
set may-write-registers off
set may-write-memory off
set may-insert-breakpoints off
set may-insert-tracepoints off
set may-insert-fast-tracepoints off
set may-interrupt off
```

### 8.3 Forks

**بالعامية:** لما البرنامج يعمل `fork`، GDB بيتبع الـ parent بالـ default. `set follow-fork-mode child` بيخلّيه يتبع الـ child. `set detach-on-fork off` بيخلّيه يمسك **الاتنين** كـ inferiors.

```gdb
set follow-fork-mode parent|child   # which side to follow after fork
set detach-on-fork on|off           # off = keep both as inferiors
show follow-fork-mode
catch fork / catch vfork / catch exec
set follow-exec-mode new|same
info inferiors                      # see both processes when detach-on-fork off
```

### 8.4 Checkpoints (Bookmarks)

**بالعامية:** `checkpoint` بياخد snapshot من الـ process (بيستخدم fork جوّاه). تقدر ترجع له بـ `restart N` وتجرّب تاني من نفس النقطة. Linux only.

```gdb
checkpoint                     # save a snapshot of the process
info checkpoints               # list them
restart N                      # go back to checkpoint N
delete checkpoint N            # remove
# Benefit: a restarted checkpoint keeps the same PID -> same addresses
```

---

## 9. Reverse Execution & Process Record

### 9.1 Reverse Execution

**بالعامية:** لو الـ target بيدعم (مثلًا بعد `record`)، تقدر تمشي **للخلف**: `reverse-next`, `reverse-step`, `reverse-continue`... نفس الأوامر العادية بس بالعكس. `set exec-direction reverse` بيقلب كل الأوامر العادية.

```gdb
reverse-continue / rc          # run backward until a breakpoint
reverse-step [N] / rs          # step backward into functions
reverse-stepi    / rsi         # one instruction backward
reverse-next [N] / rn          # step backward over calls
reverse-nexti    / rni
reverse-finish                 # go back to where current function was called
set exec-direction reverse     # make normal step/next/continue go backward
set exec-direction forward
show exec-direction
```

### 9.2 Process Record and Replay

**بالعامية:** `record` بيسجّل كل instruction عشان تقدر تعمل replay و reverse. فيه 3 methods: `full` (software, بطيء بس شغّال في كل مكان)، `btrace bts` و `btrace pt` (hardware branch tracing على Intel، مبيسجّلش data). `record save/restore` بيحفظ الـ log في ملف.

```gdb
record                         # = record full (start recording)
record full
record btrace                  # hardware branch trace (Intel)
record btrace bts              # Branch Trace Store
record btrace pt               # Intel Processor Trace
record btrace ptw              # PT with ptwrite support (py gdb.ptwrite)
record stop                    # stop recording, keep process
record delete                  # delete log after current point
record goto begin|start|end|N  # jump in the log
record instruction-history [RANGE] [/m|/r|/s|/f]  # btrace only
record function-call-history [RANGE] [/l|/c|/i|/s]
record save FILE               # save log to file (record full)
record restore FILE            # load a saved log (needs core file)
info record                    # status
set record full insn-number-max N|unlimited
set record full stop-at-limit on|off
set record full memory-query on|off
set record btrace replay-memory-access read-only|read-write
set record btrace cpu auto|none|VENDOR:PROC/STEP
set record btrace bts buffer-size N
set record btrace pt buffer-size N
set record btrace pt event-tracing on|off
set record btrace pt ptwrite-filter on|off
set record instruction-history-size N
set record function-call-history-size N
```

---

## 10. Examining the Stack

### 10.1 Frames & Backtraces

**بالعامية:** كل function call ليها `frame` على الـ stack. Frame #0 = الـ function اللي واقفين فيها دلوقتي. `backtrace` بيطبع كل الـ frames. `bt full` بيطبع الـ locals كمان. `bt -N` بيطبع آخر N frames (الأقدم). `up`/`down` بينقّلوك بين الـ frames، `frame N` بينقّلك لـ frame معيّنة.

```gdb
backtrace / bt / where / info stack   # print call stack
bt N                           # innermost N frames
bt -N                          # outermost N frames
bt full                        # with local variables
bt -full                       # same (option form)
bt -no-filters                 # ignore Python frame filters
bt -hide                       # hide frames elided by filters
bt -past-main on               # continue past main() into startup code
bt -past-entry on              # continue past the entry point
bt -entry-values no|only|preferred|if-needed|both|compact|default
bt -frame-arguments all|scalars|none|presence
bt -raw-frame-arguments on     # ignore pretty printers for arguments
bt -frame-info auto|source-line|location|source-and-location|location-and-address|short-location
set backtrace past-main on
set backtrace past-entry on
set backtrace limit N          # max frames
set print frame-arguments scalars|all|none|presence
set print frame-info ...
set print entry-values ...
set print raw-frame-arguments on
set filename-display basename|relative|absolute
```

### 10.2 Selecting & Inspecting Frames

```gdb
frame / f                      # print the current frame
frame N / f N                  # select frame by level (0 = innermost)
frame level N
frame address ADDR             # select by stack address
frame function NAME            # select innermost frame of function NAME
frame view STACK_ADDR [PC]     # view a frame that is not on the current stack
up [N]                         # go N frames toward the caller (outer)
down [N]                       # go N frames toward the callee (inner)
up-silently [N] / down-silently [N]   # same without printing
select-frame N                 # select without printing
info frame / info f            # detailed info about selected frame
info frame level N / address A / function F / view A
info args                      # arguments of current frame
info args -q / info args REGEX / info args -t TYPEREGEX
info locals                    # local variables (all nested blocks)
info locals -q REGEX
info registers                 # registers as seen from this frame
frame apply all CMD            # run CMD in every frame
frame apply N CMD              # innermost N frames
frame apply -N CMD             # outermost N
frame apply level 2-4 CMD      # by level
frame apply all -s CMD         # silent errors; also -c, -q, -past-main, -past-entry
faas CMD                       # = frame apply all -s CMD
```

### 10.3 Frame Filters (Python)

**بالعامية:** الـ frame filters عبارة عن Python code بيغيّر شكل الـ backtrace (يخفي frames أو يضيف معلومات). الأوامر دي بتديرها.

```gdb
info frame-filter              # list filters and priorities
disable frame-filter DICT NAME # DICT: global, progspace, or objfile name
enable frame-filter DICT NAME
set frame-filter priority DICT NAME PRIORITY
show frame-filter priority DICT NAME
```

---

## 11. Examining Source Files

### 11.1 Printing Source Lines

**بالعامية:** `list` بيطبع 10 سطور. من غير args بيكمّل من آخر مكان. `list -` بيرجع لورا. `list FUNC` بيطبع حوالين الـ function. `set listsize` بيغيّر عدد السطور.

```gdb
list / l                       # 10 more lines (around current line first time)
list -                         # 10 lines BEFORE the last printed
list +                         # 10 lines after
list .                         # around the current location again
list LINENUM                   # centered on line
list FUNCTION                  # centered on function start
list file.c:42
list 10,20                     # range
list ,20                       # 10 lines ending at 20
list 10,                       # 10 lines starting at 10
list *0x401234                 # around an address
set listsize N|unlimited       # lines per list
show listsize
info source                    # current source file info (compiler, dir, ...)
info line LOCATION             # address range for a source line
info line *0x401234            # which line is at this address
```

### 11.2 Editing, Searching, Source Directories

**بالعامية:** `edit` بيفتح الـ editor (من `$EDITOR`) على السطر الحالي. `search`/`reverse-search` بيدوّر بـ regex في الملف. `directory` بيضيف أماكن يدوّر فيها GDB على الـ source. `set substitute-path` بيبدّل جزء من المسار (لما الـ binary اتعمل build في مكان تاني).

```gdb
edit                           # open editor at current line
edit LOCATION                  # e.g. edit main, edit file.c:20
# uses $EDITOR; e.g. export EDITOR=/usr/bin/vim

search REGEX / forward-search REGEX / fo REGEX
reverse-search REGEX / rev REGEX

directory DIR... / dir DIR...  # add to source path (front)
directory                      # reset to default ($cdir:$cwd)
show directories
set directories DIR:DIR        # replace source path
set substitute-path FROM TO    # e.g. set substitute-path /build/src /home/me/src
unset substitute-path [FROM]
show substitute-path
set source open on|off         # off = never read source files (headers still checked)
show source open
```

### 11.3 Source and Machine Code

**بالعامية:** `disassemble` بيطبع الـ assembly. `/m` أو `/s` بيدمج الـ source مع الـ assembly. `/r` بيطبع الـ raw bytes. `x/i` بيطبع instructions من address. `set disassembly-flavor intel` للي بيفضّل Intel syntax.

```gdb
disassemble / disas            # current function
disassemble FUNC
disassemble 0x400,0x420        # start,end
disassemble 0x400,+32          # start,+length
disassemble /m                 # mixed source+asm (source order; deprecated)
disassemble /s                 # mixed source+asm (address order; better)
disassemble /r                 # raw bytes too
disassemble /b                 # raw bytes, one byte each (for wide-insn arches)
disassemble /ri
x/10i $pc                      # 10 instructions from PC
x/3i main+8
display/i $pc                  # show next instruction at each stop
set disassembly-flavor intel|att   # x86 syntax
set disassemble-next-line on|off|auto
set disassembler-options OPTS  # e.g. "no-aliases" for RISC-V
show disassembler-options
info line *$pc
maint print objfiles           # (see maintenance)
```

---

## 12. Examining Data

### 12.1 print / Expressions

**بالعامية:** `print` (أو `p`) بيقيّم أي expression بلغة البرنامج (C, C++, ...) ويطبعه. النتيجة بتتحط في value history `$1, $2...`. تقدر تستخدم `::` عشان تحدد الـ scope، و `@` عشان تعمل artificial array، و casts، و function calls.

```gdb
print EXPR / p EXPR / inspect EXPR
print                          # print $ again (last value)
print/x EXPR                   # with format (see formats)
print -pretty -- EXPR          # with options (see below)
p var
p arr[3]
p *ptr
p ptr->field
p obj.method(3)                # call a function/method
p func(1, 2)
p (char)x                      # cast
p {int}0x601040                # treat address as int
p sizeof(struct foo)
p $rip                         # registers
p $1 + $2                      # value history
p $                            # last value; $$ = one before; $$3 = 3 before
p 'file.c'::global_var         # variable in another file
p func::static_var             # static in a function
p ns::Class::member            # C++ scope
p &var                         # address
p *arr@10                      # artificial array: 10 elements from arr[0]
p/x arr[0]@5
p arr[1]@3
p $_siginfo
p $_exitcode
p -elements 200 -- big_array
p -array-indexes on -- arr
p -null-stop on -- charbuf     # stop C strings at first NUL
p -object on -- *base_ptr      # print real derived type (C++)
p -vtbl on -- obj
p -static-members off -- obj
p -union on -- u
p -symbol on -- ptr            # print <symbol+off> next to pointers
p -address off -- ptr
p -repeats N -- arr            # "<repeats N times>" threshold
p -max-depth N -- deep_struct
p -memory-tag-violations on -- ptr
p -nibbles on -- /t x          # group binary digits by 4
p -raw-values on -- obj        # ignore pretty printers
p -characters N -- str         # limit chars printed
```

### 12.2 Ambiguous Expressions & Program Variables

**بالعامية:** لو اسم موجود في أكتر من مكان (overloaded / templates / نفس الاسم في ملفين)، GDB يا إما يطبع كله أو يسألك حسب `set multiple-symbols`. الـ variables اللي مش في الـ current frame محتاجة `::` أو تعمل `frame` الأول. لو الـ variable optimized out هتشوف `<optimized out>`.

```gdb
set multiple-symbols all|ask|cancel
p 'file.c'::var                # disambiguate file
p function::var                # disambiguate function-static
p 'foo(int)'                   # quote overloaded C++ names
p ns::foo<int>(x)              # template function
```

### 12.3 Output Formats

**بالعامية:** بعد `/` بتحط format letter (وممكن size). بتشتغل مع `print`, `x`, `display`, `output`.

```text
Format letters (print/FMT):
  x  hexadecimal            d  signed decimal        u  unsigned decimal
  o  octal                  t  binary (two)          a  address + <symbol+off>
  c  character              f  float                 s  string
  z  hex, zero-padded       i  instruction (x only)  r  raw (bypass pretty printer)

Size letters (for x command):
  b  byte (1)   h  halfword (2)   w  word (4)   g  giant (8)
```

```gdb
p/x 255                        # 0xff
p/t 10                         # 1010
p/c 65                         # 65 'A'
p/d 'A'                        # 65
p/a 0x401136                   # 0x401136 <main+4>
p/z 5                          # 0x00000005
p $xmm0.v4_float               # vector register as 4 floats
p/x $sp
p/s buf                        # as string
p/r obj                        # raw, no pretty printer
p/x -1                         # 0xffffffff (width of int)
output EXPR                    # print without "$N =" and newline
output/x EXPR
call EXPR                      # like print but void results are not shown
```

### 12.4 Examining Memory (x)

**بالعامية:** `x/NFU ADDR` = examine memory. N = عدد الوحدات، F = format، U = size. لو معملتش `Enter` على سطر فاضي، بيكمّل من بعد آخر address.

```gdb
x/NFU ADDR                     # N units, format F, unit size U
x/4xw &var                     # 4 words in hex
x/8xb ptr                      # 8 bytes in hex
x/s str                        # C string ⭐
x/2s str                       # 2 strings
x/10i $pc                      # 10 instructions
x/3xg $sp                      # 3 giant (8-byte) words
x/16c buf                      # 16 chars
x/2f &dbl                      # 2 floats (size from type)
x/ax $sp                       # address format
x &var                         # default: last format used
x $sp
$_                             # last address examined
$__                            # contents of last address examined
x/-4xw $sp                     # negative count: memory BEFORE address
```

### 12.5 Memory Tagging (AArch64 MTE)

```gdb
memory-tag print-logical-tag POINTER
memory-tag print-allocation-tag ADDR
memory-tag with-logical-tag POINTER TAG
memory-tag set-allocation-tag ADDR LENGTH TAGS
memory-tag check POINTER       # validate pointer tag vs allocation tag
set print memory-tag-violations on|off
```

### 12.6 Automatic Display

**بالعامية:** `display EXPR` بيطبع الـ expression أوتوماتيك كل ما البرنامج يقف. مفيد لما تمشي بـ `next` وعايز تراقب variable.

```gdb
display EXPR                   # show at every stop
display/FMT EXPR               # e.g. display/x flags
display/i $pc                  # next instruction
display/4xw $sp
undisplay N...                 # remove
delete display N...
disable display N...
enable display N...
info display                   # list
display                        # redisplay all now
```

### 12.7 Print Settings

**بالعامية:** دي كل الـ `set print ...` settings اللي بتتحكم في شكل الـ output. الأهم: `pretty`, `elements`, `object`, `array-indexes`, `null-stop`.

```gdb
set print address on|off       # show addresses next to pointers/strings
set print symbol on|off        # show <symbol> for pointers
set print symbol-filename on   # show file:line for symbols
set print array on|off         # arrays on multiple lines
set print array-indexes on|off # print [0] = ... indexes
set print elements N|unlimited # max array/string elements (default 200)
set print characters N|unlimited|elements   # max string chars
set print repeats N|unlimited  # threshold for "<repeats N times>"
set print null-stop on|off     # stop C arrays of char at NUL
set print pretty on|off        # indent structs
set print raw-frame-arguments on|off
set print raw-values on|off    # bypass pretty printers
set print sevenbit-strings on|off
set print union on|off
set print object on|off        # C++: show real (dynamic) type
set print static-members on|off
set print vtbl on|off
set print demangle on|off      # C++ names
set print asm-demangle on|off  # in disassembly
set demangle-style gnu-v3|auto|...
set print pascal_static-members on|off
set print max-depth N|unlimited
set print max-symbolic-offset N|unlimited
set print type methods on|off  # ptype: show methods
set print type typedefs on|off
set print type nested-type-limit N|unlimited
set print type hex on|off      # sizes/offsets in hex (ptype/o)
set print inferior-events on|off
set print thread-events on|off
set print finish on|off
set print entry-values ...
set print frame-arguments ...
set print frame-info ...
set print nibbles on|off
set print memory-tag-violations on|off
set print symbol-loading off|brief|full
show print ...                 # any of the above
show print                     # all print settings
```

### 12.8 Pretty Printing

**بالعامية:** الـ pretty printers عبارة عن Python scripts بتخلي GDB يطبع types معقدة (زي `std::vector`, `std::map`) بشكل مفهوم. libstdc++ بيجي مع printers جاهزة (auto-load). الأوامر دي بتتحكم فيهم. `/r` بيتخطاهم.

```gdb
info pretty-printer [OBJECT-REGEX [NAME-REGEX]]   # list printers
disable pretty-printer [OBJECT-REGEX [NAME-REGEX]]
enable pretty-printer [OBJECT-REGEX [NAME-REGEX]]
disable pretty-printer global std::vector
p/r vec                        # print raw without printer
set print raw-values on
python print(gdb.pretty_printers)   # global list
```

### 12.9 Value History & Convenience Variables

**بالعامية:** كل `print` بيحفظ نتيجته في `$N`. الـ convenience variables بتبدأ بـ `$` وتقدر تعملها بنفسك (`set $i = 0`). GDB عنده كتير جاهزة (`$_`, `$_exitcode`, `$bpnum`...). شوف section 29 للقائمة الكاملة.

```gdb
p $                            # last value
p $$                           # value before last
p $$N                          # N values back
p $5                           # history entry 5
show values                    # last 10 values
show values N                  # 10 values around N
show values +                  # next 10
set $foo = 42                  # your own convenience variable
set $ptr = list_head
p *$ptr; set $ptr = $ptr->next # walk a linked list (repeat with RET)
p $foo++                       # increment
show convenience / show conv   # list all convenience vars & functions
init-if-undefined $x = 0       # set only if not already set
set var x = 5                  # program variable (use "set var" to avoid clashes)
```

### 12.10 Convenience Functions

```gdb
p $_memeq(buf1, buf2, 16)      # compare memory
p $_streq(s1, s2)              # string equal
p $_strlen(s)
p $_regex(s, "^ab.*")          # regex match
p $_isvoid(EXPR)               # is void?
p $_gdb_setting_str("print elements")   # setting as string
p $_gdb_setting("print elements")       # setting as value
p $_gdb_maint_setting_str(...) / $_gdb_maint_setting(...)
p $_shell("cmd")               # run shell, return exit code
p $_as_string(enum_val)        # value as string (Python)
p $_cimag(z) / $_creal(z)      # complex parts
p $_caller_is("main")          # is caller main? (also $_caller_matches, $_any_caller_is, $_any_caller_matches)
p $_caller_is("f", 2)          # check 2 frames up
help function                  # list all convenience functions
```

---

## 13. Registers, Memory, Core Files

### 13.1 Registers

**بالعامية:** `info registers` بيطبع الـ general registers. `$pc`, `$sp`, `$fp`, `$ps` أسماء موحّدة لكل الـ architectures. `p $rax`, `p/x $eflags`. `info all-registers` بيطبع كل حاجة (floating point, vector).

```gdb
info registers / info reg / i r      # general registers
info registers rax rbx         # specific
info registers rip
info all-registers             # everything (float, vector, system)
info registers general|float|vector|system|all   # by group
maint print reggroups          # available groups
p $pc / p $sp / p $fp / p $ps  # standard names (program counter, stack ptr, frame ptr, status)
p/x $rax
p $xmm0                        # vector register as union
p $xmm0.v4_float[0]
p $ymm0.v8_float
set $rax = 0                   # write a register
set var $pc = 0x401000
p $eflags
info float                     # floating point unit status
info vector                    # vector unit status
x/i $pc
```

### 13.2 OS Auxiliary Info, Memory Regions

**بالعامية:** `info auxv` بيطبع الـ auxiliary vector (من الـ kernel). `info os` بيديك معلومات من الـ OS زي processes, threads, files. `mem` بيعرّف memory regions بصلاحيات (ro/rw/wo) و cache attributes، مفيد للـ embedded.

```gdb
info auxv                      # auxiliary vector (AT_* entries)
info os                        # list OS info types
info os processes|procgroups|threads|files|sockets|shm|semaphores|msg|modules|cpus

mem LOW HIGH ATTRS...          # define memory region
mem 0x1000 0x2000 ro           # read-only
mem 0x2000 0x3000 rw 8         # read-write, 8-byte access
mem auto                       # use target-provided memory map
mem 0x0 0x0 nocache            # attributes: ro rw wo 8 16 32 64 cache nocache
info mem                       # list regions
delete mem N... / disable mem N... / enable mem N...
set mem inaccessible-by-default on|off
show mem inaccessible-by-default
```

### 13.3 Copy Memory <-> File, Core Files

**بالعامية:** `dump` بيحفظ memory أو value في ملف (binary, ihex, srec, tekhex, verilog). `restore` بيرجّعه للـ memory. `generate-core-file` (أو `gcore`) بيعمل core dump من البرنامج الشغّال. `core-file` بيفتح core.

```gdb
dump [FORMAT] memory FILE START END      # FORMAT: binary(default) ihex srec tekhex verilog
dump [FORMAT] value FILE EXPR
dump binary memory mem.bin 0x400000 0x401000
dump ihex value out.hex arr
append [binary] memory FILE START END
append [binary] value FILE EXPR
restore FILE [binary] [BIAS START END]   # load file into memory
restore mem.bin binary 0x400000

generate-core-file [FILE] / gcore [FILE]    # write core of running process
set use-coredump-filter on|off # honor /proc/PID/coredump_filter
set dump-excluded-mappings on|off
core-file FILE / core FILE     # load core file
core-file                      # discard core
target core FILE
info proc mappings             # memory map (Linux)
```

```bash
ulimit -c unlimited            # allow core dumps in the shell
cat /proc/sys/kernel/core_pattern   # where cores go
coredumpctl gdb                # systemd systems
```

### 13.4 Character Sets, Caching, Search Memory, Value Sizes

```gdb
set charset CHARSET            # both host & target
set host-charset / set target-charset / set target-wide-charset
show charset
set charset UTF-8

set remotecache on|off         # cache target memory (remote)
set stack-cache on|off
set code-cache on|off
info dcache [line]             # data cache stats
maint flush dcache             # (maint) clear cache

find [/SIZE-CHAR] [/MAX-COUNT] START, END, VAL1 [, VAL2...]
find [/SIZE-CHAR] [/MAX-COUNT] START, +LENGTH, VAL1...
find &buf[0], +100, "hello"    # search a string
find/w 0x400000, 0x500000, 0xdeadbeef   # search 4-byte value
find/1 ...                     # stop at first match (max count 1)
$_                             # address of last match
$numfound                      # number of matches

set max-value-size N|unlimited # error if value bigger than N bytes (default 64k)
show max-value-size
```

---

## 14. Optimized Code, Macros

### 14.1 Inline Functions & Tail Calls

**بالعامية:** في الكود الـ optimized، الـ inline functions بتظهر في الـ backtrace كـ frames وهمية. `step` بيدخلهم، `finish` بيخرج منهم. الـ tail-call frames بتظهر لو الـ compiler سجّلها (`-O2` + DWARF). لو شفت `<optimized out>` يبقى الـ variable مش موجودة في الـ register/memory دلوقتي.

```gdb
info frame                     # shows "inlined into frame N"
set debug entry-values 1       # debug tail-call detection
set print entry-values compact # show foo@entry=... values
info locals                    # may show <optimized out>
```

### 14.2 C Preprocessor Macros

**بالعامية:** لو عملت compile بـ `-g3`، GDB بيعرف الـ macros. `macro expand` بيوريك الـ expansion، `info macro` بيوريك التعريف ومكانه. تقدر تعرّف macros مؤقتة بـ `macro define`.

```gdb
macro expand EXPR / macro exp   # show fully expanded expression
macro expand-once EXPR          # expand only one level
info macro [-a|-all] NAME       # definition of macro (all definitions with -a)
info macro -- -MACRO_NAME       # "--" if name starts with "-"
info macros [LOCATION]          # all macros visible at location
macro define NAME(ARGS) BODY    # user macro
macro define PI 3.14
macro undef NAME
macro list                      # user-defined macros
p SOME_MACRO(3)                 # GDB expands macros in expressions
```

---

## 15. Tracepoints

**بالعامية:** الـ tracepoints بتجمع data من البرنامج من غير ما توقّفه (مفيد للـ real-time / embedded). محتاج target يدعم (`gdbserver` بيدعم). بتعرّف tracepoint + `actions` تقول تجمع إيه، تعمل `tstart`، البرنامج يجري، `tstop`، وبعدين تتصفح الـ trace frames بـ `tfind`.

```gdb
# --- create / delete ---
trace LOCATION / tr / tp / tracepoint   # set tracepoint
ftrace LOCATION                # fast tracepoint (needs in-process agent)
strace LOCATION                # static tracepoint (UST markers)
strace -m MARKER               # by marker id
info tracepoints [N] / info tp
delete tracepoints [N...]      # delete
disable tracepoints [N...] / enable tracepoints [N...]
passcount COUNT [N]            # stop tracing after N hits
condition N EXPR               # conditional tracepoint
trace foo if x > 3

# --- trace state variables ---
tvariable $name [= EXPR]       # create trace state variable
info tvariables
delete tvariable [$name...]

# --- actions ---
actions [N]                    # define actions (end with "end")
  collect EXPR, EXPR...        # e.g. collect $regs, $locals, $args, $_ret, $_sdata, *ptr@10
  collect/s str                # collect as string
  teval EXPR                   # evaluate, no collect (e.g. teval $count++)
  while-stepping N / stepping N / ws N   # collect while single-stepping N times
    collect $pc
  end
end
set default-collect EXPR...    # collect these at every tracepoint
info static-tracepoint-markers # list UST markers

# --- run the experiment ---
tstart [NOTES]                 # start tracing
tstop [NOTES]                  # stop
tstatus                        # status
set disconnected-tracing on|off   # keep tracing after GDB disconnects
set circular-trace-buffer on|off
set trace-buffer-size N|unlimited
set trace-user NAME / set trace-notes TEXT / set trace-stop-notes TEXT

# --- examine collected data ---
tfind [start]                  # first frame
tfind none                     # exit trace-frame mode
tfind end                      # last
tfind / tfind next             # next frame
tfind -                        # previous
tfind N                        # frame number N
tfind tracepoint N             # next frame collected by tracepoint N
tfind pc ADDR
tfind range START, END
tfind outside START, END
tfind line [FILE:]LINE
tdump                          # show all data of current trace frame
save tracepoints FILE          # save tracepoint definitions
$trace_frame                   # current frame number (-1 if none)
$tracepoint                    # tracepoint number of current frame
$trace_line / $trace_file / $trace_func
$tpnum                         # last tracepoint number set
$_sdata                        # static tracepoint data

# --- trace files ---
tsave [-r] [-ctf] FILE         # save trace data (-r: remote saves; -ctf: CTF format)
target tfile FILE              # open a saved trace file
target ctf DIR                 # open CTF trace directory
```

---

## 16. Overlays

**بالعامية:** الـ overlays نظام قديم للـ embedded: أجزاء من الكود بتتحمّل في نفس الـ memory بالتبادل. GDB محتاج يعرف أنهي overlay "mapped" دلوقتي عشان الـ breakpoints تشتغل.

```gdb
overlay off                    # disable overlay support
overlay manual                 # you tell GDB what is mapped
overlay map-overlay OVERLAY / overlay map OVERLAY
overlay unmap-overlay OVERLAY / overlay unmap OVERLAY
overlay auto                   # GDB reads _ovly_table from the program
overlay load-target / overlay load   # re-read the overlay table
overlay list-overlays / overlay list
# program side: _ovly_table, _novlys, _ovly_debug_event()
```

---

## 17. Languages

**بالعامية:** GDB بيفهم أكتر من لغة (C, C++, D, Go, Objective-C, OpenCL C, Fortran, Pascal, Rust, Modula-2, Ada, Asm, Minimal). بيختار اللغة أوتوماتيك من الـ source file extension. `set language` بيغيّرها يدوي (بيأثر على syntax الـ expressions).

```gdb
show language                  # current working language
set language auto|local        # infer from frame (default)
set language c|c++|d|go|objective-c|opencl|fortran|pascal|rust|modula-2|ada|asm|minimal
info frame                     # shows source language
info source                    # shows language of file
set check type on|off          # type checking
set check range on|off|warn    # range checking (Modula-2, Pascal, Ada)
show check type / show check range

# C / C++
set print demangle on
set overload-resolution on|off # C++ overload resolution in expressions
p obj.*memfn                   # pointer to member
p dynamic_cast<D*>(base)       # casts: dynamic_cast, static_cast, reinterpret_cast, const_cast
p sizeof(T)                    # sizeof works on types and expressions
p ns::var
p this->x                      # "this" is available
info vtbl OBJ                  # print virtual table
set cp-abi auto|gnu-v3
show cp-abi
rbreak Class::.*               # break on all methods

# D / Go / Rust / Objective-C
info classes [REGEX]           # Objective-C classes
info selectors [REGEX]         # Objective-C selectors
p [obj message]                # ObjC method call in expressions
p x as u32                     # Rust cast syntax; p x.0 for tuple field
p mod::item                    # Rust paths

# Fortran
info common [NAME]             # COMMON blocks
set fortran repack-array-slices on|off
p arr(1:5:2)                   # Fortran array slice
p SIZE(arr) / p LBOUND(arr) / p UBOUND(arr) / p KIND(x)  # intrinsics

# Ada
info tasks                     # Ada tasks
task N                         # switch task
task apply all CMD / task apply 1 2 -s CMD
break LOC task N
set ada print-signatures on|off
set ada trust-PAD-over-XVS on|off
set ada source-charset CHARSET
catch exception / catch handlers / catch assert
set print pascal_static-members
```

---

## 18. Symbols

**بالعامية:** الأوامر دي بتسألك GDB عن الـ symbol table: `whatis` = type الـ expression، `ptype` = التعريف الكامل للـ type (`/o` بيطبع offsets عشان تعرف الـ struct layout). `info functions/variables/types` بيدوّروا بـ regex. `info scope`, `info address`, `info symbol`.

```gdb
info address SYMBOL            # where is SYMBOL stored (register, static, ...)
info symbol ADDR               # which symbol is at ADDR (e.g. main + 4 in section .text)
whatis EXPR                    # type of expression (one level)
whatis TYPE / whatis struct foo
ptype EXPR / ptype TYPE        # full type definition
ptype/o struct foo             # with offsets and sizes (struct layout, padding)
ptype/r ...                    # raw, no typedef substitution; /m no methods, /t no typedefs
ptype/x struct foo             # offsets in hex; /d decimal
info types [REGEX]             # types matching regex
info types -q REGEX            # quiet: no file headers
info scope LOCATION            # all variables local to a scope
info source
info sources [-dirname|-basename] [-- ] [REGEX]   # all source files
info functions [REGEX]         # functions (with -q, -n to skip non-debug, -t TYPEREGEX)
info functions -n ^foo         # exclude non-debugging symbols
info variables [REGEX]         # global/static variables
info variables -q -t int$ REGEX
info line LOCATION
info modules [-q] [REGEX]      # Fortran modules
info module functions / info module variables [-m MODREGEX] [-t TYPEREGEX] [REGEX]
info classes / info selectors  # Objective-C
info vtbl OBJ                  # C++ vtable
info set                       # all settings
set opaque-type-resolution on|off
set print type ...             # see print settings
maint print symbols / maint print psymbols / maint print msymbols FILE
maint info symtabs / maint info psymtabs
maint expand-symtabs [REGEX]
maint set symbol-cache-size N
maint print symbol-cache / maint print symbol-cache-statistics / maint flush symbol-cache
demangle [-l LANG] [--] NAME   # demangle a C++ (or other) mangled name
set demangle-style gnu-v3
```

---

## 19. Altering Execution

**بالعامية:** تقدر تغيّر البرنامج وهو شغّال: تعدّل variables (`set var`)، تنط لسطر تاني (`jump`)، ترجع من function بقيمة معيّنة (`return`)، تنادي functions (`call`)، أو حتى تعدّل الـ executable نفسه (`set write on`). `compile` بيخلّيك تكتب C code جوه GDB يتـ compile ويتحقن في البرنامج.

```gdb
# --- assignment ---
set var x = 10                 # "set var" avoids clash with GDB "set" subcommands
set var arr[2] = 5
set var ptr->field = 'c'
set var $rax = 0
p x = 10                       # also assigns
set {int}0x601040 = 4          # write memory
set var buf = "hello"          # only for char arrays of the right size

# --- change control flow ---
jump LOCATION / j              # continue at LOCATION (does not change stack!)
jump 42 / jump *0x401000
tbreak 50 ; jump 42            # jump and stop at 50
set var $pc = 0x401000         # move PC without continuing
return [EXPR]                  # pop frame, return EXPR to caller (asks confirm)
finish                         # normal return

# --- signals ---
signal SIG / signal 0 / queue-signal SIG

# --- calling functions ---
call FUNC(ARGS)                # call; void result not printed
print FUNC(ARGS)               # call; prints result
call (void)free(ptr)
p strlen("abc")                # works if libc has symbols
p ((int(*)(const char*))puts)("hi")   # cast when no debug info
set unwindonsignal on|off      # unwind stack if called function crashes
set unwind-on-timeout on|off
set direct-call-timeout N / set indirect-call-timeout N   # seconds (threads)
set unwind-on-terminating-exception on|off   # C++ exception in called fn
set may-call-functions on|off  # off = forbid all inferior calls
show may-call-functions

# --- patching the executable / core ---
set write on                   # open exec and core for writing (then "file" again)
set write off
show write
file prog                      # reload after set write on

# --- compile & inject code (needs GCC + libcc1) ---
compile code CODE              # compile and run C code in the inferior
compile code printf("x=%d\n", x);
compile code                   # multi-line, end with "end"
compile file FILE              # compile a file
compile file -raw FILE
compile print EXPR             # evaluate using the compiler
compile print/x EXPR
compile print -- 
set compile-args ARGS          # extra compiler flags (default: -O0 -gdwarf-4 -fPIE ...)
show compile-args
set compile-gcc PATH           # which gcc to use
show compile-gcc
```

---

## 20. GDB Files, Separate Debug Info, debuginfod

### 20.1 Commands to Specify Files

**بالعامية:** `file` بيحدد الـ executable + symbols. `symbol-file` symbols بس، `exec-file` executable بس. `add-symbol-file` بيضيف symbols لـ address معيّن (kernel modules, JIT). `info sharedlibrary` بيوريك الـ .so اللي متحمّلة. `set sysroot` مهم جدًا في remote/cross debugging عشان GDB يلاقي الـ libs بتاعة الـ target.

```gdb
file [FILE]                    # executable + symbols; no arg = discard both
file -readnow FILE / file -readnever FILE
exec-file [FILE]               # executable only
symbol-file [FILE] [-o OFFSET] # symbols only
symbol-file -readnow FILE
core-file [FILE] / core FILE
add-symbol-file FILE [-readnow|-readnever] [-o OFF] [TEXTADDR] [-s SECTION ADDR]...
add-symbol-file mod.ko 0xffffffffc0000000 -s .data 0xffff...
remove-symbol-file FILE / remove-symbol-file -a ADDR
add-symbol-file-from-memory ADDR
section SECTION ADDR           # relocate one section
info files / info target       # all files & sections in use
info sharedlibrary [REGEX] / info share / info dll   # loaded shared libs
sharedlibrary [REGEX] / share  # load symbols of shared libs now
nosharedlibrary                # unload all shared-lib symbols
set auto-solib-add on|off      # auto load shared lib symbols
set stop-on-solib-events 0|1   # stop when a lib is loaded/unloaded
set sysroot PATH / set solib-absolute-prefix PATH   # where target libs are
set sysroot target:            # read libs from the remote target
set sysroot remote:            # older spelling of target:
set solib-search-path PATH:PATH
show sysroot / show solib-search-path
set trust-readonly-sections on # read read-only sections from exec file, not target
set exec-file-mismatch ask|warn|off   # when attach exec != file
load [FILE] [OFFSET]           # download program to target (remote/sim)
```

### 20.2 File Caching, Separate Debug Info

**بالعامية:** الـ debug info ممكن تكون في ملف منفصل (`.debug`) عن طريق `debug link` أو `build-id`. GDB بيدوّر عليها في `/usr/lib/debug` والمسارات في `debug-file-directory`. `objcopy` بيفصلهم.

```gdb
set debug-file-directory DIRS  # where to look for separate debug files
show debug-file-directory
set debug-file-directory /usr/lib/debug:/home/me/dbg
set build-id-verbose 0|1|2
info sharedlibrary             # "(*)" = no debug info
maint set bfd-sharing on|off   # file caching
maint flush bfd-cache / maint info bfd
```

```bash
# create a separate debug file
objcopy --only-keep-debug prog prog.debug
objcopy --strip-debug prog
objcopy --add-gnu-debuglink=prog.debug prog
# build-id style: /usr/lib/debug/.build-id/xx/yyyy....debug
readelf -n prog | grep Build   # show build-id
# MiniDebugInfo: .gnu_debugdata section (xz-compressed symtab, Fedora style)
```

### 20.3 Index Files (faster symbol loading)

```gdb
save gdb-index [-dwarf-5] DIR  # write .gdb_index / .debug_names into DIR/FILE
set index-cache enabled on|off # cache indexes automatically
set index-cache directory DIR
show index-cache stats
maint set dwarf-max-cache-age N
```

```bash
gdb -batch -ex "save gdb-index ." prog
objcopy --add-section .gdb_index=prog.gdb-index --set-section-flags .gdb_index=readonly prog
ld --gdb-index                 # gold linker can build it at link time
```

### 20.4 Errors Reading Symbols & GDB Data Files

```gdb
set complaints N               # how many symbol-reading complaints to show (0 default)
show complaints
set data-directory DIR         # where GDB's own data (python, syscalls XML) lives
show data-directory
```

### 20.5 debuginfod

**بالعامية:** `debuginfod` خدمة بتنزّل الـ debug info و source files من server أوتوماتيك (Fedora, Debian, Ubuntu عندهم servers). لازم `DEBUGINFOD_URLS` متعرّفة.

```bash
export DEBUGINFOD_URLS="https://debuginfod.ubuntu.com"   # or fedoraproject / debian
```

```gdb
set debuginfod enabled on|off|ask
set debuginfod urls URLS
set debuginfod verbose 0|1
show debuginfod enabled / show debuginfod urls
```

---

## 21. Targets & Remote Debugging (gdbserver)

### 21.1 Targets

**بالعامية:** الـ target = الحاجة اللي GDB بيتعامل معاها: native process، remote (gdbserver / JTAG stub)، core file، simulator، record. `info files` بيوريك الـ active targets.

```gdb
target TYPE PARAMS             # connect to a target
target native                  # local process
target core FILE
target exec FILE
target remote HOST:PORT        # gdbserver / stub over TCP
target remote /dev/ttyS0       # serial
target remote | CMD            # over a pipe
target extended-remote HOST:PORT   # extended: run/attach/restart on remote
target sim [ARGS]              # built-in simulator
target tfile FILE / target ctf DIR   # trace files
help target                    # list available targets
info files
detach / disconnect / kill
load [FILE] [OFFSET]           # download to target memory
flash-erase                    # erase flash memory (remote)
set endian big|little|auto     # byte order
show endian
set architecture ARCH / set arch   # e.g. i386:x86-64, arm, riscv:rv64
show architecture
set osabi OSABI                # e.g. GNU/Linux, none
show osabi
set gnutarget FORMAT           # BFD target format (e.g. elf32-littlearm)
set hash on|off                # print "#" while loading (remote)
set debug remote 1             # print remote protocol packets
```

### 21.2 Connecting to a Remote Target

```gdb
target remote 192.168.1.10:2345
target remote localhost:2345
target remote :2345
target remote tcp:HOST:PORT / udp:HOST:PORT
target remote unix:/path/socket        # Unix domain socket
target remote /dev/ttyUSB0             # serial (see set serial baud)
target extended-remote HOST:PORT
set remote exec-file /path/on/target   # program to run (extended-remote)
run                            # only in extended-remote mode
attach PID                     # remote attach (extended-remote)
monitor CMD                    # send command to gdbserver/stub
monitor help
monitor exit                   # stop gdbserver
monitor set debug 1
disconnect                     # leave gdbserver running
detach                         # detach and let program continue
set serial baud RATE / set remotebaud
set serial parity none|odd|even
set remotetimeout SECONDS
set remotelogfile FILE / set remotelogbase hex|octal|ascii
set remote interrupt-sequence Ctrl-C|BREAK|BREAK-g
set remote interrupt-on-connect on|off
set remoteflow on|off
set remote hardware-breakpoint-limit N / hardware-watchpoint-limit N
set remote hardware-watchpoint-length-limit N
set remote exec-file FILE
set remote PACKET-NAME-packet on|off|auto   # e.g. set remote Z-packet off
show remote                    # all remote settings
set tcp connect-timeout SECONDS|unlimited
set tcp auto-retry on|off
set remote multiprocess-feature-packet on
set sysroot target:            # read files from target
remote get TARGETFILE HOSTFILE # file transfer
remote put HOSTFILE TARGETFILE
remote delete TARGETFILE
set remote system-call-allowed 0|1   # File-I/O extension: allow system()
show remote system-call-allowed
```

### 21.3 gdbserver

**بالعامية:** `gdbserver` برنامج صغير بيتحط على الـ target machine ويتكلم مع GDB على الـ host. مفيد للـ embedded Linux وللـ containers. الـ `--multi` mode بيخلّيه يفضل شغّال وتقدر تعمل run/attach أكتر من مرة.

```bash
# --- on the target ---
gdbserver :2345 ./prog args    # listen on TCP port 2345
gdbserver host:2345 ./prog     # host part is ignored
gdbserver /dev/ttyS0 ./prog    # serial
gdbserver --attach :2345 PID   # attach to running process
gdbserver --multi :2345        # extended mode, wait for GDB commands
gdbserver --once :2345 ./prog  # exit after GDB disconnects
gdbserver --debug / --remote-debug / --event-loop-debug
gdbserver --debug-file=FILE
gdbserver --wrapper env FOO=bar -- :2345 ./prog
gdbserver --disable-randomization / --no-disable-randomization
gdbserver --startup-with-shell / --no-startup-with-shell
gdbserver --disable-packet=vCont,threads,Tthread,qC
gdbserver --version / --help

# --- on the host ---
gdb ./prog                     # same binary (with symbols)
(gdb) target remote TARGET:2345
(gdb) set sysroot /path/to/target/rootfs   # so libs match
(gdb) b main
(gdb) c                        # gdbserver already started the program
```

```gdb
# gdbserver monitor commands
monitor help
monitor set debug 0|1
monitor set debug-format all|none|timestamp
monitor set remote-debug 0|1
monitor set event-loop-debug 0|1
monitor set debug-file FILE
monitor set libthread-db-search-path PATH
monitor exit
```

### 21.4 Remote Stub (bare metal)

**بالعامية:** لو بتعمل debugging على board من غير OS، بتلنك stub (زي `i386-stub.c`) مع البرنامج وبيتكلم مع GDB بالـ Remote Serial Protocol. لازم تكتب `getDebugChar`, `putDebugChar`, `exceptionHandler`, `flush_i_cache` وتنادي `set_debug_traps()` ثم `breakpoint()`.

```c
/* in your program */
set_debug_traps();             /* install handlers */
breakpoint();                  /* stop so GDB can connect */
```

---

## 22. Configuration-Specific & Architecture Notes

**بالعامية:** أوامر خاصة بأنظمة أو معالجات معيّنة. الأهم للـ Linux: `info proc`. للـ Windows: `info dll`, `info w32`. للـ ARM/AArch64/x86/RISC-V فيه settings خاصة.

```gdb
# --- Linux / native process info ---
info proc [PID|FILE]           # process summary
info proc mappings             # memory map
info proc stat / status / cmdline / cwd / exe / files / all
set procfs-trace on|off / set procfs-file FILE / proc-trace-entry ...   # Solaris procfs
info pidlist / info meminfo    # QNX Neutrino

# --- BSD ---
kvm pcb / kvm proc             # libkvm (crash dumps)

# --- MS Windows ---
info w32 / info w32 thread-information-block
set cygwin-exceptions on|off
set new-console on|off         # program in its own console
set new-group on|off
set shell on|off
set debugevents / debugexec / debugexceptions / debugmemory on|off
info dll                       # = info sharedlibrary
set stop-on-solib-events 1

# --- DJGPP (DOS) ---
info dos / info dos sysinfo / gdt / ldt / idt / pde / pte / address ADDR
set com1base / com1irq ...

# --- Hurd ---
set signals / set sigs on|off
set signal-thread THREAD / set sigthread
set stopped on|off
set exceptions on|off
set task pause on|off / set task detach-suspend-count N / set task exception-port PORT
set thread pause / thread run / thread detach-suspend-count / thread exception-port ...
set noninvasive on|off

# --- Darwin (macOS) ---
set debug darwin N / set debug mach-o N
set mach-exceptions on|off

# --- FreeBSD ---
set debug fbsd-lwp / set debug fbsd-nat

# --- Embedded OS / processors ---
set debug arc / set debug rl78 / ...
# ARM
set arm disassembler STYLE / show arm disassembler
set arm apcs32 on|off
set arm fpu fpa|softfpa|fpa|vfp / show arm fpu
set arm abi auto|APCS|AAPCS
set arm fallback-mode arm|thumb|auto
set arm force-mode arm|thumb|auto
set arm unwind-secure-frames on|off
set debug arm 0|1
target rdi / rdp               # old Angel stubs (removed in modern GDB)
# AArch64
info registers sve / za / zt
set debug aarch64 0|1
# SVE: $vg, $z0-$z31, $p0-$p15, $ffr ; SME: $svg, $svcr, $za ; SME2: $zt0
# MTE: memory-tag commands (section 12.5)
# PAC: bt shows [PAC] marker; GCS: $gcs_features_enabled etc.
# BPF
# M68k, MicroBlaze, MIPS Embedded
set mipsfpu double|single|none|auto / show mipsfpu
set mips abi auto|o32|o64|n32|n64|eabi32|eabi64 / show mips abi
set mips compression mips16|micromips
set mips mask-address on|off|auto
set remote-mips64-transfers-32bit-regs on|off
set debug mips 0|1
pmon CMD                       # MIPS PMON monitor
# OpenRISC 1000
# PowerPC Embedded
set powerpc vector-abi auto|generic|altivec|spe
set powerpc soft-float on|off
set powerpc exact-watchpoints on|off
info spu ...                   # removed
# AVR
# CRIS
set cris-version N / set cris-mode guru|normal / set cris-dwarf2-cfi on|off
# Super-H
# x86
info registers eflags / st0-st7 / mxcsr
set debug x86-nat / x86-linux
# CET (shadow stack): $pl3_ssp ; info registers pl3_ssp
# Alpha, HPPA
set debug hppa 1
maint print unwind ADDR        # HPPA unwind
# PowerPC
set debug ppc-linux / set debug xcoffread
# Sparc64 ADI
adi examine ADDR [/ N] / adi assign ADDR [/ N] VALUE
# S12Z
# AMD GPU (ROCm)
info agents / info queues / info dispatches   # AMD GPU entities (ROCgdb)
set debug amd-dbgapi-lib log-level LEVEL
set debug amd-dbgapi on|off
$_wave_id, $_dispatch_pos, $_dispatch_id, $_queue_id, $_agent_id   # AMD GPU vars
# RISC-V
set riscv use-compressed-breakpoints auto|on|off
set debug riscv breakpoints|infcall|unwinder|gdbarch 0|1
set riscv numeric-register-names on|off
```

---

## 23. Controlling GDB — Settings

**بالعامية:** كل حاجة بتتحكم في *شكل* و*سلوك* GDB نفسه: الـ prompt، الـ history، حجم الشاشة، الألوان (styling)، الأرقام (radix)، الـ ABI، auto-load، التحذيرات، الـ debug output.

### 23.1 Prompt, Editing, History, Screen

```gdb
set prompt (gdb-app)           # change the prompt (trailing space matters)
set prompt \033[1;31m(gdb)\033[0m   # colored prompt
show prompt
set editing on|off             # readline line editing
show editing
set history filename FILE      # default ~/.gdb_history or $GDBHISTFILE
set history save on|off        # save history on exit
set history size N|unlimited   # $GDBHISTSIZE
set history remove-duplicates N|unlimited
set history expansion on|off   # "!" history expansion
show history                   # all history settings
show commands                  # last 10 commands
show commands N / show commands +

set height N|unlimited|0       # lines per page (0 = no paging)
set width N|unlimited|0        # columns
set pagination on|off          # "--Type <RET>--"
show height / show width
```

### 23.2 Output Styling (colors)

```gdb
set style enabled on|off       # colors on/off
set style sources on|off       # colorize source (uses GNU Source Highlight / pygments)
set style disassembler enabled on|off   # libopcodes colors
set style tui-current-position on|off
set style filename foreground COLOR      # COLOR: none black red green yellow blue magenta cyan white, or 0-255, or #RRGGBB
set style filename background COLOR
set style filename intensity normal|bold|dim
set style function foreground green
set style variable foreground cyan
set style address foreground blue
set style title ...
set style highlight ...        # matches in apropos etc.
set style metadata ...         # <optimized out> etc.
set style version ...
set style tui-border foreground / tui-active-border / tui-border-style ...
set style disassembler mnemonic|register|immediate|address|symbol|comment ...
set style line-number ...
set style command ...
set style warning-prefix TEXT / set style error-prefix TEXT
show style                     # all styles
```

### 23.3 Numbers, ABI

```gdb
set radix 16                   # input AND output radix (8, 10, 16)
set input-radix 16             # 0x not needed; careful: "10" means 16!
set output-radix 16
show radix / show input-radix / show output-radix

set osabi OSABI / show osabi
set cp-abi auto|gnu-v3
set coerce-float-to-double on|off   # float args to functions without prototype
set unwindonsignal ...
```

### 23.4 Auto-loading

**بالعامية:** GDB بيحمّل أوتوماتيك ملفات زي `.gdbinit` في الـ current dir، `libthread_db`، والـ Python scripts (`prog-gdb.py`). عشان الأمان مبيحمّلش إلا من `safe-path`. لو شفت warning "File ... auto-loading has been declined"، ضيف المسار لـ `add-auto-load-safe-path`.

```gdb
set auto-load off              # disable all auto-loading
set auto-load local-gdbinit on|off
set auto-load libthread-db on|off
set auto-load gdb-scripts on|off       # OBJFILE-gdb.gdb
set auto-load python-scripts on|off    # OBJFILE-gdb.py
set auto-load guile-scripts on|off     # OBJFILE-gdb.scm
set auto-load scripts-directory DIRS   # $debugdir:$datadir/auto-load
set auto-load safe-path DIRS   # trusted directories; "/" = everything
add-auto-load-safe-path DIR
add-auto-load-scripts-directory DIR
show auto-load                 # all
info auto-load                 # what was loaded / declined
info auto-load local-gdbinit / libthread-db / gdb-scripts / python-scripts / guile-scripts
set debug auto-load on         # show files tried
```

### 23.5 Warnings, Messages, Confirmations, Debug Output

```gdb
set confirm on|off             # ask before dangerous commands
set verbose on|off             # messages while loading symbols
set complaints N
set trace-commands on|off      # echo each command as executed (+ nesting)
set exec-done-display on|off   # "completed." after async commands
set print inferior-events on|off
set print thread-events on|off
set print symbol-loading full|brief|off
set suppress-cli-notifications on|off   # for front ends
set startup-quietly on
set debuginfod ...

set debug ...                  # internal debug output (many: infrun, remote, lin-lwp, ...)
set debug infrun 1             # very useful for stepping/threads problems
set debug remote 1
set debug lin-lwp 1
set debug frame 1
set debug dwarf-read N / set debug dwarf-die N / dwarf-line N
set debug expression 1
set debug symtab-create N / symbol-lookup N
set debug target N
set debug threads 1
set debug event-loop off|all|all-except-ui
set debug py-unwind / py-breakpoint / py-micmd 1
set debug separate-debug-file 1
set debug notification / observer / overload / parser / serial / stack-cache ...
show debug                     # all debug settings
set debug timestamp on|off     # timestamps on debug output
set displaced-stepping on|off|auto   # step over breakpoints out of line
set schedule-multiple ...
set interactive-mode on|off|auto
set trace-commands on
set unwind-on-signal ...
set may-call-functions ...
set stack-cache / set code-cache ...
set backtrace ...
set exec-wrapper ...
set filename-display ...
set extended-prompt TEXT       # (Python) prompt with \f, \p{setting}, \w, ... substitutions
show extended-prompt
```

---

## 24. Extending GDB — Scripts, Python, Guile

### 24.1 User-defined Commands (CLI scripting)

**بالعامية:** تقدر تعرّف أوامر بتاعتك بـ `define` (تاخد `$arg0..$arg9`, `$argc`). فيه `if/while/loop_break/loop_continue`. `hook-CMD` بيتنفذ **قبل** أمر معيّن، `hookpost-CMD` **بعده**. `source` بيشغّل ملف أوامر. `echo`, `printf`, `output` للطباعة.

```gdb
define NAME                    # define a command (end with "end")
  if $argc == 0
    printf "usage: NAME ARG\n"
  else
    print $arg0 * 2
  end
end
define-prefix NAME             # make NAME a prefix so you can "define NAME sub"
document NAME                  # add help text (end with "end")
  Doubles the argument.
end
help NAME / help user-defined  # list user commands
show user [NAME]               # show definition
dont-repeat                    # inside define: do not repeat on RET

# control flow (inside define / command files)
if EXPR ... else ... end
while EXPR ... end
loop_break / loop_continue
$argc / $arg0 ... $arg9        # arguments (text substitution)
$_gdb_setting("...")           # read settings

# hooks
define hook-echo               # runs BEFORE "echo"
  echo <<<---
end
define hookpost-echo           # runs AFTER
  echo --->>>
end
define hook-stop               # runs every time the program stops (very useful)
  x/i $pc
end
# hook-run, hook-continue etc. also possible

# command files
source FILE                    # run commands from file
source -v FILE                 # echo each command
source -s FILE                 # search in source path
gdb -x FILE                    # from shell
# lines starting with # are comments; errors abort the file

# output
echo TEXT\n                    # print text (\n for newline, \  for leading space)
output EXPR / output/FMT EXPR  # print value only
printf "FORMAT", ARGS...       # C-style printf; supports %s %d %x %f %c %p %%
printf "%s at %p\n", name, &name
printf "%5.2f\n", 3.14159
printf "%ls\n", widestr        # wide strings
printf "%lld %llu\n", ...      # 64-bit
eval "FORMAT", ARGS...         # build a command from a format and run it
eval "p $%d", 5                # -> p $5
```

### 24.2 Command Aliases

```gdb
alias NEW = OLD                # e.g. alias bt5 = backtrace 5
alias -a NEW = OLD             # abbreviation (not shown in help)
alias pp = print -pretty --    # alias with default args
alias spe = set print elements
alias -a set print elms = set print elements   # multi-word alias
help aliases
```

### 24.3 Python — Commands

**بالعامية:** GDB بيجي بـ Python مدمج (لو اتبنى بيه). تقدر تكتب Python inline بـ `python` أو ملف بـ `source file.py`. الـ `gdb` module بيديك access لكل حاجة: values, types, frames, breakpoints, events, pretty printers, new commands, TUI windows.

```gdb
python CODE                    # one line (py is alias)
python
import gdb
print(gdb.parse_and_eval("x"))
end                            # multi-line block
python-interactive / pi        # interactive Python REPL
pi EXPR                        # evaluate one expression
source script.py               # run a Python file (by .py extension)
set script-extension off|soft|strict   # how to decide language by extension
set python print-stack none|message|full
set python ignore-environment on|off
set python dont-write-bytecode auto|on|off
show python ...
```

### 24.4 Python — API Quick Reference

```python
import gdb

# --- basic ---
gdb.execute("bt", to_string=True)     # run a CLI command, get output
gdb.parse_and_eval("x + 1")           # -> gdb.Value
gdb.parameter("print elements")       # read a setting
gdb.set_parameter("print elements", 10)
gdb.set_convenience_variable("foo", 5) / gdb.convenience_variable("foo")
gdb.history(0)                        # value history $
gdb.add_history(value)
gdb.history_count()
gdb.write("text\n"), gdb.flush()
gdb.lookup_type("struct foo")  / gdb.lookup_type("int").pointer()
gdb.lookup_symbol("main")      / gdb.lookup_global_symbol("g") / gdb.lookup_static_symbol
gdb.lookup_objfile("libc.so.6")
gdb.current_progspace(), gdb.progspaces(), gdb.objfiles()
gdb.selected_inferior(), gdb.inferiors()
gdb.selected_thread(), gdb.selected_frame(), gdb.newest_frame()
gdb.breakpoints()
gdb.decode_line("file.c:42")
gdb.find_pc_line(pc)                  # -> Symtab_and_line
gdb.block_for_pc(pc)
gdb.current_language(), gdb.architecture_names()
gdb.solib_name(addr)
gdb.string_to_argv("a 'b c'")
gdb.post_event(callable)              # run in GDB's main thread (thread-safe)
gdb.prompt_hook = lambda cur: "> "
gdb.STDOUT, gdb.STDERR, gdb.STDLOG
gdb.PYTHONDIR, gdb.VERSION, gdb.HOST_CONFIG, gdb.TARGET_CONFIG
gdb.interrupt()                       # like Ctrl-C
gdb.notify_mi("name", data)           # custom MI async notification
gdb.format_address(addr), gdb.current_recording()
gdb.rl_hooks / gdb.execute_mi("-data-evaluate-expression", "x")

# --- exceptions ---
try: ...
except gdb.error: ...                 # generic GDB error
except gdb.MemoryError: ...
except gdb.GdbError: ...              # raise this in commands: no traceback shown
except KeyboardInterrupt: ...

# --- Value ---
v = gdb.parse_and_eval("ptr")
v.type, v.address, v.is_optimized_out, v.is_lazy, v.dynamic_type
v.dereference(), v.referenced_value(), v.reference_value(), v.const_value()
v.cast(t), v.dynamic_cast(t), v.reinterpret_cast(t)
v["field"], v[0], int(v), float(v), str(v), bool(v)
v.string(encoding="utf-8", length=10), v.lazy_string(), v.format_string(format='x', pretty_structs=True)
v.fetch_lazy(), v.to_array(), v.assign(newval), v.bytes
gdb.Value(5), gdb.Value(b"\x00\x01", gdb.lookup_type("short"))
gdb.Value.__init__(obj)               # Python int/float/str/bool -> Value

# --- Type ---
t = gdb.lookup_type("struct foo")
t.name, t.tag, t.code, t.sizeof, t.alignof, t.dynamic, t.objfile, t.is_scalar, t.is_signed, t.is_array_like, t.is_string_like
t.fields()  -> field.name, .type, .bitpos, .bitsize, .enumval, .artificial, .is_base_class, .parent_type
t.keys(), t.values(), t.items(), t["field"], "field" in t, len(t)
t.strip_typedefs(), t.target(), t.pointer(), t.reference(), t.rvalue_reference()
t.array(n), t.array(lo, hi), t.vector(n), t.const(), t.volatile(), t.unqualified()
t.range(), t.template_argument(n)
gdb.TYPE_CODE_PTR, TYPE_CODE_ARRAY, TYPE_CODE_STRUCT, TYPE_CODE_UNION, TYPE_CODE_ENUM,
TYPE_CODE_FLAGS, TYPE_CODE_FUNC, TYPE_CODE_INT, TYPE_CODE_FLT, TYPE_CODE_VOID, TYPE_CODE_RANGE,
TYPE_CODE_STRING, TYPE_CODE_BITSTRING, TYPE_CODE_ERROR, TYPE_CODE_METHOD, TYPE_CODE_METHODPTR,
TYPE_CODE_MEMBERPTR, TYPE_CODE_REF, TYPE_CODE_RVALUE_REF, TYPE_CODE_CHAR, TYPE_CODE_BOOL,
TYPE_CODE_COMPLEX, TYPE_CODE_TYPEDEF, TYPE_CODE_NAMESPACE, TYPE_CODE_DECFLOAT, TYPE_CODE_INTERNAL_FUNCTION, TYPE_CODE_XMETHOD, TYPE_CODE_FIXED_POINT, TYPE_CODE_NAMELIST
gdb.types.get_basic_type(t), gdb.types.has_field(t, "x"), gdb.types.make_enum_dict(t), gdb.types.deep_items(t)
gdb.types.get_type_recognizers(), gdb.types.apply_type_recognizers(), gdb.types.register_type_printer()

# --- Pretty printer ---
class FooPrinter:
    def __init__(self, val): self.val = val
    def to_string(self): return "foo(%d)" % int(self.val["x"])
    def children(self): yield "x", self.val["x"]     # optional
    def display_hint(self): return "string" | "array" | "map" | None
    def num_children(self): ...       # optional, for MI
    def child(self, n): ...           # optional
import gdb.printing
pp = gdb.printing.RegexpCollectionPrettyPrinter("mylib")
pp.add_printer("foo", "^foo$", FooPrinter)
gdb.printing.register_pretty_printer(gdb.current_objfile(), pp)   # or None for global
# or simple:  gdb.pretty_printers.append(lookup_function)
gdb.default_visualizer(value)

# --- Type printer ---
class MyTypePrinter: name, enabled, instantiate() -> recognizer.recognize(type) -> str|None
gdb.type_printers.append(...)  / gdb.types.register_type_printer(objfile, printer)

# --- Frame filters / decorators ---
class MyFilter:  name, priority, enabled, filter(frame_iter) -> iterator of FrameDecorator
from gdb.FrameDecorator import FrameDecorator    # function(), address(), filename(), line(), frame_args(), frame_locals(), elided(), inferior_frame()
from gdb.FrameIterator import FrameIterator
gdb.frame_filters["name"] = MyFilter()           # or progspace.frame_filters / objfile.frame_filters

# --- Unwinders ---
from gdb.unwinder import Unwinder, register_unwinder
class MyUnwinder(Unwinder):
    def __call__(self, pending_frame):           # pending_frame.read_register(), .create_unwind_info(frame_id), .architecture(), .level(), .pc(), .language(), .find_sal(), .block(), .function()
        ...
        unwind_info.add_saved_register("rip", val)
register_unwinder(locus, unwinder, replace=False)   # locus: None / objfile / progspace
gdb.FrameId(sp, pc)

# --- Xmethods (replace C++ methods with Python) ---
from gdb.xmethod import XMethod, XMethodMatcher, XMethodWorker, register_xmethod_matcher
# matcher.match(class_type, method_name) -> workers; worker.get_arg_types(), get_result_type(), __call__()

# --- Inferior / Thread ---
inf = gdb.selected_inferior()
inf.num, inf.pid, inf.was_attached, inf.progspace, inf.connection, inf.connection_num, inf.main_name
inf.threads(), inf.architecture(), inf.is_valid()
inf.read_memory(addr, len) -> memoryview ; inf.write_memory(addr, buf) ; inf.search_memory(addr, len, pattern)
inf.thread_from_handle(h), inf.arguments, inf.clear_env(), inf.set_env(k,v), inf.unset_env(k), inf.environment
th = gdb.selected_thread()
th.name, th.num, th.global_num, th.ptid, th.inferior, th.details, th.is_valid()
th.switch(), th.is_stopped(), th.is_running(), th.is_exited(), th.handle()
gdb.InferiorThread.ptid_string
# Recordings: gdb.start_recording(method, format), gdb.current_recording(), gdb.stop_recording()
#   rec.method, rec.format, rec.begin, rec.end, rec.replay_position, rec.instruction_history, rec.function_call_history, rec.goto(insn)

# --- Events ---
gdb.events.stop.connect(handler)      # handler(event): event.inferior_thread; BreakpointEvent.breakpoints / SignalEvent.stop_signal
gdb.events.cont / exited (event.exit_code, .inferior) / new_objfile (event.new_objfile) / free_objfile / clear_objfiles
gdb.events.new_inferior / inferior_deleted / new_thread / thread_exited / inferior_call (pre/post) / memory_changed / register_changed
gdb.events.breakpoint_created / breakpoint_modified / breakpoint_deleted / before_prompt / gdb_exiting / connection_removed / executable_changed / new_progspace / free_progspace / tui_enabled
gdb.events.stop.disconnect(handler)

# --- Commands ---
class Hello(gdb.Command):
    """Say hello.  Usage: hello NAME"""      # docstring = help text
    def __init__(self):
        super().__init__("hello", gdb.COMMAND_USER)   # COMMAND_NONE/RUNNING/DATA/STACK/FILES/SUPPORT/STATUS/BREAKPOINTS/TRACEPOINTS/OBSCURE/MAINTENANCE/TUI/USER
    def invoke(self, arg, from_tty):
        argv = gdb.string_to_argv(arg)
        gdb.write("hello %s\n" % argv[0])
    def complete(self, text, word): return gdb.COMPLETE_SYMBOL   # or COMPLETE_NONE/FILENAME/LOCATION/COMMAND/EXPRESSION or a list
    def dont_repeat(self): ...
Hello()
# prefix command: gdb.Command.__init__(self, "myprefix", gdb.COMMAND_USER, prefix=True)

# --- MI commands in Python ---
class MyMI(gdb.MICommand):
    def __init__(self): super().__init__("-my-command")
    def invoke(self, argv): return {"result": "ok"}   # dict/list/str -> MI output
MyMI()

# --- Parameters (set/show) ---
class MyParam(gdb.Parameter):
    """Doc"""
    set_doc = "Set the thing"; show_doc = "Show the thing"
    def __init__(self): super().__init__("my-thing", gdb.COMMAND_DATA, gdb.PARAM_BOOLEAN)   # PARAM_INTEGER/UINTEGER/ZINTEGER/ZUINTEGER/ZUINTEGER_UNLIMITED/STRING/STRING_NOESCAPE/OPTIONAL_FILENAME/FILENAME/ENUM/AUTO_BOOLEAN/COLOR
    def get_set_string(self): return ""
    def get_show_string(self, svalue): return "value is " + svalue
MyParam()   # then: set my-thing on / show my-thing / gdb.parameter("my-thing")

# --- Convenience functions ---
class Greet(gdb.Function):
    def __init__(self): super().__init__("greet")
    def invoke(self, name): return "Hi " + name.string()
Greet()   # then: p $greet("bob")

# --- Progspace / Objfile ---
ps = gdb.current_progspace(); ps.filename, ps.executable_filename, ps.symbol_file, ps.objfiles(), ps.solib_name(addr), ps.block_for_pc(pc), ps.find_pc_line(pc), ps.is_valid(), ps.objfile_for_address(addr), ps.pretty_printers, ps.type_printers, ps.frame_filters, ps.frame_unwinders, ps.missing_debug_handlers
o = gdb.lookup_objfile("prog"); o.filename, o.username, o.owner, o.build_id, o.progspace, o.is_file, o.is_valid(), o.add_separate_debug_file(f), o.lookup_global_symbol(n), o.lookup_static_symbol(n), o.pretty_printers, o.type_printers, o.frame_filters, o.frame_unwinders, o.xmethods
gdb.current_objfile()   # only during auto-load

# --- Frames ---
f = gdb.selected_frame()
f.name(), f.pc(), f.is_valid(), f.type(), f.unwind_stop_reason(), f.architecture(), f.language(), f.level()
f.block(), f.function(), f.older(), f.newer(), f.find_sal(), f.read_register("rip"), f.read_var("x"), f.select(), f.static_link()
gdb.frame_stop_reason_string(reason)
gdb.NORMAL_FRAME, DUMMY_FRAME, INLINE_FRAME, TAILCALL_FRAME, SIGTRAMP_FRAME, ARCH_FRAME, SENTINEL_FRAME
gdb.FRAME_UNWIND_NO_REASON, NULL_ID, OUTERMOST, UNAVAILABLE, INNER_ID, SAME_ID, NO_SAVED_PC, MEMORY_ERROR
gdb.invalidate_cached_frames()

# --- Blocks / Symbols / Symtabs ---
b = gdb.block_for_pc(pc); b.start, b.end, b.function, b.superblock, b.global_block, b.static_block, b.is_global, b.is_static, b.is_valid(); for sym in b: ...
s = gdb.lookup_symbol("x")[0]; s.name, s.linkage_name, s.print_name, s.type, s.symtab, s.line, s.addr_class, s.needs_frame, s.is_argument, s.is_constant, s.is_function, s.is_variable, s.is_artificial, s.value(frame), s.is_valid()
gdb.SYMBOL_LOC_UNDEF/CONST/STATIC/REGISTER/ARG/REF_ARG/LOCAL/TYPEDEF/LABEL/BLOCK/CONST_BYTES/UNRESOLVED/OPTIMIZED_OUT/COMPUTED/REGPARM_ADDR/COMMON_BLOCK
gdb.SYMBOL_VAR_DOMAIN, STRUCT_DOMAIN, LABEL_DOMAIN, MODULE_DOMAIN, COMMON_BLOCK_DOMAIN, ...
gdb.lookup_static_symbols("x")
sal = gdb.find_pc_line(pc); sal.pc, sal.last, sal.line, sal.symtab, sal.is_valid()
st = sal.symtab; st.filename, st.objfile, st.producer, st.fullname(), st.global_block(), st.static_block(), st.linetable()
lt = st.linetable(); lt.line(n), lt.has_line(n), lt.source_lines(); for e in lt: e.line, e.pc

# --- Breakpoints ---
bp = gdb.Breakpoint("main")            # gdb.Breakpoint(spec, type=BP_BREAKPOINT, wp_class=WP_WRITE, internal=False, temporary=False, qualified=False)
gdb.Breakpoint(source="f.c", line=10, function=None, label=None)
gdb.Breakpoint("x", gdb.BP_WATCHPOINT, gdb.WP_READ)   # BP_BREAKPOINT/HARDWARE_BREAKPOINT/WATCHPOINT/HARDWARE_WATCHPOINT/READ_WATCHPOINT/ACCESS_WATCHPOINT/CATCHPOINT; WP_READ/WRITE/ACCESS
bp.enabled, bp.silent, bp.pending, bp.thread, bp.inferior, bp.task, bp.ignore_count, bp.number, bp.type, bp.visible, bp.temporary, bp.hit_count, bp.location, bp.locations, bp.expression, bp.condition, bp.commands
bp.is_valid(), bp.delete()
class MyBP(gdb.Breakpoint):
    def stop(self): return int(gdb.parse_and_eval("x")) > 5   # True = stop, False = continue
# bp.locations -> gdb.BreakpointLocation: address, enabled, fullname, function, source, thread_groups, owner
class MyFinish(gdb.FinishBreakpoint):   # gdb.FinishBreakpoint(frame, internal=False); .return_value; stop(), out_of_scope()
    ...

# --- Lazy strings / Colors / Styles ---
ls = v.lazy_string(); ls.address, ls.length, ls.encoding, ls.type, ls.value()
gdb.Color("red"), gdb.Color(5), gdb.Color((255,0,0)); c.is_none, c.is_direct, c.is_indexed, c.colorspace, c.index, c.components, c.escape_sequence(is_foreground)
gdb.Style(...)  # style objects for styled output (newer API)

# --- Architecture / Registers / Disassembly ---
arch = gdb.selected_frame().architecture() ; arch.name(), arch.disassemble(start, end=None, count=None) -> [{addr, asm, length}]
arch.registers(reggroup=None) -> RegisterDescriptor(name) ; arch.register_groups() -> RegisterGroup(name)
arch.integer_type(size, signed=True), arch.void_type()
from gdb.disassembler import Disassembler, DisassembleInfo, DisassemblerResult, register_disassembler, builtin_disassemble, DisassemblerTextPart, DisassemblerAddressPart, syntax_highlight

# --- Connections ---
c = inf.connection ; c.num, c.type, c.description, c.details, c.is_valid() ; gdb.RemoteTargetConnection.send_packet(b"...")
gdb.connections()

# --- TUI windows ---
class MyWin:                            # constructed with (tui_window): .width .height .title .is_valid() .erase() .write(str, full_window=False) .click? 
    def __init__(self, tw): self.tw = tw; tw.title = "My"
    def render(self): self.tw.write("hello")
    def hscroll(self, n): ... ; def vscroll(self, n): ... ; def click(self, x, y, button): ... ; def close(self): ...
gdb.register_window_type("mywin", MyWin)
# then: tui new-layout my mywin 1 cmd 1 ; layout my

# --- Missing debug info / objfiles handlers ---
from gdb.missing_debug import MissingDebugHandler ; gdb.missing_debug.register_handler(locus, handler)  # handler(objfile) -> None|False|True|str
from gdb.missing_objfile import MissingObjfileHandler ; gdb.missing_objfile.register_handler(...)
# CLI: info missing-debug-handlers / enable|disable missing-debug-handler LOCUS NAME ; info missing-objfile-handlers ...

# --- Core files ---
gdb.selected_inferior().corefile ; inf.corefile.filename, .mapped_files(), .build_id() ...  # newer API
# --- gdb.prompt ---  substitute_prompt("\\f \\p{prompt} \\w \\v \\e[1m")  ; gdb.prompt.prompt_help()
# --- gdb.ptwrite ---  gdb.ptwrite.register_filter_factory(f), gdb.ptwrite.get_filter()
```

### 24.5 Python Auto-loading

**بالعامية:** لما GDB يحمّل `prog` أو `libfoo.so`، بيدوّر أوتوماتيك على `prog-gdb.py` في نفس المكان أو في `auto-load scripts-directory`، أو على `.debug_gdb_scripts` section جوه الملف.

```text
Looked-up names for OBJFILE = /path/libfoo.so:
  /path/libfoo.so-gdb.py         (also -gdb.gdb, -gdb.scm)
  $datadir/auto-load/path/libfoo.so-gdb.py
  $debugdir/path/libfoo.so-gdb.py
.debug_gdb_scripts section entries:
  SECTION_SCRIPT_ID_PYTHON_FILE (1) "file.py"
  SECTION_SCRIPT_ID_PYTHON_TEXT (4) "name\n<script text>"
```

```gdb
info auto-load python-scripts [REGEX]
set auto-load python-scripts off
```

### 24.6 Guile

**بالعامية:** نفس فكرة Python بس بلغة Scheme (Guile). الـ API شبه Python: values, types, frames, breakpoints, pretty printers, commands, parameters. Python بيتحمّل الأول لو الاتنين موجودين.

```gdb
guile CODE / gu CODE           # one line
guile
  (use-modules (gdb))
  (display (value->integer (parse-and-eval "x")))
end
guile-repl / gr                # interactive REPL
source script.scm
set guile print-stack none|message|full
info auto-load guile-scripts
```

```scheme
(use-modules (gdb) (gdb printing) (gdb types))
(execute "bt" #:to-string #t)
(parse-and-eval "x")  (value->integer v) (value->string v) (value-type v) (value-field v "f") (value-dereference v) (value-cast v t)
(lookup-type "int") (type-sizeof t) (type-fields t) (type-pointer t) (type-strip-typedefs t)
(selected-frame) (frame-name f) (frame-pc f) (frame-read-var f "x") (frame-older f) (frame-newer f)
(make-breakpoint "main" #:type BP_BREAKPOINT) (register-breakpoint! bp) (breakpoint-enabled? bp) (set-breakpoint-stop! bp proc)
(make-command "hello" #:command-class COMMAND_USER #:invoke (lambda (self arg from-tty) ...)) (register-command! cmd)
(make-parameter "my-p" #:command-class COMMAND_DATA #:parameter-type PARAM_BOOLEAN ...) (register-parameter! p)
(make-pretty-printer "foo" (lambda (val) ...)) (append-pretty-printer! #f pp)
(current-progspace) (objfiles) (objfile-filename o) (current-objfile)
(lookup-symbol "x") (symbol-name s) (symbol-type s) (block-for-pc pc)
(arch-name (current-arch)) (arch-disassemble arch pc #:count 5)
(open-memory #:start addr #:size n)   ; memory ports
(make-iterator ...) (iterator-map ...) (iterator-filter ...)   ; iterators
(make-color "red") (color-escape-sequence c #t)
(throw-user-error "msg") (catch 'gdb:error ...)
```

### 24.7 Auto-loading Extensions Summary

```text
OBJFILE-gdb.gdb   -> CLI script     (set auto-load gdb-scripts)
OBJFILE-gdb.py    -> Python         (set auto-load python-scripts)
OBJFILE-gdb.scm   -> Guile          (set auto-load guile-scripts)
.debug_gdb_scripts section: 1=python file, 3=guile file, 4=python text, 6=guile text
Multiple languages: Python is tried first for printers/filters/etc.
```

---

## 25. Interpreters, TUI, Emacs

### 25.1 Command Interpreters

```gdb
interpreter-exec mi "-data-list-register-names"   # run one MI command from CLI
interpreter-exec console "bt"   # run CLI command from MI
gdb -i=mi / gdb --interpreter=mi3 / mi2 / mi1 / console / dap
# "-interpreter-exec console ..." from MI side
new-ui INTERP TTY               # new-ui mi /dev/pts/5 : extra UI on another terminal
```

### 25.2 TUI (Text User Interface)

**بالعامية:** TUI بيقسّم الـ terminal لـ windows: source, assembly, registers, command. `Ctrl-x a` بيفتحه/يقفله. `layout` بيغيّر الترتيب. `focus` بيحدد أنهي window بتاخد الأسهم. `tui new-layout` بتعمل layout بتاعك. `Ctrl-x s` = SingleKey mode (حرف واحد لكل أمر).

```gdb
tui enable / tui disable       # turn TUI on/off
Ctrl-x a                       # toggle TUI (also Ctrl-x A)
Ctrl-x 1                       # one window layout
Ctrl-x 2                       # two windows (cycle: src/asm/regs)
Ctrl-x o                       # change focus to next window
Ctrl-x s                       # toggle SingleKey mode
Ctrl-L                         # refresh screen
PgUp / PgDn / Up / Down / Left / Right   # scroll focused window
Ctrl-p / Ctrl-n / Ctrl-b / Ctrl-f        # command history / cursor (when cmd has focus)

layout src                     # source + command
layout asm                     # assembly + command
layout split                   # source + assembly + command
layout regs                    # registers + (source or asm) + command ⭐
layout next / layout prev
layout NAME                    # user layout
tui new-layout NAME WINDOW WEIGHT [WINDOW WEIGHT]...   # e.g. tui new-layout mine src 2 regs 1 status 0 cmd 1
tui new-layout h {-horizontal src 1 asm 1} 2 status 0 cmd 1
tui layout NAME                # same as layout
info win                       # list windows
focus src|asm|regs|cmd|status|next|prev / fs
tui focus NAME
refresh
update                         # update source window to current line
winheight NAME +N / -N / N     # wh src +5
tui window height NAME N
winwidth NAME +N / tui window width NAME N
tui reg GROUP                  # registers window group: general, float, vector, system, all, next, prev
tui reg general
tabset N                       # tab width
set tui border-kind space|ascii|acs
set tui border-mode / active-border-mode normal|standout|reverse|half|half-standout|bold|bold-standout
set tui tab-width N
set tui compact-source on|off
set tui mouse-events on|off
set tui left-margin-verbose on|off
set style tui-current-position on
show tui ...

# SingleKey mode keys (Ctrl-x s):
# c continue, d down, f finish, n next, o nexti, r run, s step, i stepi, u up, v info locals, w where, q exit SingleKey
```

### 25.3 Emacs

```text
M-x gdb                        # start GDB inside Emacs (gdb-mi mode)
M-x gud-gdb                    # older text mode
C-c C-s  step    C-c C-n  next    C-c C-i  stepi   C-c C-r  continue
C-c C-f  finish  C-c <    up      C-c >    down    C-c C-l  refresh source
C-x SPC  set breakpoint at point (in a source buffer)
C-c C-d  delete breakpoint     C-c C-t  temp breakpoint
```

---

## 26. GDB/MI, DAP, Annotations, JIT, In-Process Agent

### 26.1 GDB/MI (Machine Interface)

**بالعامية:** MI هي الـ protocol اللي الـ IDEs (VS Code, Eclipse, CLion) بتكلّم بيها GDB. كل أمر بيبدأ بـ `-` وممكن يكون له token رقمي في الأول. الـ output بيبقى `^done`, `^error`, `*stopped`, `=breakpoint-created`, `~"console text"`... إلخ.

```text
Input:   [TOKEN]-command [args]      e.g.  123-break-insert main
Output:  TOKEN^done[,results]   ^running   ^connected   ^error,msg="..."   ^exit
         *running,thread-id="all"    *stopped,reason="breakpoint-hit",...
         =thread-created  =thread-exited  =library-loaded  =breakpoint-created/modified/deleted
         =thread-group-added/started/exited  =record-started  =cmd-param-changed  =memory-changed
         ~"console stream"   @"target stream"   &"log stream"
         (gdb)     <- prompt terminates each output block
Stop reasons: breakpoint-hit, watchpoint-trigger, read-watchpoint-trigger, access-watchpoint-trigger,
  function-finished, location-reached, watchpoint-scope, end-stepping-range, exited-signalled,
  exited, exited-normally, signal-received, solib-event, fork, vfork, syscall-entry, syscall-return, exec, no-history
```

```text
# Breakpoints
-break-insert [-t] [-h] [-f] [-d] [-a] [-c COND] [-i COUNT] [-p THREAD] [--qualified] [--source F --line N --function F --label L] [LOCATION]
-break-after N COUNT  -break-condition [--force] N EXPR  -break-commands N "cmd"...
-break-delete N  -break-disable N  -break-enable N  -break-info N  -break-list
-break-passcount TP COUNT  -break-watch [-a|-r] EXPR
-dprintf-insert [opts] LOCATION FORMAT ARGS
-catch-load [-t] [-d] REGEX  -catch-unload  -catch-assert  -catch-exception  -catch-handlers  -catch-throw  -catch-catch  -catch-rethrow
# Program context
-exec-arguments ARGS  -environment-cd DIR  -environment-directory  -environment-path  -environment-pwd
-inferior-tty-set TTY  -inferior-tty-show
# Threads / inferiors
-thread-info [ID]  -thread-list-ids  -thread-select ID
-list-thread-groups [--available] [--recurse 1] [GROUP]
-add-inferior [--no-connection]  -remove-inferior ID
# Ada tasks
-ada-task-info [ID]
# Execution
-exec-run [--all|--thread-group N] [--start]  -exec-continue [--reverse] [--all|--thread-group N]
-exec-next [--reverse]  -exec-next-instruction  -exec-step  -exec-step-instruction  -exec-finish [--reverse]
-exec-until [LOC]  -exec-jump LOC  -exec-return  -exec-interrupt [--all|--thread-group N]  -exec-abort
# Stack
-stack-info-frame  -stack-info-depth [MAX]  -stack-list-frames [--no-frame-filters] [LOW HIGH]
-stack-list-arguments [--no-frame-filters] [--skip-unavailable] PRINT-VALUES [LOW HIGH]
-stack-list-locals [--no-frame-filters] [--skip-unavailable] PRINT-VALUES
-stack-list-variables ...  -stack-select-frame N
-enable-frame-filters
# Variable objects
-var-create NAME|"-" FRAME|"*"|"@" EXPR  -var-delete [-c] NAME  -var-set-format NAME FMT  -var-show-format NAME
-var-info-num-children  -var-list-children [PRINT-VALUES] NAME [FROM TO]  -var-info-type  -var-info-expression  -var-info-path-expression
-var-show-attributes  -var-evaluate-expression [-f FMT] NAME  -var-assign NAME EXPR  -var-update [PRINT-VALUES] NAME|*
-var-set-frozen NAME 0|1  -var-set-update-range NAME FROM TO  -var-set-visualizer NAME VIS
-enable-pretty-printing
# Data
-data-disassemble [-s START -e END | -a ADDR | -f FILE -l LINE [-n LINES]] [--opcodes bytes|display|none] [--source] -- MODE(0-5)
-data-evaluate-expression EXPR  -data-list-changed-registers  -data-list-register-names [N...]
-data-list-register-values [--skip-unavailable] FMT [N...]  -data-read-memory-bytes [-o OFFSET] ADDR COUNT
-data-write-memory-bytes ADDR CONTENTS [COUNT]  -data-read-memory (deprecated)  -data-write-memory (deprecated)
# Tracepoints
-trace-find MODE ...  -trace-define-variable NAME [VALUE]  -trace-frame-collected [...]  -trace-list-variables
-trace-save [-r] [-ctf] FILE  -trace-start  -trace-status  -trace-stop
# Symbols
-symbol-info-functions [--include-nondebug] [--type R] [--name R] [--max-results N]  -symbol-info-module-functions  -symbol-info-module-variables
-symbol-info-modules  -symbol-info-types  -symbol-info-variables  -symbol-list-lines FILE
# Files
-file-exec-and-symbols FILE  -file-exec-file FILE  -file-list-exec-source-file  -file-list-exec-source-files [--group-by-objfile] [--dirname|--basename] [--] [REGEX]
-file-list-shared-libraries [REGEX]  -file-symbol-file FILE
# Target
-target-attach PID|FILE  -target-detach [ID]  -target-disconnect  -target-download  -target-flash-erase  -target-select TYPE PARAMS
-target-file-put HOST TARGET  -target-file-get TARGET HOST  -target-file-delete TARGET
# Support / misc
-info-gdb-mi-command NAME  -list-features  -list-target-features  -gdb-exit  -gdb-set  -gdb-show  -gdb-version
-list-features  -info-ada-exceptions [REGEX]  -info-os [TYPE]  -inferior-tty-set  -interpreter-exec INTERP CMD
-complete "text"  -fix-multi-location-breakpoint-output  -fix-breakpoint-script-output
```

### 26.2 Debugger Adapter Protocol (DAP)

**بالعامية:** DAP هو protocol موحّد (بتاع VS Code) — GDB بيدعمه بـ `gdb -i=dap` (محتاج Python). الـ IDE بيبعت JSON requests و GDB بيرد.

```bash
gdb -i=dap                     # start GDB as a DAP server (stdin/stdout)
```

```gdb
set debug dap-log-file FILE    # log DAP traffic
set debug dap-log-level 1
# launch request extra params: "program", "args", "env", "cwd", "stopAtBeginningOfMainSubprogram", "stopOnEntry"
# attach: "pid" or "target" (remote)
```

### 26.3 Annotations (legacy)

```gdb
set annotate LEVEL             # 0 none, 1 Emacs, 2 deprecated, 3 max
# output like: ^Z^Zbreakpoint 1 ... ^Z^Zsource file:line:char:beg:addr
# "server " prefix on a command = do not affect history / repeat
server break main
```

### 26.4 JIT Compilation Interface

**بالعامية:** لو عندك JIT (زي LLVM) بيولّد كود في الـ runtime، البرنامج بيسجّل الـ object files عند GDB عن طريق `__jit_debug_descriptor` و `__jit_debug_register_code()` عشان GDB يعرف الـ symbols. تقدر تكتب reader بتاعك لـ custom debug info.

```gdb
maint info jit                 # list JIT-registered objects
jit-reader-load FILE.so        # load a custom JIT debug-info reader
jit-reader-unload
set debug jit 1
```

```c
/* program side */
struct jit_code_entry { next_entry, prev_entry, symfile_addr, symfile_size };
struct jit_descriptor  { version=1, action_flag (JIT_NOACTION/JIT_REGISTER_FN/JIT_UNREGISTER_FN), relevant_entry, first_entry };
extern struct jit_descriptor __jit_debug_descriptor;
void __attribute__((noinline)) __jit_debug_register_code(void) { asm(""); }
```

### 26.5 In-Process Agent (IPA)

**بالعامية:** الـ IPA library (`libinproctrace.so`) بتتحمّل جوه البرنامج عشان تدعم fast tracepoints و static tracepoints مع gdbserver.

```bash
LD_PRELOAD=libinproctrace.so ./prog     # load the agent
gdbserver :2345 ./prog
```

```gdb
set agent on|off               # use the in-process agent when possible
show agent
ftrace LOCATION                # fast tracepoints need IPA
```

---

## 27. Command Line Editing & History

**بالعامية:** GDB بيستخدم Readline (زي bash). كل shortcuts الـ Emacs موجودة. تقدر تعمل `~/.inputrc` وتحط فيه `$if Gdb` لإعدادات خاصة بـ GDB. `set editing off` بيطفّي الـ editing، وفيه vi mode.

```text
# Movement          # Editing                   # History
C-a  line start     C-d  delete char            C-p / Up      previous command
C-e  line end       DEL  backspace              C-n / Down    next command
C-f  forward char   C-k  kill to end            C-r           reverse search
C-b  back char      C-u  kill to start          C-s           forward search
M-f  forward word   C-w  kill word back         M-<  / M->    first / last
M-b  back word      M-d  kill word forward      C-o           accept & get next
C-l  clear screen   C-y  yank (paste)           !!  !N  !-N  !string  !?string   history expansion (set history expansion on)
                    M-y  yank previous kill     !$  !^  !*  !:N   word designators
                    C-_  undo                   ^old^new^         quick substitution
                    C-t  transpose chars        :h :t :r :e :p :s/a/b/ :g   modifiers
                    M-u / M-l / M-c  upper/lower/capitalize word
                    TAB  complete   M-?  list completions   M-*  insert all completions
                    C-q / C-v  quoted insert    M-r  revert line
```

```text
# ~/.inputrc
$if Gdb
    set editing-mode vi
    "\C-xb": "break main\n"
$endif
set show-all-if-ambiguous on
set completion-ignore-case on
```

---

## 28. Maintenance Commands & Bug Reports

**بالعامية:** أوامر `maint` للي بيطوّروا GDB نفسه أو بيعملوا debugging عميق. الأكثر فائدة: `maint info sections`, `maint info breakpoints`, `maint print registers`, `maint time`, `maint set dwarf ...`.

```gdb
maint info sections [-all-objects] [FILTERS]   # ELF sections & addresses (ALLOC LOAD CODE DATA ...)
maint info target-sections
maint info breakpoints         # incl. internal (negative numbers)
maint info bfds
maint info line-table [REGEX]
maint info symtabs / psymtabs [REGEX]
maint info program-spaces
maint info sol-threads
maint info jit
maint info frame-unwinders
maint info selftests / maint selftest [-verbose] [FILTER]
maint print registers / raw-registers / cooked-registers / register-groups / remote-registers [FILE]
maint print reggroups
maint print architecture [FILE]
maint print c-tdesc [FILE] / maint print xml-tdesc [FILE]
maint print dummy-frames
maint print objfiles [REGEX]
maint print symbols / psymbols / msymbols [-pc ADDR | -objfile OBJ | -source SRC] [--] [OUTFILE]
maint print statistics
maint print target-stack
maint print type EXPR
maint print unwind ADDR
maint print user-registers
maint print core-file-backed-mappings
maint print remote-registers
maint print frame-id [LEVEL]
maint print symbol-cache / symbol-cache-statistics
maint print xml-tdesc
maint expand-symtabs [REGEX]
maint flush symbol-cache / register-cache / dcache / source-cache / bfd-cache
maint cplus first_component NAME / maint cplus namespace
maint demangler-warning / maint deprecate COMMAND [REPLACEMENT] / maint undeprecate COMMAND
maint dump-me / maint internal-error [MSG] / maint internal-warning / maint demangler-warning
maint packet TEXT              # send raw packet to remote target
maint set dwarf always-disassemble on|off
maint set dwarf max-cache-age N
maint set dwarf unwinders on|off
maint set catch-demangler-crashes on|off
maint set profile on|off       # GDB profiling
maint set show-debug-regs on|off
maint set show-all-tib on|off
maint set target-async on|off
maint set target-non-stop on|off|auto
maint set per-command time|space|symtab on|off   # stats after every command
maint set worker-threads N|unlimited
maint set internal-error quit|corefile ask|yes|no
maint set bfd-sharing on|off
maint set check-libthread-db on|off
maint set ignore-prologue-end-flag on|off
maint set gnu-source-highlight enabled on|off
maint set backtrace-on-fatal-signal on|off
maint set test-settings TYPE VALUE
maint set tui-resize-message on|off
maint set tui-left-margin-verbose ...
maint set libopcodes-styling enabled on|off
maint time 0|1                 # (old) time each command
maint space 0|1
maint translate-address [SECTION] ADDR
maint agent EXPR / maint agent-eval EXPR / maint agent-printf FMT, ARGS   # show agent bytecode
maint check-psymtabs / maint check-symtabs / maint check xml-descriptions DIR
maint btrace packet-history / clear-packet-history / clear
maint with SETTING [VALUE] [-- CMD]
maint canonicalize NAME
maint test-options require-delimiter ... / unknown-is-error ... / unknown-is-operand ...
maint show ...                 # any of the maint settings
```

```gdb
# --- reporting bugs (include these) ---
show version
show configuration
gdb -batch -ex "show version"
# report at https://sourceware.org/bugzilla/ (component gdb) or bug-gdb@gnu.org
# include: exact input, exact output, "set verbose on", a minimal reproducer
```

```bash
# --- building GDB ---
./configure --prefix=/opt/gdb --with-python --enable-tui --with-guile --with-debuginfod \
            --target=arm-none-eabi          # cross debugger
make -j$(nproc) && make install
./configure --with-system-gdbinit=/etc/gdbinit --with-system-gdbinit-dir=/etc/gdbinit.d
```

---

## 29. Convenience Variables & Functions (Full List)

**بالعامية:** دي كل الـ `$`-variables اللي GDB بيوفّرها جاهزة. `show convenience` بيوريهم.

```text
$_                    last address examined by x / info line / info breakpoints
$__                   contents of $_
$_exitcode            exit code of the program
$_exitsignal          signal that killed the program
$_exception           current C++ exception (at catch throw/catch)
$_ada_exception       Ada exception address
$_probe_argc / $_probe_arg0..$_probe_arg11   probe arguments
$_siginfo             extra signal info (struct)
$_tlb                 Windows Thread Information Block
$_inferior            current inferior number
$_thread              current thread number
$_gthread             current global thread number
$_inferior_thread_count  number of live threads in inferior
$_gdb_major / $_gdb_minor   GDB version numbers
$_shell_exitcode / $_shell_exitsignal
$_linker_namespace    (glibc dlmopen) namespace of current location
$_active_linker_namespaces
$bpnum                number of last breakpoint set
$_hit_bpnum / $_hit_locno   breakpoint / location just hit
$tpnum                number of last tracepoint set
$trace_frame / $tracepoint / $trace_line / $trace_file / $trace_func
$_sdata               static tracepoint data
$_ret                 (tracepoints) return value
$numfound             matches found by "find"
$pc $sp $fp $ps       standard registers
$_wave_id $_dispatch_pos $_dispatch_id $_queue_id $_agent_id   AMD GPU

Functions (help function):
$_as_string(V) $_caller_is(NAME[,N]) $_caller_matches(REGEX[,N]) $_any_caller_is $_any_caller_matches
$_cimag(Z) $_creal(Z) $_gdb_maint_setting(S) $_gdb_maint_setting_str(S) $_gdb_setting(S) $_gdb_setting_str(S)
$_isvoid(E) $_memeq(A,B,N) $_regex(S,R) $_shell(CMD) $_streq(A,B) $_strlen(S)
```

---

## 30. Abbreviation Table

**بالعامية:** جدول سريع لأشهر الاختصارات.

| Abbrev | Full | Abbrev | Full |
|---|---|---|---|
| `b` | break | `c` / `fg` | continue |
| `tb` | tbreak | `n` | next |
| `hb` | hbreak | `s` | step |
| `d` | delete | `ni` / `si` | nexti / stepi |
| `dis` | disable | `fin` | finish |
| `en` | enable | `u` | until |
| `r` | run | `j` | jump |
| `k` | kill | `rc` / `rs` / `rn` | reverse-continue/step/next |
| `bt` / `where` | backtrace | `f` | frame |
| `p` | print | `i` | info |
| `x` | examine memory | `i r` | info registers |
| `l` | list | `i b` | info breakpoints |
| `wa` | watch | `t` | thread |
| `disas` | disassemble | `sha` | sharedlibrary |
| `q` | quit | `h` | help |
| `py` | python | `pi` | python-interactive |
| `gu` | guile | `gr` | guile-repl |
| `fo` / `rev` | forward-search / reverse-search | `w` | with |
| `tp` / `tr` | trace | `tf` | tfind |
| `taas` / `tfaas` / `faas` | thread/frame apply all -s | `fs` | focus |
| `wh` | winheight | `RET` | repeat last command |

---

*Generated 2026-09-07 from the GDB 19 (git) manual. Commands marked with version-specific behavior may differ on older GDB releases; run `help CMD` inside your GDB to confirm.*
