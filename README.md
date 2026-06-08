# runplan-ai

> 🌐 [Baca dalam Bahasa Indonesia](README.id.md)

A COROS + AI integration that reads your watch data, asks about your goals, and generates a structured training plan — then uploads it directly to your COROS account via the web API.

Built for personal use, shared in case it helps others.

---

## Background

I wanted a training plan based on my actual data — not a generic template. Paid apps like Runna exist, but they're expensive for what they do. When COROS released their MCP (Model Context Protocol), it became possible for an AI assistant to read watch data directly: VO2max, resting HR, recent race times, training load, HRV. That removed the main blocker, so I built this.

It's not a product. It's a script and a set of instructions for Claude that happens to work well enough to share.

---

## What it does

1. Reads your COROS data via MCP — VO2max, resting HR, recent race times, training load, HRV
2. Asks only what it can't read — goal, race date, available days, injury history, equipment access
3. Calculates training zones from your actual data (pace + HR)
4. Generates a running plan — 8–24 weeks, polarized 80/20 structure
5. Generates a strength program from 216 runner-relevant exercises, adapted to your injury history, race distance, training phase, equipment, and daily recovery data
6. Uploads both to COROS via the internal web API

---

## Compatible AI Tools

Each platform reads its own instruction file automatically:

| Tool | Instruction file | How to open |
|---|---|---|
| **Claude Code** | `CLAUDE.md` | `claude .` in terminal |
| **OpenAI Codex** | `AGENTS.md` | `codex` in terminal |
| **Cursor** | `.cursor/rules/coros-coach.mdc` | Open folder in Cursor |

The Python upload script and `training_plan.json` format work the same regardless of which tool you use.

> **MCP note**: Automatic data reading requires your AI tool to support MCP. Claude Code and Cursor both do. Without MCP, the AI asks for your fitness data manually — plan generation still works either way.

---

## Requirements

- Python 3.8+
- A COROS account with at least one connected device
- One of the compatible AI tools above (requires paid plan or API key)
- COROS MCP configured in your AI tool (optional — for automatic data reading)
- Google Chrome (to extract your COROS auth token for plan upload)

---

## Setup

### 1. Clone

```bash
git clone https://github.com/rabbani554/runplan-ai.git
cd runplan-ai
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure COROS MCP (optional but recommended)

Add to your Claude Code MCP settings:

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

Without this, Claude will ask you to fill in your fitness data manually.

### 4. Get your COROS auth token

The upload script needs two values from your browser:

1. Open [t.coros.com](https://t.coros.com) in Chrome while logged in
2. Press **F12** → **Network** tab → filter by `teamapi`
3. Click any request → **Headers** tab
4. Copy `accesstoken`
5. Copy `yfheader` — looks like `{"userId":"123456789"}` — the number is your `user_id`

Create `auth.json` in the project root (gitignored — never committed):

```json
{
  "access_token": "paste_your_accesstoken_here",
  "user_id": "paste_your_userid_here"
}
```

### 5. Open in your AI tool

```bash
claude .
```

The AI reads the instruction file automatically and walks through the rest.

---

## How it works

```
COROS MCP reads your data              (~10 sec, automatic)
        ↓
AI asks what it can't read             (~3–5 min, you answer)
        ↓
Writes athlete_profile.md              (automatic)
        ↓
Generates training_plan.json           (~5–10 min — the longest step)
        ↓
Shows full plan preview for review     (~1 min, you confirm)
        ↓
python scripts/upload_plan.py          (~30 sec, automatic)
        ↓
Plan appears in COROS app
```

**Typical end-to-end: ~15–20 minutes.**

The generation step takes the longest — the AI is writing out every session across multiple weeks. It is not frozen; it just takes time.

---

## File structure

```
runplan-ai/
├── CLAUDE.md                   ← instructions for Claude Code
├── AGENTS.md                   ← instructions for OpenAI Codex
├── .cursor/rules/              ← instructions for Cursor
├── README.md                   ← this file
├── README.id.md                ← Bahasa Indonesia
├── requirements.txt
├── .gitignore
├── auth.json.example
├── templates/
│   └── athlete_profile.md
├── data/
│   └── coros_exercises.json    ← 382 COROS exercises (216 runner-relevant)
├── docs/
│   └── plan-schema.md          ← training_plan.json schema reference
└── scripts/
    └── upload_plan.py
```

---

## Training plan

**Road running structure:**
- Polarized 80/20 — 80% easy Z2, 20% quality sessions
- Weekly km increase capped at 10%
- Recovery week every 4th week (30–40% volume reduction)
- Race taper in final 2–3 weeks (40–50% reduction)
- Session types: easy, long, recovery, tempo, intervals, marathon pace, time trial, strides

**Trail running structure:**

Trail training uses different metrics from road — pace is unreliable on variable terrain.

- All session targets are HR-based — no pace targets
- Long runs measured in time on feet (TOF) + weekly elevation gain target, not km
- Weekly elevation builds progressively to 60–75% of race total elevation at peak week
- Hill repeats replace road interval sessions
- Back-to-back long run weekends for races ≥30km (one per 3-week block in Build phase)
- Supports road trail 20–30km, ultra 50km+, and vertical KM/skyrace with different strength emphasis per distance

**Urban trail runner support:**

For athletes who can only access trails on specific days:

- Elevation-dependent sessions (hill repeats, trail long runs) scheduled only on stated access days
- Flat day substitutes: treadmill at 6–8% incline with same HR target, or stair repeats
- Limited trail access triggers increased eccentric strength volume on weekday sessions to compensate for missing downhill loading

**Strength program:**

Of 382 total COROS exercises, 216 target muscles relevant to running (glutes, quads, hamstrings, calves, core, lower back). The program is adapted based on:

| Input | Effect |
|---|---|
| Equipment access | Filters to bodyweight / home / gym pool |
| Injury history | Substitutes risky exercises per area |
| Race distance | Adjusts emphasis (power vs stability vs endurance) |
| Training phase | Shifts rep range (base 3×12 → build 4×8 → peak 4×6 → taper 2×8) |
| Training load (MCP) | Reduces volume when overreaching |
| Recovery score + HRV (MCP) | Flags session optional when readiness is low |
| Terrain | Adds eccentric loading for hilly routes |

Exercise pool by equipment:

| Pool | Count | Requires |
|---|---|---|
| Bodyweight / resistance band | 148 | Nothing |
| Home setup | 28 | Dumbbells or kettlebells |
| Full gym | 40 | Barbell, cables, machines |

---

## Sharing with others

Each person needs their own `auth.json` — COROS tokens are account-specific. Everything else is reusable.

> **Note on API usage**: This uses COROS's internal web API — the same requests your browser sends when using t.coros.com. It only accesses your own account. No data is sent anywhere else. Use at your own discretion.

---

## Troubleshooting

**`auth.json not found`** — copy `auth.json.example` and fill in your token.

**`401 Unauthorized`** — token expired. Repeat the browser steps to get a fresh one.

**MCP not available** — AI will ask for data manually. Plan generation still works.

**Plan not appearing in app** — token may have expired mid-upload. Re-fetch and rerun `upload_plan.py`.

**AI doesn't start** — make sure you opened the project root, not a subfolder.

---

## A note on limitations

An AI-generated training plan is a starting point, not a prescription.

The model works from structured inputs — pace, HR zones, injury flags, training load — but it cannot observe how you move, read fatigue that doesn't show in data, or adjust in real time the way a coach who knows you can. There are many variables that influence whether a plan is right for a given person on a given week: sleep quality, life stress, motivation, form, terrain, heat, illness. Most of these are invisible to any algorithm.

A few honest caveats:

- **Consult a coach or physio** if you are returning from injury, training for your first race, or dealing with recurring pain. This tool is not a substitute for professional guidance.
- **Trust your body over the plan.** If a session feels wrong — too hard, too easy, or something hurts — adjust it. No plan survives contact with reality perfectly.
- **AI makes mistakes.** Zone calculations may be off if your input data is sparse. Session structure may not suit your specific physiology. Treat the output as a draft, not a final answer.
- **Progress takes time.** A well-structured plan helps, but consistency, sleep, and nutrition matter more than any specific session design.

Use this as a tool to reduce friction in planning — not as a replacement for understanding your own training.

---

## Contributing

Fixes, improvements, and additional exercise mappings are welcome. Open an issue or PR.

---

## Documentation

- [docs/plan-schema.md](docs/plan-schema.md) — `training_plan.json` schema reference

---

## License

MIT
