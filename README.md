# COROS AI Running Coach

> 🌐 [Baca dalam Bahasa Indonesia](README.id.md)

Turn your COROS watch into a personalized training partner. Clone this repo, open it in Claude Code — Claude reads your COROS data automatically, asks a few questions about your goals, generates a full structured plan, and uploads it directly to your watch.

No paid subscription. No spreadsheets. No manual entry.

---

## Why I built this

I wanted a training plan that actually fits *me* — my current pace, my schedule, my goals — not a generic template. The problem: every app that does this costs money. A lot of it. Apps like Runna charge monthly fees that add up fast, and at the end of the day they're still just pre-built plans with some light customization on top.

Then COROS released their MCP (Model Context Protocol) — a direct connection between AI assistants and your watch data. That changed everything. Claude can now read your real fitness metrics, VO2max, resting HR, recent race times, training load, and HRV directly from your COROS account. No manual input. No guessing.

So I built this: an AI coach that knows your actual fitness, understands periodization and training science, generates a plan built specifically for you, and pushes it straight to your COROS app — for free.

If you're a COROS user and tired of paying for apps that don't do anything smarter than Claude already can, this repo is for you.

---

## What it does

1. **Reads your COROS data automatically** via MCP — fitness score, VO2max, recent race times, training load, HRV, resting HR
2. **Asks only what it can't read** — your goal, race date, available training days, injury history
3. **Calculates your training zones** — pace zones and HR zones from your actual data
4. **Generates a structured plan** — 8–24 weeks, polarized 80/20 structure, with optional strength training
5. **Uploads directly to COROS** — plan appears in your app, ready to activate

---

## Compatible AI Tools

This repo works with multiple AI coding assistants. Each platform reads its own instruction file automatically:

| Tool | Instruction file | How to open |
|---|---|---|
| **Claude Code** | `CLAUDE.md` | `claude .` in terminal |
| **OpenAI Codex** | `AGENTS.md` | `codex` in terminal |
| **Cursor** | `.cursor/rules/coros-coach.mdc` | Open folder in Cursor |

All three files contain the same coaching logic. The Python upload script and `training_plan.json` format work identically regardless of which tool you use.

> **MCP note**: COROS MCP (for automatic data reading) requires your AI tool to support the Model Context Protocol. Claude Code and Cursor both support MCP. If your tool doesn't support MCP, the AI will ask you to enter your fitness data manually instead — the plan generation still works.

---

## Requirements

- Python 3.8 or newer
- A COROS account with at least one connected device
- One of the compatible AI tools above (requires paid plan or API key)
- COROS MCP configured in your AI tool (optional but recommended — for automatic data reading)
- Google Chrome (to grab your COROS auth token for plan upload)

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/rabbani554/runplan-ai.git
cd runplan-ai
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure COROS MCP (for automatic data reading)

COROS MCP lets Claude read your watch data directly. Add it to your Claude Code MCP settings:

```json
{
  "mcpServers": {
    "coros": {
      "command": "npx",
      "args": ["-y", "@coros/mcp-server"]
    }
  }
}
```

> If MCP is not configured, Claude will ask you to fill in your fitness data manually instead. The plan generation still works — it just requires more manual input.

### 4. Get your COROS token (for plan upload)

You need two values from your browser session:

1. Open [t.coros.com](https://t.coros.com) in Chrome while logged in
2. Press **F12** → go to the **Network** tab
3. Type `teamapi` in the filter box
4. Click on any request that appears → click the **Headers** tab
5. Copy the value of `accesstoken`
6. Copy the value of `yfheader` — it looks like `{"userId":"123456789"}` — the number is your `user_id`

Create a file called `auth.json` in the project root (it's gitignored — never committed):

```json
{
  "access_token": "paste_your_accesstoken_here",
  "user_id": "paste_your_userid_here"
}
```

### 5. Open in Claude Code

```bash
claude .
```

Claude reads `CLAUDE.md` automatically and handles everything from here.

---

## How it works

```
COROS MCP reads your data automatically   (~10 sec, automatic)
        ↓
Claude asks only what it can't read       (~3–5 min, you answer)
(goal, race date, schedule, injuries)
        ↓
Claude writes athlete_profile.md          (automatic)
        ↓
Claude generates training_plan.json       (~5–10 min — the longest step)
        ↓
Claude shows you the full plan preview    (~1 min, you review)
You confirm or request changes
        ↓
python scripts/upload_plan.py             (~30 sec, automatic)
        ↓
Plan appears in your COROS app
```

**Total time: ~15–20 minutes end to end.**

The plan generation step takes the longest — Claude is building a full multi-week structured program session by session. This is normal; it is not frozen.

After upload, Claude gives you a direct link. Open it and hit **Start Plan** to set your start date.

---

## File structure

```
coros-coach/
├── CLAUDE.md                   ← orchestration instructions for Claude
├── README.md                   ← this file
├── requirements.txt
├── .gitignore                  ← auth.json and athlete_profile.md are excluded
├── auth.json.example           ← template (copy to auth.json and fill in)
├── templates/
│   └── athlete_profile.md      ← questionnaire template
├── data/
│   └── coros_exercises.json    ← full COROS strength exercise library (382 exercises)
└── scripts/
    └── upload_plan.py          ← converts training_plan.json → COROS API calls
```

Files created during your session (gitignored):
- `auth.json` — your personal COROS token
- `athlete_profile.md` — your profile (auto-filled from MCP + your answers)
- `training_plan.json` — the generated plan in machine-readable format

---

## Training plan features

- **Reads real data** — zones calculated from your actual VO2max, resting HR, and race times
- **80/20 polarized structure** — 80% easy Z2, 20% quality
- **Progressive overload** — weekly km increases ≤10%
- **Recovery weeks** — every 4th week drops 30–40%
- **Race taper** — volume reduces 40–50% in final 2–3 weeks
- **Session types**: easy run, long run, recovery run, tempo, intervals, marathon pace, time trial, strides
- **Strength training** (optional): lower body A, upper/core B, full body circuits — scheduled around running sessions

---

## Sharing with friends

Each person needs their own `auth.json` with their own COROS token — tokens are personal and account-specific. Everything else in the repo is reusable.

> **Legal note**: This uses COROS's internal web API (the same requests your browser makes when you use t.coros.com). It reads and writes your own account only. No data is shared with third parties. Use responsibly.

---

## Troubleshooting

**`auth.json not found`** — create it from `auth.json.example` with your real token.

**`401 Unauthorized`** — your token has expired. Repeat the browser steps to get a fresh `accesstoken`.

**MCP tools not found** — Claude will fall back to the manual questionnaire. You can still get a full plan, just with more questions.

**Plan not showing in app** — tokens sometimes expire mid-upload. Re-fetch and re-run `upload_plan.py`.

**Claude doesn't start automatically** — make sure you opened the project root with `claude .` (not a subdirectory).

---

## Documentation

- [docs/plan-schema.md](docs/plan-schema.md) — full reference for `training_plan.json` (step types, HR zones, strength exercises, examples)

---

## License

MIT — fork it, adapt it, share it.
