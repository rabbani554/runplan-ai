# runplan-ai

> 🌐 [Read in English](README.md)

Integrasi COROS + AI yang membaca data jam tanganmu, menanyakan goalmu, lalu generate program latihan terstruktur dan mengupload langsung ke akun COROS melalui web API.

Dibuat untuk kebutuhan pribadi, dibagikan kalau bermanfaat buat yang lain.

---

## Latar Belakang

Saya ingin program latihan yang dibuat dari data kondisi nyata — bukan template generik. Aplikasi berbayar seperti Runna ada, tapi harganya tidak sebanding dengan apa yang mereka tawarkan. Ketika COROS merilis MCP (Model Context Protocol), AI assistant jadi bisa baca data jam tangan secara langsung: VO2max, resting HR, waktu race terakhir, training load, HRV. Hambatan utama hilang, jadi saya buat ini.

Ini bukan produk. Ini script dan instruksi untuk Claude yang kebetulan cukup berguna untuk dibagikan.

---

## Apa yang dilakukan

1. Baca data COROS lewat MCP — VO2max, resting HR, waktu race terakhir, training load, HRV
2. Tanya hanya yang tidak bisa dibaca — goal, tanggal race, hari yang tersedia, riwayat cedera, akses alat
3. Hitung zona latihan dari data yang sebenarnya (pace + HR)
4. Generate program lari — 8–24 minggu, struktur polarized 80/20
5. Generate program strength dari 216 exercise khusus pelari, disesuaikan dengan riwayat cedera, jarak race, fase training, alat yang tersedia, dan data recovery harian
6. Upload keduanya ke COROS via internal web API

---

## AI Tools yang Kompatibel

Tiap platform membaca file instruksinya sendiri secara otomatis:

| Tool | File instruksi | Cara buka |
|---|---|---|
| **Claude Code** | `CLAUDE.md` | `claude .` di terminal |
| **OpenAI Codex** | `AGENTS.md` | `codex` di terminal |
| **Cursor** | `.cursor/rules/coros-coach.mdc` | Buka folder di Cursor |

Script Python dan format `training_plan.json` bekerja sama di semua tool.

> **Catatan MCP**: Pembacaan data otomatis butuh AI tool yang support MCP. Claude Code dan Cursor keduanya support. Tanpa MCP, AI akan minta data fitness secara manual — generate plan tetap bisa jalan.

---

## Yang Dibutuhkan

- Python 3.8+
- Akun COROS dengan minimal satu perangkat terhubung
- Salah satu AI tool di atas (butuh langganan berbayar atau API key)
- COROS MCP yang dikonfigurasi di AI tool (opsional — untuk baca data otomatis)
- Google Chrome (untuk ambil auth token COROS)

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

### 3. Konfigurasi COROS MCP (opsional tapi disarankan)

Tambahkan ke pengaturan MCP di Claude Code:

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

Tanpa ini, AI akan minta data fitness secara manual.

### 4. Ambil auth token COROS

Script upload butuh dua nilai dari browser:

1. Buka [t.coros.com](https://t.coros.com) di Chrome dalam kondisi login
2. Tekan **F12** → tab **Network** → filter `teamapi`
3. Klik salah satu request → tab **Headers**
4. Copy `accesstoken`
5. Copy `yfheader` — bentuknya `{"userId":"123456789"}` — angkanya adalah `user_id`

Buat `auth.json` di root project (sudah di-gitignore — tidak akan ter-commit):

```json
{
  "access_token": "tempel_accesstoken_di_sini",
  "user_id": "tempel_userid_di_sini"
}
```

### 5. Buka di AI tool

```bash
claude .
```

AI membaca file instruksi secara otomatis dan melanjutkan dari sana.

---

## Cara Kerjanya

```
COROS MCP baca data                    (~10 detik, otomatis)
        ↓
AI tanya yang tidak bisa dibaca        (~3–5 menit, kamu jawab)
        ↓
Tulis athlete_profile.md               (otomatis)
        ↓
Generate training_plan.json            (~5–10 menit — tahap terlama)
        ↓
Tampilkan preview untuk direview       (~1 menit, kamu konfirmasi)
        ↓
python scripts/upload_plan.py          (~30 detik, otomatis)
        ↓
Program muncul di aplikasi COROS
```

**Total waktu: sekitar 15–20 menit.**

Tahap generate adalah yang paling lama — AI sedang menulis setiap sesi latihan selama beberapa minggu. Ini normal, bukan error atau freeze.

---

## Struktur File

```
runplan-ai/
├── CLAUDE.md                   ← instruksi untuk Claude Code
├── AGENTS.md                   ← instruksi untuk OpenAI Codex
├── .cursor/rules/              ← instruksi untuk Cursor
├── README.md                   ← versi Inggris
├── README.id.md                ← file ini
├── requirements.txt
├── .gitignore
├── auth.json.example
├── templates/
│   └── athlete_profile.md
├── data/
│   └── coros_exercises.json    ← 382 exercise COROS (216 relevan untuk pelari)
├── docs/
│   └── plan-schema.md          ← referensi schema training_plan.json
└── scripts/
    └── upload_plan.py
```

---

## Program Latihan

**Struktur lari:**
- Polarized 80/20 — 80% easy Z2, 20% sesi quality
- Kenaikan km per minggu maksimal 10%
- Recovery week setiap minggu ke-4 (volume turun 30–40%)
- Race taper di 2–3 minggu terakhir (volume turun 40–50%)
- Jenis sesi: easy, long, recovery, tempo, interval, marathon pace, time trial, strides

**Program strength:**

Dari 382 total exercise di COROS, 216 melatih otot yang relevan untuk pelari (glutes, quads, hamstrings, calves, core, lower back). Program disesuaikan berdasarkan:

| Input | Efeknya |
|---|---|
| Akses alat | Filter ke pool bodyweight / home / gym |
| Riwayat cedera | Substitusi exercise per area yang bermasalah |
| Jarak race | Sesuaikan penekanan (power vs stabilitas vs ketahanan) |
| Fase training | Geser range rep (base 3×12 → build 4×8 → peak 4×6 → taper 2×8) |
| Training load (MCP) | Kurangi volume saat overreaching |
| Recovery + HRV (MCP) | Tandai sesi opsional saat readiness rendah |
| Terrain | Tambah eccentric loading untuk rute berbukit |

Pool exercise berdasarkan alat:

| Pool | Jumlah | Butuh |
|---|---|---|
| Bodyweight / resistance band | 148 | Tidak ada |
| Home setup | 28 | Dumbbell atau kettlebell |
| Full gym | 40 | Barbell, cable, mesin gym |

---

## Berbagi ke Orang Lain

Setiap orang butuh `auth.json` sendiri — token COROS bersifat per akun. Semua yang lain bisa langsung dipakai.

> **Catatan penggunaan API**: Repo ini menggunakan internal web API COROS — request yang sama yang dikirim browser saat menggunakan t.coros.com. Hanya mengakses akun milik sendiri. Tidak ada data yang dikirim ke tempat lain. Gunakan sesuai kebijaksanaan masing-masing.

---

## Troubleshooting

**`auth.json not found`** — copy `auth.json.example` dan isi dengan token yang valid.

**`401 Unauthorized`** — token expired. Ulangi langkah browser untuk ambil token baru.

**MCP tidak tersedia** — AI akan minta data secara manual. Generate plan tetap bisa jalan.

**Program tidak muncul di aplikasi** — token mungkin expired di tengah upload. Ambil token baru dan jalankan ulang `upload_plan.py`.

**AI tidak mulai otomatis** — pastikan membuka root project, bukan subfolder.

---

## Catatan tentang keterbatasan

Program latihan yang digenerate AI adalah titik awal, bukan resep yang harus diikuti sepenuhnya.

Model ini bekerja dari input terstruktur — pace, zona HR, catatan cedera, training load — tapi tidak bisa melihat cara kamu bergerak, membaca kelelahan yang tidak tertangkap data, atau menyesuaikan secara real-time seperti yang bisa dilakukan coach yang benar-benar mengenal atletnya. Ada banyak variabel yang menentukan apakah sebuah program cocok untuk seseorang di minggu tertentu: kualitas tidur, tekanan hidup, motivasi, kondisi cuaca, sakit ringan. Sebagian besar dari ini tidak terlihat oleh algoritma apapun.

Beberapa catatan jujur:

- **Konsultasikan dengan coach atau fisioterapis** jika kamu sedang kembali dari cedera, mempersiapkan race pertama, atau menghadapi nyeri yang berulang. Tool ini bukan pengganti bimbingan profesional.
- **Percayai tubuh lebih dari jadwal.** Kalau sebuah sesi terasa tidak benar — terlalu berat, terlalu mudah, atau ada yang sakit — sesuaikan. Tidak ada program yang sempurna bertahan kontak dengan realita.
- **AI bisa salah.** Kalkulasi zona bisa meleset jika data input terbatas. Struktur sesi mungkin tidak cocok dengan fisiologi spesifik kamu. Anggap output ini sebagai draf, bukan jawaban final.
- **Kemajuan butuh waktu.** Program yang terstruktur membantu, tapi konsistensi, tidur, dan nutrisi lebih menentukan daripada desain sesi manapun.

Gunakan ini sebagai alat untuk mengurangi hambatan dalam perencanaan — bukan sebagai pengganti pemahaman terhadap latihanmu sendiri.

---

## Kontribusi

Perbaikan, peningkatan, dan mapping exercise tambahan dipersilakan. Buka issue atau PR.

---

## Dokumentasi

- [docs/plan-schema.md](docs/plan-schema.md) — referensi schema `training_plan.json`

---

## Lisensi

MIT
