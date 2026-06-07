# COROS AI Running Coach

> 🌐 [Read in English](README.md)

Jadiin jam COROS kamu sebagai pelatih lari personal. Clone repo ini, buka di Claude Code — Claude otomatis baca data COROS kamu, tanya beberapa hal soal target kamu, bikin program latihan yang beneran pas buat kamu, terus langsung upload ke jam tangan kamu.

Ga perlu langganan berbayar. Ga perlu spreadsheet. Ga perlu input manual.

---

## Kenapa Gue Bikin Ini

Gue pengen punya program latihan yang beneran disesuaiin sama kondisi gue — bukan template generik yang dipake semua orang. Masalahnya, semua aplikasi yang bisa bikin program kayak gitu bayar. Dan mahal. Runna misalnya, bayar bulanan terus, padahal ujung-ujungnya tetep cuma template dengan sedikit kustomisasi doang.

Terus COROS ngerilis MCP-nya — koneksi langsung antara AI dan data dari jam tangan kamu. Nah ini yang bikin semuanya berubah. Claude sekarang bisa baca data fitness kamu langsung dari akun COROS: VO2max, detak jantung istirahat, waktu race terakhir, training load, HRV — semua otomatis. Ga perlu input manual.

Jadi gue bikin ini: AI coach yang tau kondisi kamu sebenarnya, ngerti cara bikin program latihan yang bener secara ilmiah, generate plan yang beneran personalized buat kamu, terus langsung upload ke aplikasi COROS kamu — dan ini **gratis**.

Kalau kamu pengguna COROS dan udah capek bayar aplikasi yang sebenernya ga lebih pinter dari Claude, repo ini buat kamu.

---

## Fitur Utama

1. **Baca data COROS kamu otomatis** lewat MCP — fitness score, VO2max, waktu race terakhir, training load, HRV, resting HR
2. **Nanya cuma yang ga bisa dibaca** — goal kamu, tanggal race, hari latihan yang kosong, riwayat cedera
3. **Hitung zona latihan kamu** — pace zone dan HR zone dari data kamu yang sebenarnya
4. **Generate program terstruktur** — 8–24 minggu, struktur polarized 80/20, dengan strength training opsional
5. **Upload langsung ke COROS** — program langsung muncul di aplikasi, tinggal aktifin

---

## AI Tools yang Kompatibel

Repo ini bisa dijalankan pakai beberapa AI coding assistant. Tiap platform otomatis baca file instruksinya masing-masing:

| Tool | File instruksi | Cara buka |
|---|---|---|
| **Claude Code** | `CLAUDE.md` | `claude .` di terminal |
| **OpenAI Codex** | `AGENTS.md` | `codex` di terminal |
| **Cursor** | `.cursor/rules/coros-coach.mdc` | Buka folder di Cursor |

Ketiga file ini isinya sama persis — logika coaching-nya identik. Script Python dan format `training_plan.json` juga sama, tidak peduli pakai tool mana.

> **Catatan MCP**: COROS MCP (untuk baca data otomatis) butuh AI tool kamu support Model Context Protocol. Claude Code dan Cursor keduanya support MCP. Kalau tool kamu belum support MCP, AI bakal nanya data fitness kamu secara manual — generate plan-nya tetap bisa jalan.

---

## Yang Lo Butuhkan

- Python 3.8 atau lebih baru
- Akun COROS dengan minimal satu perangkat yang terhubung
- Salah satu AI tool yang kompatibel di atas (butuh langganan berbayar atau API key)
- COROS MCP yang sudah dikonfigurasi (opsional tapi direkomendasikan — untuk baca data otomatis)
- Google Chrome (buat ambil token COROS untuk upload program)

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

### 3. Setup COROS MCP (biar data kamu kebaca otomatis)

COROS MCP yang bikin Claude bisa baca data jam tangan kamu langsung. Tambahin ke pengaturan MCP di Claude Code:

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

> Kalau MCP belum dikonfigurasi, Claude bakal nanya data fitness kamu secara manual. Program tetap bisa dibuat — cuma butuh lebih banyak pertanyaan.

### 4. Ambil token COROS (untuk upload program)

Lo butuh dua nilai dari browser:

1. Buka [t.coros.com](https://t.coros.com) di Chrome dalam kondisi sudah login
2. Tekan **F12** → buka tab **Network**
3. Ketik `teamapi` di kotak filter
4. Klik salah satu request yang muncul → klik tab **Headers**
5. Copy nilai `accesstoken`
6. Copy nilai `yfheader` — bentuknya kayak `{"userId":"123456789"}` — angkanya itu `user_id` kamu

Buat file bernama `auth.json` di root project (sudah di-gitignore — tidak akan ter-commit):

```json
{
  "access_token": "tempel_accesstoken_lo_di_sini",
  "user_id": "tempel_userid_lo_di_sini"
}
```

### 5. Buka di Claude Code

```bash
claude .
```

Claude otomatis baca `CLAUDE.md` dan ngurusin sisanya dari sini.

---

## Cara Kerjanya

```
COROS MCP baca data kamu otomatis
        ↓
Claude cuma nanya yang ga bisa dibaca
(goal, tanggal race, jadwal, cedera)
        ↓
Claude nulis athlete_profile.md
        ↓
Claude generate training_plan.json
        ↓
python scripts/upload_plan.py
        ↓
Program muncul di aplikasi COROS kamu
```

Setelah upload, Claude kasih kamu link langsung. Buka dan klik **Start Plan** untuk set tanggal mulai.

---

## Struktur File

```
coros-coach/
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

File yang dibuat selama sesi kamu (tidak di-commit):
- `auth.json` — token COROS personal kamu
- `athlete_profile.md` — profil kamu (diisi otomatis dari MCP + jawaban kamu)
- `training_plan.json` — program yang sudah digenerate

---

## Fitur Program Latihan

- **Baca data nyata kamu** — zona dihitung dari VO2max, resting HR, dan waktu race kamu yang sebenarnya
- **Struktur polarized 80/20** — 80% easy Z2, 20% sesi quality
- **Progressive overload** — kenaikan km per minggu maksimal 10%
- **Recovery week** — setiap minggu ke-4 volume turun 30–40%
- **Race taper** — volume turun 40–50% di 2–3 minggu terakhir sebelum race
- **Jenis sesi**: easy run, long run, recovery run, tempo, interval, marathon pace, time trial, strides
- **Strength training** (opsional): lower body, upper/core, full body circuit — dijadwalkan tidak bentrok sama sesi lari

### Personalisasi strength training

Program kekuatan disesuaikan berdasarkan:

| Sinyal | Dari mana | Efeknya |
|---|---|---|
| Riwayat cedera | Pertanyaan | Latihan diganti (misal nyeri lutut → box step-up gantiin squat) |
| Fase training | Minggu ke berapa | Set/rep/istirahat berubah sesuai fase (base → build → peak → taper) |
| Jarak race | Pertanyaan | 5k = fokus power; HM = stabilitas pinggul; maraton = pencegahan cedera |
| Training load saat ini | COROS MCP | Beban tinggi → kurangi ke 1 sesi, maks 2 set |
| Recovery score + HRV | COROS MCP | Readiness rendah → sesi jadi opsional; HRV turun → maintenance only |
| Terrain | Pertanyaan | Berbukit → tambahin sl_calf_raise eksentrik dan box step-ups |

---

## Dibagiin ke Teman

Setiap orang butuh `auth.json`-nya sendiri dengan token COROS masing-masing — token bersifat personal dan terikat ke akun COROS individu. Semua yang lain di repo ini bisa langsung dipakai.

> **Catatan legal**: Ini pakai API web internal COROS (request yang sama yang dikirim browser kamu saat pakai t.coros.com). Hanya baca dan tulis akun kamu sendiri. Tidak ada data yang dibagikan ke pihak ketiga. Gunakan dengan bijak.

---

## Troubleshooting

**`auth.json not found`** — buat dari `auth.json.example` dengan token asli kamu.

**`401 Unauthorized`** — token kamu expired. Ulangi langkah browser untuk ambil `accesstoken` baru.

**MCP tools tidak ketemu** — Claude bakal fallback ke pertanyaan manual. Program tetap bisa dibuat, cuma butuh lebih banyak input.

**Program tidak muncul di aplikasi** — token kadang expired di tengah upload. Ambil token baru dan jalanin ulang `upload_plan.py`.

**Claude tidak mulai otomatis** — pastikan kamu buka root project dengan `claude .` (bukan subdirektori).

---

## Dokumentasi

- [docs/plan-schema.md](docs/plan-schema.md) — referensi lengkap `training_plan.json` (jenis step, zona HR, latihan kekuatan, contoh)

---

## Lisensi

MIT — fork, modif, dan share sesuka kamu.
