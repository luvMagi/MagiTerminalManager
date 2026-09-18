# MagiTerminalManager

GUI generator for Windows Terminal workspaces and appearance.

## Why this exists

Windows Terminal ships a fairly complete settings UI, but it cannot edit the two things this
tool exists for:

| Not reachable from the settings UI | Lives in | Consequence |
|---|---|---|
| `actions[]` entries of type `wt` | `settings.json` | An entire workspace layout - every pane's directory and command - is one hand-written string |
| The custom new-tab menu structure | `newTabMenu[]` | Folders, separators and menu placement are hand-written, and must match an `actions[]` entry by `id` |

So "make a named workspace" has no graphical entry point at all. Rebuilding a four-pane,
two-tab workspace on a second machine takes about an hour, and most of that hour is spent on
failures that do not report themselves: a mistyped `id` makes the menu entry silently vanish,
and a layout built in the wrong order just comes out crooked.

MagiTerminalManager fills exactly that gap. It does not compete with the settings UI; it adds
the two pages that UI does not have.

## How it works

```
pick a tab template  ->  read the diagram (panes are numbered)  ->  fill in directory + command
                     ->  tick which artifacts you want  ->  review the diff  ->  write
```

A workspace is a list of tabs. Each tab picks one of six templates. There is no free-form
layout editor, and that is deliberate: six fixed `wt` sequences can each be verified once and
stay correct forever, whereas planning `move-focus` for an arbitrary pane tree is a geometry
problem that fails silently when it gets it wrong.

### The six tab templates

```
P1 left/right       P2 top/bottom     P3 three columns
+----+----+         +---------+       +---+---+---+
| 1  | 2  |         |    1    |       | 1 | 2 | 3 |
+----+----+         +---------+       +---+---+---+
                    |    2    |
                    +---------+

P4 three rows       P5 left + split   P6 grid of four
+---------+         +----+----+       +----+----+
|    1    |         |    | 2  |       | 1  | 2  |
+---------+         | 1  +----+       +----+----+
|    2    |         |    | 3  |       | 3  | 4  |
+---------+         +----+----+       +----+----+
|    3    |
+---------+
```

Pane numbers are in visual reading order. They are *not* creation order: P6 has to fill slots
1, 2, 4, 3, because `split-pane` always splits the focused pane, and a two-by-two grid needs
one focus move back to the left column. Mapping visual number to argv slot is the template's
job, so that nobody using the tool has to know this.

### Artifacts

All three are optional, ticked per workspace:

| Artifact | Where it goes | What it buys |
|---|---|---|
| `settings.json` entry | `actions[]` + `newTabMenu[]` | The workspace appears in Terminal's own dropdown. No extra process, no window flash |
| `.lnk` | Wherever you want it | Desktop, taskbar pin, system-wide hotkey. Points straight at `wt.exe`, so no intermediate shell |
| `.ps1` | Wherever you want it | A readable copy you can diff and carry to another machine |

## Status

**v0.1.0, in development. Nothing works yet.**

The current task is a mechanism spike: twelve Windows Terminal behaviours have to be measured
before the rest can be written against fact rather than inference. See `spike/README.md`.

## Design rules

These are the lines the implementation is not allowed to cross. The reasoning behind each one
is recorded in the author's private design notes; what matters here is the rule.

| # | Rule |
|---|---|
| 1 | **The workspace definition is the only source of truth.** Every artifact is build output. Nothing is ever read back, and there is no "edit the artifact and sync it back" |
| 2 | **One generator, many backends.** Definition to `wt` argv has exactly one implementation and it is a pure function - no I/O, no side effects. Backends only wrap its output |
| 3 | **`settings.json` is only ever upserted by `id`**, under the `User.MagiTerm.*` namespace. Never rewrite the whole file; never touch a key outside that namespace |
| 4 | **Two escaping layers, handled separately.** The `wt` layer (`;` is a subcommand separator, a literal one needs escaping) and the host layer (JSON, PowerShell) are different rule sets and must never be collapsed into one substitution pass |
| 5 | **Back up before writing, and make rollback a button.** The live `settings.json` sits under `%LOCALAPPDATA%\Packages\...\LocalState\` and is under no version control |
| 6 | **Show the full diff before any write.** Not a summary. The bytes that are about to land on disk. This is also the only debugging tool this program has |
| 7 | **Stamp artifacts with their provenance** (source definition, content hash, timestamp). If an artifact was hand-edited, refuse to overwrite it and say so rather than silently discarding the edit |
| 8 | **Write only, never read.** Terminal exposes no supported way to read back a running window's pane structure. Layout generation is one-directional; "save my current window as a workspace" is not possible |
| 9 | **Carry pane commands verbatim.** No injected `cd`, no auto-activated virtualenv, no guessing the package manager. Shell differences (`-NoExit`, `/k`, `exec bash`) are the generator's business because they are `wt` mechanics, not the user's command |
| 10 | **A theme spans two files.** Terminal's profile keys and the shell prompt's own colours are one unit; emit both sides or neither. Generate a pure-data colour file for the prompt to dot-source - never rewrite the user's `prompt` function |
| 11 | **Never generate `.vbs`.** It is the only script form that fully suppresses the console flash, but Windows Script Host is widely disabled and antivirus heuristics dislike it. A `.lnk` pointing at `wt.exe` gets the same result cleanly |
| 12 | **Paths must support variables.** A definition that can only hold absolute paths is useless on the next machine, which defeats the entire point |
| 13 | **Do not reimplement what Terminal's settings UI already covers.** Profiles, colour schemes, fonts, keybindings: send the user there. The only reason to touch a profile key is rule 10 |

## Toolchain

| | |
|---|---|
| Runtime | Python >= 3.11, **standard library only** (tkinter for the GUI) |
| Environment | uv |
| Lint / format | ruff |
| Types | mypy, strict |
| Tests | pytest |
| Packaging | PyInstaller, single file |

```sh
uv sync                  # create the environment
uv run ruff check .      # lint
uv run ruff format .     # format
uv run mypy              # type check
uv run pytest            # tests
uv run magiterm          # run the app
```

### Zero runtime dependencies is a design goal

`dependencies` in `pyproject.toml` is empty and stays that way; a test asserts it. This is a
config tool opened once every few months, and needing no environment at all is what makes it
still work half a year later.

The one place that tempts a dependency is `.lnk` generation - a binary format, normally done
with `pywin32`. It goes through PowerShell's `WScript.Shell.CreateShortcut` instead. PowerShell
is already present on any machine this runs on, and this program already emits `.ps1`, so that
route adds no new surface.

## Layout

```
src/magiterm/     product code; import as `from magiterm import ...`
tests/            pytest suite
spike/            throwaway verification scripts, excluded from lint, types and packaging
```

The long name `MagiTerminalManager` is the product. The short name `magiterm` is used for every
machine-visible identifier: this package, the CLI, the `User.MagiTerm.*` id namespace written
into `settings.json`, and the generated `magiterm-theme.ps1`.

## Language

Everything in this repository is written in English, including comments, docstrings, test
names, error messages and documentation.

## License

MIT
