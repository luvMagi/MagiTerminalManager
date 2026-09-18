# spike/

Throwaway verification scripts for the v0.1.0 mechanism spike.

Nothing here is product code. It is excluded from ruff, mypy and the wheel, it has no tests,
and it is held to no quality bar. Its only job is to answer twelve questions about how Windows
Terminal actually behaves, so the rest of v0.1.0 can be written against measured behaviour
instead of against inference.

## Before running anything

**Back up the live `settings.json` first.**

Two of the twelve checks modify the configuration Windows Terminal is actively using, and that
file lives under `%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\`,
which is under no version control at all. Copy it somewhere outside this repository with a date
on it before you start.

Design rule 5 requires the product to back up before writing. Whoever is writing the product
has less excuse to skip it, not more.

## What has to be measured

| # | Question | Why it blocks work |
|---|---|---|
| 1 | Can a Terminal fragment extension inject `actions` and `newTabMenu`? (It is known to handle `profiles` and `schemes`.) | **Biggest one.** If yes, this tool writes its own fragment file and never touches the user's `settings.json`, and most of the backup/rollback/concurrent-write machinery becomes unnecessary |
| 2 | What is the real length limit of a `.lnk` arguments field? | Decides whether the shortcut points straight at `wt.exe` or has to indirect through a `.ps1` |
| 3 | In the grid-of-four sequence, does `move-focus left` land on pane 1? | That template is the only one needing a focus move. If it lands elsewhere the layout comes out crooked, silently |
| 4 | Is `split-pane -s` a fraction of the parent pane or of the whole window? | The three-column and three-row templates encode thirds as `0.667` then `0.5`. If the basis is different, those numbers are wrong and the proportions are quietly off |
| 5 | Can `-EncodedCommand` and `-NoExit` be used together? | Decides whether the base64 escape hatch for awkward pane commands exists |
| 6 | How does a WSL pane actually take its starting directory? | Decides whether WSL ships in v0.1.0 and whether the shell field needs another branch |
| 7 | What does Terminal do when `settings.json` changes underneath it, and can its settings UI write back over an external edit? | Decides how far the concurrent-write mitigation has to go |
| 8 | Can `WScript.Shell.CreateShortcut` reliably set `.Hotkey` and `.IconLocation`? | **Decides whether zero runtime dependencies survives.** If not, `.lnk` generation falls back to `pywin32` |
| 9 | How does the standard library `json` fail on a `settings.json` containing `//` comments? | Decides whether a comment-tolerant parser is needed, which would cost the zero-dependency goal |
| 10 | Can Tk render the powerline separator `U+E0B0` and CJK text in Cascadia Code? | Decides how far the theme preview can go: real shapes, or colour swatches only |
| 11 | How do `SetProcessDpiAwareness` and `tk scaling` behave across monitors with different scale factors? | Decides window setup, and whether `Canvas` coordinates need manual scaling |
| 12 | Is there a "focus pane N" subcommand, and what is its index base? | Decides whether per-tab initial pane focus is a real field or a documented limitation |

## Recording results

Every finding needs three things, or it is not a finding:

1. the conclusion
2. the evidence: the command as run, the value read back, or a screenshot
3. **the Windows Terminal version** (`wt --version`)

The version is part of the conclusion, not a footnote. Fragment capability in particular is
something Microsoft is still extending, so "does not work" is only ever true for a given build.

Checks 3, 4 and 10 can only be judged by eye - a crooked layout, an off proportion and a missing
glyph all fail without raising anything. Screenshot them, or the finding cannot be reviewed.

Output goes in `spike/out/`, which is gitignored. The scripts themselves are tracked, because
how something was measured is part of the result.
