# 🐍 Snake and Ladder Multiplayer 🎲

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Pygame](https://img.shields.io/badge/pygame-2.6.1-green.svg)

Proyek ini merupakan implementasi teknis dari permainan Ular Tangga yang dikembangkan untuk memenuhi tugas mata kuliah Pemrograman Jaringan (C). Dengan memanfaatkan kekuatan Python, library Pygame untuk rendering grafis, dan modul Socket untuk komunikasi jaringan, kami berhasil membangun sebuah aplikasi client-server yang fungsional. Fokus utama dari proyek ini adalah mendemonstrasikan arsitektur jaringan yang memungkinkan dua pemain untuk berinteraksi secara real-time dalam satu sesi permainan melalui jaringan lokal (LAN).

## Tangkapan Layar (Screenshots)
*Tempatkan screenshot dari dua jendela klien yang sedang berjalan berdampingan di sini untuk menunjukkan fungsionalitas multiplayer secara langsung.*

<p align="center">
  <img src="URL_SCREENSHOT_CLIENT_1.png" alt="Tampilan Klien 1" width="400"/>
  <img src="URL_SCREENSHOT_CLIENT_2.png" alt="Tampilan Klien 2" width="400"/>
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
Proyek Ular Tangga Multiplayer ini adalah implementasi penuh dari game klasik yang kita semua kenal dan sukai, namun dibawa ke level berikutnya dengan memungkinkan dua pemain untuk bermain bersama dari komputer yang berbeda melalui jaringan lokal (LAN). Dibangun sepenuhnya menggunakan Python, proyek ini memanfaatkan kekuatan library Pygame untuk antarmuka grafis yang interaktif dan modul `socket` bawaan Python untuk membangun komunikasi client-server yang andal dan responsif.

## Fitur Unggulan
Proyek ini dirancang dengan berbagai fitur untuk menciptakan pengalaman bermain yang lengkap, modern, dan stabil.

### Gameplay
- **🧑‍🤝‍🧑 Multiplayer untuk 2 Pemain**: Didesain khusus untuk dua pemain yang terhubung melalui jaringan yang sama.
- **📜 Aturan Permainan Klasik**: Mengimplementasikan papan 10x10 dengan aturan ular (turun) dan tangga (naik) yang sudah dikenal.
- **⚖️ Sistem Giliran (Turn-Based) yang Adil**: Server bertindak sebagai wasit, memastikan giliran pemain berjalan secara teratur dan adil.
- **🎲 Giliran Ekstra**: Mendapatkan angka 6 pada dadu akan memberikan pemain hak untuk melempar dadu sekali lagi.
- **🎯 Kemenangan Akurat**: Pemain harus mendapatkan angka dadu yang pas untuk mendarat tepat di kotak 100.
- **🔄 Permainan Berkelanjutan**: Setelah seorang pemain menang, server secara otomatis akan mereset dan memulai permainan baru setelah jeda 5 detik.

### Teknis & Jaringan
- **👑 Arsitektur Client-Server Otoritatif**: Server adalah satu-satunya sumber kebenaran (*Single Source of Truth*), memvalidasi semua aksi dan mencegah kecurangan dari sisi client.
- **🔗 Koneksi TCP Persisten**: Menggunakan Sockets TCP untuk membangun koneksi yang andal dan menjaga sesi tetap terbuka selama permainan berlangsung.
- **📝 Protokol Komunikasi JSON**: Semua komunikasi antara client dan server menggunakan format JSON yang terstruktur dan mudah dibaca.
- **⚙️ Server Konkuren dengan Thread Pool**: Menggunakan `concurrent.futures.ThreadPoolExecutor` untuk menangani koneksi dari banyak client secara efisien dan stabil.
- **🔒 Keamanan Thread (Thread-Safety)**: Mengimplementasikan `threading.Lock` pada semua operasi kritis di server untuk mencegah *race condition* dan memastikan integritas data *game state*.

### Pengalaman Pengguna (UX)
- **🎨 Antarmuka Grafis yang Menarik**: Dibangun dengan `Pygame`, menampilkan papan permainan, bidak pemain, dan informasi status permainan secara jelas.
- **💨 Animasi yang Halus**: Animasi pergerakan bidak dari kotak ke kotak dan animasi kocokan dadu memberikan *feedback* visual yang memuaskan.
- **🔊 Efek Suara Imersif**: Dilengkapi dengan efek suara untuk kocokan dadu, pergerakan bidak, dan saat pemain memenangkan permainan.
- **💡 Feedback Giliran yang Jelas**: Bidak pemain yang sedang mendapat giliran akan berdenyut secara visual, memudahkan pemain untuk mengetahui kapan giliran mereka tiba.
- **🏷️ Personalisasi Nama Pemain**: Pemain dapat memasukkan nama mereka sendiri sebelum permainan dimulai, yang akan ditampilkan di sepanjang permainan.

## Arsitektur & Pilihan Desain
Proyek ini dibangun di atas arsitektur Client-Server yang modular untuk memisahkan tanggung jawab, meningkatkan keterbacaan kode, dan memudahkan pemeliharaan.

```
+----------------+      +------------------+      +----------------+
|   Client 1     |      |                  |      |   Client 2     |
| (Pygame,       |      |      Server      |      | (Pygame,       |
|  Sockets)      |      | (Sockets,        |      |  Sockets)      |
|                |      |  ThreadPool)     |      |                |
+-------+--------+      +--------+---------+      +--------+-------+
        |                        ^                        |
        |                        |                        |
        +------------------------+------------------------+
                  (Koneksi TCP/IP via LAN/localhost)
                      (Port: 55555, Protokol JSON)
```

#### Pilihan Desain Utama:
> **Mengapa Thread Pool?** 🤔 Dibandingkan membuat satu thread baru untuk setiap client (`threading.Thread`), `ThreadPoolExecutor` lebih efisien dalam mengelola sumber daya. Ia membatasi jumlah thread aktif, mencegah server dari kehabisan memori atau menjadi tidak responsif saat banyak client mencoba terhubung secara bersamaan.

> **Mengapa Server Otoritatif?** 🛡️ Dengan menjadikan server sebagai pengatur utama, logika permainan (misalnya hasil lemparan dadu) tidak dapat dimanipulasi oleh client. Client hanya bertugas mengirim input dan menampilkan hasil, memastikan permainan yang adil untuk semua.

#### Tumpukan Teknologi (Technology Stack):
- **Bahasa Pemrograman**: Python 3
- **Library Grafis & Game**: Pygame
- **Jaringan**: Modul `socket` bawaan Python
- **Konkurensi**: Modul `threading` dan `concurrent.futures.ThreadPoolExecutor`

## Protokol Jaringan
Komunikasi antara client dan server mengikuti protokol berbasis JSON. Setiap pesan JSON dikirim sebagai satu baris dan diakhiri dengan karakter newline (`\n`) sebagai pemisah.

#### Client → Server
| Perintah | Parameter | Deskripsi |
| :--- | :--- | :--- |
| `(string nama)` | - | Pesan teks mentah pertama yang dikirim setelah terhubung, berisi nama pemain. |
| `{"command": "START_GAME"}` | - | Dikirim saat pemain menekan spasi untuk memulai game (jika belum aktif). |
| `{"command": "ROLL_DICE"}` | - | Dikirim saat pemain menekan spasi untuk melempar dadu di gilirannya. |

#### Server → Client
| Perintah | Parameter | Deskripsi |
| :--- | :--- | :--- |
| `PLAYER_ASSIGNED` | `player_num` | Memberitahu client nomor pemain yang diberikan (1 atau 2). |
| `GAME_UPDATE` | `(beragam)` | "Heartbeat" game. Pesan utama yang berisi seluruh status game terkini. |
| `DICE_RESULT` | `dice` | Memberitahu hasil kocokan dadu untuk memulai animasi di client. |
| `SERVER_FULL`| - | Dikirim jika client mencoba terhubung saat server sudah penuh. |
| `GAME_ERROR`| `message` | Mengirim pesan error (misal: mencoba mulai dengan 1 pemain). |

## Struktur Proyek
Proyek ini diorganisir ke dalam beberapa file untuk memastikan pemisahan tanggung jawab yang jelas.
```
.
├── assets/                 # 🖼️ Direktori untuk semua aset visual
│   ├── board.png
│   ├── pawn_blue.png
│   └── ...
├── sounds/                 # 🎵 Direktori untuk semua efek suara
│   ├── dice_roll.wav
│   └── ...
├── client.py               # 💻 Titik masuk untuk pemain, mengelola UI dan koneksi.
├── server.py               # 🚪 Titik masuk untuk server, mengelola koneksi & thread.
├── game_server.py          # 🧠 Otak dari server, berisi semua logika permainan.
└── game_state.py           # 📝 Struktur data untuk menyimpan state game.
```
- **client.py**: Mengurus semua hal yang dilihat dan diinput oleh pemain.
- **server.py**: Bertugas sebagai "penerima tamu" yang menerima koneksi dan mendelegasikannya.
- **game_server.py**: Bertindak sebagai "koki" yang memproses semua perintah dan logika game.
- **game_state.py**: Bertindak sebagai "papan tulis" yang menyimpan data permainan.

## Cara Menjalankan
Ikuti langkah-langkah berikut untuk menjalankan game.

#### 1. Prasyarat
Pastikan Anda memiliki Python 3 terpasang. Kemudian, install library Pygame.
```bash
pip install pygame
```

#### 2. Unduh Aset
Pastikan semua file gambar (`assets/`) dan suara (`sounds/`) berada di direktori yang benar sesuai dengan struktur proyek di atas.

#### 3. Jalankan Server
Buka terminal, navigasi ke direktori proyek, dan jalankan file `server.py`.
```bash
python server.py
```
Server akan berjalan dan siap menerima koneksi di port 55555.

#### 4. Jalankan Client
Buka terminal **baru** untuk setiap pemain.
- **Untuk bermain di komputer yang sama (localhost):**
  Jalankan `client.py` tanpa argumen. Anda akan diminta memasukkan nama.
  ```bash
  python client.py
  ```
- **Untuk bermain di jaringan lokal (LAN):**
  Cari tahu alamat IP dari komputer yang menjalankan server (misalnya: `192.168.1.10`). Jalankan `client.py` dengan alamat IP tersebut sebagai argumen.
  ```bash
  python client.py 192.168.1.10
  ```
Permainan akan dimulai setelah dua pemain terhubung dan salah satunya menekan `SPACE`.

## Tim Kami
Proyek ini dikembangkan dengan penuh semangat oleh:
- **[Farrel Akmalazmi Nugraha]**
- **[Nama Anggota 2]**

Proyek ini dibuat sebagai bagian dari tugas mata kuliah **[Nama Mata Kuliah]** di **[Nama Universitas]**.
