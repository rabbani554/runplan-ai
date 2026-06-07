# COROS AI Running Coach

> 🌐 [Read in English](README.md)

Jadiin jam COROS-mu sebagai pelatih lari personal. Clone repo ini, buka di Claude Code — Claude otomatis baca datamu dari COROS, tanya beberapa hal soal targetmu, bikin program latihan yang beneran pas, lalu upload langsung ke jam tanganmu.

Tanpa langganan berbayar. Tanpa spreadsheet. Tanpa input manual.

---

## Kenapa Saya Bikin Ini

Saya pengen punya program latihan yang beneran disesuaiin sama kondisi sendiri — bukan template generik yang dipake semua orang. Masalahnya, semua aplikasi yang bisa bikin program kayak gitu bayar. Dan mahal. Runna misalnya, bayar bulanan terus, padahal ujung-ujungnya tetep cuma template dengan sedikit kustomisasi doang.

Terus COROS ngerilis MCP-nya — koneksi langsung antara AI dan data jam tangan. Nah ini yang bikin semuanya berubah. Claude sekarang bisa baca data fitness langsung dari akun COROS: VO2max, detak jantung istirahat, waktu race terakhir, training load, HRV — semua otomatis. Ga perlu input manual.

Jadi saya bikin ini: AI coach yang tau kondisi sebenarnya, ngerti cara bikin program latihan yang bener secara ilmiah, generate plan yang beneran personal, terus langsung upload ke aplikasi COROS — dan ini **gratis**.

Kalau pengguna COROS dan udah capek bayar aplikasi yang sebenernya ga lebih pinter dari Claude, repo ini buat kita semua.

---

## Fitur Utama

1. **Baca datamu otomatis** lewat MCP — fitness score, VO2max, waktu race terakhir, training load, HRV, resting HR
2. **Nanya cuma yang ga bisa dibaca** — goal, tanggal race, jadwal, riwayat cedera, akses alat
3. **Hitung zona latihanmu** — pace zone dan HR zone dari data yang sebenarnya
4. **Generate program lari terstruktur** — 8–24 minggu, struktur polarized 80/20, dengan coaching cue di setiap sesi
5. **Bangun program strength yang benar-benar personal** — pilih dari 216 exercise khusus pelari berdasarkan cederamu, jarak race, fase training, alat yang ada, dan recovery score harian; tidak ada dua atlet yang dapat program yang sama
6. **Upload semua langsung ke COROS** — sesi lari dan strength muncul di aplikasi, tinggal aktifin

---

## AI Tools yang Kompatibel

Repo ini bisa dijalankan pakai beberapa AI coding assistant. Tiap platform otomatis baca file instruksinya masing-masing:

| Tool | File instruksi | Cara buka |
|---|---|---|
| **Claude Code** | `CLAUDE.md` | `claude .` di terminal |
| **OpenAI Codex** | `AGENTS.md` | `codex` di terminal |
| **Cursor** | `.cursor/rules/coros-coach.mdc` | Buka folder di Cursor |

Ketiga file ini isinya sama persis — logika coaching-nya identik. Script Python dan format `training_plan.json` juga sama, tidak peduli pakai tool mana.

> **Catatan MCP**: COROS MCP butuh AI tool yang support Model Context Protocol. Claude Code dan Cursor keduanya support MCP. Kalau belum support, AI akan nanya data fitness secara manual — generate plan-nya tetap bisa jalan.

---

## Yang Dibutuhkan

- Python 3.8 atau lebih baru
- Akun COROS dengan minimal satu perangkat yang terhubung
- Salah satu AI tool yang kompatibel di atas (butuh langganan berbayar atau API key)
- COROS MCP yang sudah dikonfigurasi (opsional tapi direkomendasikan)
- Google Chrome (untuk ambil token COROS saat upload)

---

## Setup

### 1. Clone repo-nya

```bash
git clone https://github.com/rabbani554/runplan-ai.git
cd runplan-ai
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup COROS MCP (biar datamu kebaca otomatis)

Tambahin ke pengaturan MCP di Claude Code:

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

> Kalau MCP belum dikonfigurasi, Claude akan nanya data fitness secara manual. Program tetap bisa dibuat — cuma butuh lebih banyak pertanyaan.

### 4. Ambil token COROS (untuk upload program)

Butuh dua nilai dari browser:

1. Buka [t.coros.com](https://t.coros.com) di Chrome dalam kondisi sudah login
2. Tekan **F12** → buka tab **Network**
3. Ketik `teamapi` di kotak filter
4. Klik salah satu request yang muncul → klik tab **Headers**
5. Copy nilai `accesstoken`
6. Copy nilai `yfheader` — bentuknya kayak `{"userId":"123456789"}` — angkanya itu `user_id`

Buat file `auth.json` di root project (sudah di-gitignore — tidak akan ter-commit):

```json
{
  "access_token": "tempel_accesstoken_di_sini",
  "user_id": "tempel_userid_di_sini"
}
```

### 5. Buka di Claude Code

```bash
claude .
```

Claude otomatis baca `CLAUDE.md` dan ngurusin sisanya.

---

## Cara Kerjanya

```
COROS MCP baca data otomatis              (~10 detik, otomatis)
        ↓
Claude nanya yang ga bisa dibaca          (~3–5 menit, kamu jawab)
(goal, tanggal race, jadwal, cedera)
        ↓
Claude tulis athlete_profile.md           (otomatis)
        ↓
Claude generate training_plan.json        (~5–10 menit — ini yang paling lama)
        ↓
Claude tampilkan preview jadwal lengkap   (~1 menit, kamu review)
Konfirmasi atau minta perubahan
        ↓
python scripts/upload_plan.py             (~30 detik, otomatis)
        ↓
Program muncul di aplikasi COROS
```

**Total waktu: sekitar 15–20 menit dari awal sampai selesai.**

Step generate jadwal adalah yang paling lama — Claude sedang membangun program latihan multi-minggu secara lengkap sesi per sesi. Ini normal, bukan error atau freeze.

Setelah upload, Claude kasih link langsung. Buka dan klik **Start Plan** untuk set tanggal mulai.

---

## Struktur File

```
runplan-ai/
├── CLAUDE.md                   ← instruksi untuk Claude
├── README.md                   ← versi Inggris
├── README.id.md                ← file ini
├── requirements.txt
├── .gitignore                  ← auth.json dan athlete_profile.md tidak ikut commit
├── auth.json.example           ← template (copy ke auth.json dan isi)
├── templates/
│   └── athlete_profile.md      ← template profil atlet
├── data/
│   └── coros_exercises.json    ← library latihan kekuatan COROS (382 gerakan)
└── scripts/
    └── upload_plan.py          ← konversi training_plan.json ke COROS API
```

File yang dibuat selama sesi (tidak di-commit):
- `auth.json` — token COROS personal
- `athlete_profile.md` — profilmu (diisi otomatis dari MCP + jawabanmu)
- `training_plan.json` — program yang sudah digenerate

---

## Fitur Program Latihan

- **Berbasis data nyata** — zona dihitung dari VO2max, resting HR, dan waktu race yang sebenarnya
- **Struktur polarized 80/20** — 80% easy Z2, 20% sesi quality
- **Progressive overload** — kenaikan km per minggu maksimal 10%
- **Recovery week** — setiap minggu ke-4 volume turun 30–40%
- **Race taper** — volume turun 40–50% di 2–3 minggu terakhir sebelum race
- **Jenis sesi**: easy run, long run, recovery run, tempo, interval, marathon pace, time trial, strides

---

## Strength Training yang Benar-Benar Personal

Kebanyakan aplikasi lari kasih 6–8 gerakan yang sama diulang terus setiap minggu. Repo ini pakai database exercise COROS secara penuh — **216 exercise khusus pelari** — dan memilih dari sana berdasarkan kondisi dan kebutuhan nyata.

### Apa yang dipersonalisasi

| Sinyal | Dari mana | Efeknya |
|---|---|---|
| Akses alat | Kamu jawab | Filter ke pool bodyweight / home / gym |
| Riwayat cedera | Kamu jawab | Exercise diganti (nyeri lutut → box step-up gantiin squat) |
| Jarak race | Kamu jawab | 5k/10k = fokus power; HM = stabilitas pinggul; maraton = ketahanan |
| Fase training | Minggu ke berapa | Set/rep bergeser: base (3×12) → build (4×8) → peak (4×6) → taper (2×8) |
| Training load | COROS MCP | Beban tinggi → kurangi ke 1 sesi, maks 2 set |
| Recovery + HRV | COROS MCP | Readiness rendah → sesi jadi opsional; HRV turun → maintenance only |
| Terrain | Kamu jawab | Berbukit → tambah eccentric calf dan step-ups untuk beban turunan |

### Breakdown pool exercise

Dari 382 total exercise di COROS, **216 melatih otot yang beneran dibutuhkan pelari** (glutes, quads, hamstrings, calves, core, lower back):

| Pool | Jumlah | Kebutuhan |
|---|---|---|
| Bodyweight & resistance band | **148** | Tidak perlu alat apapun |
| Home setup | **28** | Dumbbell atau kettlebell |
| Full gym | **40** | Barbell, cable, mesin gym |

### Kenapa ini jauh lebih baik dari aplikasi template

Satu sesi strength memilih sekitar 6 exercise dari pool yang tersedia. Hanya dari 216 exercise saja, memilih 6 menghasilkan lebih dari **8 miliar kombinasi yang mungkin** — belum termasuk variasi sets, reps, istirahat, fase training, dan substitusi cedera. Tidak ada dua atlet yang dapat program yang sama persis. Aplikasi template memilih dari sekitar 20 rutinitas yang sudah dibuat sebelumnya. Ini tidak.

---

## Dibagiin ke Teman

Setiap orang butuh `auth.json`-nya sendiri dengan token COROS masing-masing — token bersifat personal dan terikat ke akun individu. Semua yang lain di repo ini bisa langsung dipakai.

> **Catatan legal**: Repo ini pakai API web internal COROS — request yang sama yang dikirim browser saat pakai t.coros.com. Hanya baca dan tulis akun sendiri. Tidak ada data yang dibagikan ke pihak ketiga. Gunakan dengan bijak.

---

## Troubleshooting

**`auth.json not found`** — buat dari `auth.json.example` dengan token yang valid.

**`401 Unauthorized`** — token sudah expired. Ulangi langkah browser untuk ambil `accesstoken` baru.

**MCP tools tidak ketemu** — Claude akan fallback ke pertanyaan manual. Program tetap bisa dibuat, cuma butuh lebih banyak input.

**Program tidak muncul di aplikasi** — token kadang expired di tengah upload. Ambil token baru dan jalanin ulang `upload_plan.py`.

**Claude tidak mulai otomatis** — pastikan buka root project dengan `claude .` (bukan subdirektori).

---

## Dokumentasi

- [docs/plan-schema.md](docs/plan-schema.md) — referensi lengkap `training_plan.json` (jenis step, zona HR, latihan kekuatan, contoh)

---

## Lisensi

MIT — fork, modif, dan share sesuka hati.
