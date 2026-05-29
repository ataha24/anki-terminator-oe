# Anki Terminator + Open Evidence

Built on [Anki Terminator V2](http://patreon.com/Shigeyuki) by Shigeyuki.

---

## Contributors

**Alaa Taha** and **Jerry Shen** extended this fork with Open Evidence integration and a full UI overhaul:

- Integrated **Open Evidence** as a native AI mode with 5 one-click medical preset queries
- Per-card chat sessions — each card gets its own conversation history
- Configurable default preset via combo box
- Visual overhaul: accent colours, animated loading spinner, AI name button, accent bar
- Streamlined toolbar shared across all AI modes

---

## What's included

- All original Anki Terminator AI modes (ChatGPT, Claude, Perplexity, DeepSeek, Grok, DuckDuckGo AI, etc.)
- **Open Evidence** — medical AI integrated directly into the sidebar, with 5 one-click preset queries (Mechanism, Board Pearl, Distinguish, Presentation, Management)

## Installation

**Option A — Direct install (easiest):**
Download the `.ankiaddon` file from the [releases](../../releases) section (or the repo root), then double-click it. Anki installs it automatically.

**Option B — Manual:**
1. Quit Anki if it's running.
2. Find your Anki addons folder:
   - **Mac**: `~/Library/Application Support/Anki2/addons21/`
   - **Windows**: `%APPDATA%\Anki2\addons21\`
   - **Linux**: `~/.local/share/Anki2/addons21/`
3. Copy this entire folder into `addons21/` — name the folder anything you want (e.g. `anki_terminator_oe`).
4. Open Anki. The addon loads automatically.

## Using Open Evidence

1. Click the **AI** button in Anki's top toolbar (or use **Ctrl+G**) to open the sidebar.
2. Inside the sidebar, click the **AI** button (top-left) to open the AI picker menu.
3. Select **Open Evidence** from the list.
4. The 5 medical preset buttons appear: **Mechanism · Board Pearl · Distinguish · Presentation · Management**.
5. Click any preset to instantly send a USMLE-focused query about the current card to Open Evidence.
6. Enable **auto-send** (checkbox in the sidebar toolbar) to automatically query Open Evidence each time you flip a card.

> You need to be logged in to Open Evidence in the embedded browser for queries to work. Log in once and the session is remembered.
