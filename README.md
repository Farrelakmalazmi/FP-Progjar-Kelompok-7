# 🐍 Snake & Ladder Online with Load Balancing 🎲

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Pygame](https://img.shields.io/badge/pygame-2.6.1-green.svg)
![Architecture](https://img.shields.io/badge/architecture-Load%20Balanced-orange.svg)

Proyek ini merupakan implementasi teknis dari permainan Ular Tangga yang dikembangkan untuk memenuhi tugas mata kuliah Pemrograman Jaringan (C). Dengan memanfaatkan kekuatan Python, library Pygame untuk rendering grafis, dan modul Socket untuk komunikasi jaringan, kami berhasil membangun sebuah aplikasi client-server yang fungsional dan terdistribusi. Fokus utama dari proyek ini adalah mendemonstrasikan arsitektur jaringan yang skalabel menggunakan **Load Balancer**, yang memungkinkan beberapa sesi permainan berjalan secara simultan di *instance* server yang berbeda.

## Tangkapan Layar (Screenshots)
Berikut ini adalah dua screenshot saat sedang bermain Snake and Ladder, dari dua client yang berbeda yang terhubung ke game server yang sama.
<p align="center">
  <img src="https://github.com/user-attachments/assets/7f97bd7b-1961-4573-b7ee-594d2d804f7f" alt="Tampilan Klien 1" width="400"/>
  <img src="https://github.com/user-attachments/assets/864f9940-4425-4eeb-a921-52b09822909d" alt="Tampilan Klien 2" width="400"/>
</p>

## Daftar Isi
- [Tentang Proyek](#tentang-proyek)
- [Fitur Unggulan](#fitur-unggulan)
- [Arsitektur & Pilihan Desain](#arsitektur--pilihan-desain)
- [Protokol Jaringan](#protokol-jaringan)
- [Struktur Proyek](#struktur-proyek)
- [Cara Menjalankan](#cara-menjalankan)
- [Tim Kami](#tim-kami)

## Tentang Proyek
Proyek Ular Tangga Multiplayer ini adalah implementasi penuh dari game klasik yang kita semua kenal, namun dibawa ke level berikutnya dengan arsitektur terdistribusi. Proyek ini tidak hanya memungkinkan dua pemain untuk bermain bersama dari komputer yang berbeda, tetapi juga menggunakan **Load Balancer** untuk mengarahkan pasangan pemain ke *instance* server game yang berbeda. Hal ini menciptakan sistem yang lebih skalabel dan tangguh, mampu menangani banyak sesi permainan secara bersamaan.

## Fitur Unggulan
Proyek ini dirancang dengan berbagai fitur untuk menciptakan pengalaman bermain yang lengkap, modern, dan stabil.

### Gameplay
- **🧑‍🤝‍🧑 Multiplayer untuk 2 Pemain**: Didesain khusus untuk dua pemain yang terhubung melalui jaringan yang sama dalam satu sesi game.
- **📜 Aturan Permainan Klasik**: Mengimplementasikan papan 10x10 dengan aturan ular (turun) dan tangga (naik).
- **⚖️ Sistem Giliran (Turn-Based) yang Adil**: Server bertindak sebagai wasit, memastikan giliran pemain berjalan secara teratur.
- **🎲 Giliran Ekstra**: Mendapatkan angka 6 pada dadu akan memberikan pemain hak untuk melempar dadu sekali lagi.
- **🎯 Kemenangan Akurat**: Pemain harus mendapatkan angka dadu yang pas untuk mendarat tepat di kotak 100.
- **🔄 Permainan Berkelanjutan**: Setelah seorang pemain menang, server secara otomatis mereset permainan baru setelah jeda 5 detik.

### Teknis & Jaringan
- **⚖️ Arsitektur dengan Load Balancer**: Implementasi *Load Balancer* dengan logika *Pairing* yang mengarahkan setiap pasangan pemain ke *instance* server yang berbeda, memungkinkan skalabilitas horizontal.
- **👑 Server Otoritatif**: Setiap *instance* server game adalah satu-satunya sumber kebenaran (*Single Source of Truth*) untuk sesi permainannya, mencegah kecurangan dari sisi client.
- **🔗 Koneksi TCP Persisten**: Menggunakan Sockets TCP untuk membangun koneksi yang andal antara client dan server game.
- **📝 Protokol Komunikasi JSON**: Semua komunikasi menggunakan format JSON yang terstruktur dan mudah dibaca.
- **⚙️ Server Konkuren dengan Thread Pool**: Setiap *instance* server game menggunakan `concurrent.futures.ThreadPoolExecutor` untuk menangani koneksi dari kliennya secara efisien.
- **🔒 Keamanan Thread (Thread-Safety)**: Mengimplementasikan `threading.Lock` pada operasi kritis di server game dan *load balancer*.

### Pengalaman Pengguna (UX)
- **🎨 Antarmuka Grafis yang Menarik**: Dibangun dengan `Pygame`, menampilkan papan permainan, bidak, dan informasi status permainan secara jelas.
- **💨 Animasi yang Halus**: Animasi pergerakan bidak yang detail dan animasi kocokan dadu memberikan *feedback* visual yang memuaskan.
- **🔊 Efek Suara Imersif**: Dilengkapi dengan efek suara untuk kocokan dadu, pergerakan bidak, dan saat pemain menang.
- **💡 Feedback Giliran yang Jelas**: Bidak pemain yang sedang mendapat giliran akan berdenyut secara visual.
- **🏷️ Personalisasi Nama Pemain**: Pemain dapat memasukkan nama mereka sendiri sebelum permainan dimulai.

## Arsitektur & Pilihan Desain
Proyek ini mengadopsi arsitektur **Client-Server Terdistribusi dengan Load Balancer** sebagai titik masuk utama.

```
                               +-----------------------------+
                               |    Load Balancer (Python)   |
                               |      (Port Utama: 55555)    |
                               | (Logika Matchmaking/Pairing)|
                               +--------------+--------------+
                                              |
     (1. Semua Client Terhubung ke Sini Dulu) |
                 +----------------------------+----------------------------+
                 | (2. Diarahkan secara bergiliran ke server yang tersedia)|
                 |                                                         |
                 ▼                                                         ▼
+-----------------------------+                           +-----------------------------+
| Game Server #1 (Python)     |                           | Game Server #2 (Python)     |
|   (Port Backend: 60001)     |                           |   (Port Backend: 60002)     |
| (Menangani 1 Sesi Game)     |                           | (Menangani 1 Sesi Game)     |
+--------------+--------------+                           +--------------+--------------+
               |                                                         |
 (3. Permainan berlangsung di sini)                             (Permainan berlangsung di sini)
               |                                                         |
      +--------+--------+                                       +--------+--------+
      |                 |                                       |                 |
      ▼                 ▼                                       ▼                 ▼
+-----------+     +-----------+                           +-----------+     +-----------+
| Client A  |     | Client B  |                           | Client C  |     | Client D  |
+-----------+     +-----------+                           +-----------+     +-----------+
 (Bermain di Sesi 1)                                       (Bermain di Sesi 2)


```

#### Pilihan Desain Utama:
> **Mengapa Load Balancer dengan Logika Pairing?** 🤔 Daripada menyeimbangkan beban per koneksi, *load balancer* ini dirancang untuk "memasangkan" dua klien yang masuk secara berurutan dan mengirim mereka ke *instance* server yang sama menggunakan metode *Round Robin*. Ini memastikan bahwa setiap sesi permainan (yang membutuhkan 2 pemain) berjalan dalam lingkungan terisolasi, memungkinkan sistem untuk menangani banyak game secara paralel.

> **Mengapa Server Game Modular?** 🛡️ Arsitektur server dipecah menjadi `server.py` (lapisan jaringan), `game_server.py` (lapisan logika), dan `game_state.py` (lapisan data). Desain ini memungkinkan setiap komponen untuk fokus pada tugasnya masing-masing, memudahkan pengembangan, pengujian, dan pemeliharaan.

#### Tumpukan Teknologi (Technology Stack):
- **Bahasa Pemrograman**: Python 3
- **Library Grafis & Game**: Pygame
- **Jaringan**: Modul `socket` bawaan Python
- **Konkurensi**: Modul `threading` dan `concurrent.futures.ThreadPoolExecutor`

## Protokol Jaringan
Komunikasi antara client dan server mengikuti protokol berbasis JSON yang dikirim per baris (`\n`).

#### Client → Load Balancer
| Langkah | Deskripsi |
| :--- | :--- |
| 1. Connect | Client terhubung ke Load Balancer di port utama (55555). |

#### Load Balancer → Client
| Respons | Deskripsi | Contoh Payload |
| :--- | :--- | :--- |
| Alamat Server | LB mengirim alamat (host, port) dari server game yang ditugaskan. | `{"host": "127.0.0.1", "port": 60001}` |

#### Client → Server Game
| Perintah | Deskripsi |
| :--- | :--- |
| `(string nama)` | Pesan teks mentah pertama setelah terhubung, berisi nama pemain. |
| `{"command": "START_GAME"}`| Dikirim saat pemain menekan spasi untuk memulai game. |
| `{"command": "ROLL_DICE"}` | Dikirim saat pemain menekan spasi pada gilirannya. |


#### Server Game → Client
| Perintah | Deskripsi |
| :--- | :--- |
| `PLAYER_ASSIGNED` | Memberi tahu client nomor pemainnya (1 atau 2). |
| `GAME_UPDATE` | Pesan utama yang berisi seluruh status game terkini. |
| `DICE_RESULT` | Mengirim hasil kocokan dadu untuk memulai animasi di client. |
| `PLAYER_MOVE` | Mengirim jalur pergerakan pion yang detail untuk animasi. |
| `SERVER_FULL`| Dikirim jika client mencoba terhubung saat server sudah penuh. |
| `GAME_ERROR`| Mengirim pesan error (misal: mencoba mulai dengan 1 pemain). |


## Struktur Proyek
```
.
├── assets/                 # 🖼️ Direktori untuk semua aset visual
│   └── ...
├── sounds/                 # 🎵 Direktori untuk semua efek suara
│   └── ...
├── client.py               # 💻 Titik masuk untuk pemain, mengelola UI dan koneksi.
├── server.py               # 🚪 Titik masuk untuk instance server game, mengelola koneksi.
├── game_server.py          # 🧠 Otak dari server, berisi semua logika permainan.
├── game_state.py           # 📝 Struktur data untuk menyimpan state game.
└── load_balancer.py        # ⚖️ Titik masuk utama untuk semua client, mendistribusikan sesi.
```
- **load_balancer.py**: Bertindak sebagai "resepsionis" yang mengarahkan pasangan pemain ke "ruang meeting" (server game) yang tersedia.
- **server.py**: Bertugas sebagai "penjaga pintu" di setiap ruang meeting.
- **game_server.py**: Bertindak sebagai "wasit" di dalam setiap ruang meeting.
- **client.py**: Tampilan dari sisi "tamu" atau pemain.

## Cara Menjalankan
Ikuti langkah-langkah berikut untuk menjalankan game dengan arsitektur load balancer.

#### 1. Prasyarat
Pastikan Anda memiliki Python 3 terpasang dan library Pygame telah diinstal.
```bash
pip install pygame
```

#### 2. Jalankan Beberapa Instance Server Game
Buka terminal **sebanyak jumlah server yang diinginkan** (misalnya 3 terminal). Di setiap terminal, jalankan `server.py` dengan nomor port yang berbeda sesuai konfigurasi di `load_balancer.py`.
```bash
# Di Terminal 1:
python server.py 60001

# Di Terminal 2:
python server.py 60002

# Di Terminal 3:
python server.py 60003
```
Biarkan semua terminal server ini berjalan.

#### 3. Jalankan Load Balancer
Buka terminal **baru** dan jalankan `load_balancer.py`.
```bash
python load_balancer.py
```
Load Balancer sekarang akan berjalan dan siap menerima koneksi dari semua client di port `55555`.

#### 4. Jalankan Client
Buka terminal **baru** untuk setiap pemain.
- **Untuk bermain di komputer yang sama (localhost):**
  Jalankan `client.py` tanpa argumen. Klien akan otomatis terhubung ke Load Balancer.
  ```bash
  python client.py
  ```
- **Untuk bermain di jaringan lokal (LAN):**
  Jalankan `client.py` dengan alamat IP dari komputer yang menjalankan Load Balancer.
  ```bash
  python client.py [IP_LOAD_BALANCER]
  ```
Klien pertama dan kedua akan diarahkan ke Server 1. Klien ketiga dan keempat akan diarahkan ke Server 2, dan seterusnya.

## Tim Kami
Proyek ini dikembangkan dengan penuh semangat oleh:
- **Farrel Akmalazmi Nugraha - 5025221138**
- **[Nama Anggota 2]**

Proyek ini dibuat sebagai bagian dari tugas mata kuliah **Pemrograman Jaringan**.
