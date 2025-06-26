# 🐍 Snake & Ladder Online: Multiplayer

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Pygame](https://img.shields.io/badge/pygame-2.6.1-green.svg)

Selamat datang di Snake & Ladder Online, sebuah implementasi game Ular Tangga klasik yang dibangun kembali dengan arsitektur client-server modern. Proyek ini didesain sebagai tugas akhir mata kuliah Pemrograman Jaringan, yang mendemonstrasikan komunikasi jaringan real-time, penanganan koneksi konkuren, dan desain perangkat lunak yang modular.

## Daftar Isi
- [Fitur Unggulan](#fitur-unggulan)
- [Arsitektur Proyek](#arsitektur-proyek)
- [Tumpukan Teknologi (Technology Stack)](#tumpukan-teknologi-technology-stack)
- [Struktur File Proyek](#struktur-file-proyek)
- [Instalasi & Pengaturan](#instalasi--pengaturan)
- [Cara Bermain](#cara-bermain)
- [Protokol Komunikasi](#protokol-komunikasi)
- [Tim Pengembang](#tim-pengembang)

## Fitur Unggulan
- **Lobi & Nama Pemain**: Pemain dapat memasukkan nama mereka sebelum bergabung ke dalam permainan.
- **Server Otoritatif**: Seluruh logika dan aturan permainan (kocokan dadu, validasi gerakan, penentuan pemenang) 100% dikelola oleh server, mencegah kecurangan dari sisi klien.
- **Real-time Multiplayer**: Mendukung dua pemain secara bersamaan dalam satu sesi permainan melalui jaringan lokal (LAN/WiFi).
- **Animasi yang Hidup**:
    - **Animasi Kocokan Dadu**: Dadu berputar secara visual sebelum menunjukkan hasil akhir.
    - **Animasi Gerakan Pion**: Pion bergerak secara mulus dari satu kotak ke kotak lainnya.
    - **Indikator Giliran**: Pion pemain yang sedang mendapat giliran akan beranimasi (pulsing) untuk memberikan isyarat visual yang jelas.
- **Efek Suara**: Dilengkapi dengan efek suara untuk kocokan dadu, gerakan pion, dan saat terkena ular untuk pengalaman yang lebih imersif.
- **Penanganan Koneksi yang Tangguh**: Server menggunakan *ThreadPool* untuk menangani setiap klien secara terpisah, memastikan server tetap responsif. Server juga dapat menangani klien yang masuk dan keluar di tengah permainan.
- **Siklus Permainan Otomatis**: Setelah seorang pemenang ditentukan, server akan secara otomatis mereset permainan setelah jeda beberapa detik, memungkinkan sesi baru untuk dimulai tanpa perlu me-restart server.

## Arsitektur Proyek
Proyek ini mengadopsi arsitektur **Client-Server** dengan desain server yang modular untuk memisahkan tanggung jawab (*Separation of Concerns*).

```
+------------------+                    +--------------------------------+
|   Client 1       |  <-- JSON over --> |         Network Layer          |
|  (client.py)     |      TCP/IP       |          (server.py)           |
+------------------+                    | (Socket, ThreadPoolExecutor)   |
                                        +----------------|---------------+
+------------------+                    +----------------v---------------+
|   Client 2       |  <-- JSON over --> |        Game Logic Layer        |
|  (client.py)     |      TCP/IP       |       (game_server.py)         |
+------------------+                    +----------------|---------------+
                                        +----------------v---------------+
                                        |          Data State Layer      |
                                        |         (game_state.py)        |
                                        +--------------------------------+
```

- **Data State Layer (`game_state.py`)**: Bertindak sebagai *single source of truth*. Kelas ini hanya menyimpan data mentah kondisi permainan (posisi, giliran, pemenang) tanpa logika apa pun.
- **Game Logic Layer (`game_server.py`)**: Otak dari permainan. Kelas ini mengimplementasikan semua aturan, memproses perintah dari klien, dan memodifikasi `GameState`.
- **Network Layer (`server.py`)**: Pintu gerbang utama. File ini bertugas mendengarkan koneksi masuk, mengelola *thread pool*, dan meneruskan komunikasi antara klien dan *Game Logic Layer*.
- **Client (`client.py`)**: Bertindak sebagai lapisan presentasi (*view*). Klien sepenuhnya "bodoh"; ia hanya merender kondisi permainan yang diterima dari server dan mengirim input pengguna.

## Tumpukan Teknologi (Technology Stack)
- **Bahasa Pemrograman**: Python 3
- **Library Utama**:
    - **`pygame`**: Untuk membangun seluruh antarmuka grafis (GUI), menangani aset visual, audio, dan input pengguna.
    - **`socket`**: Untuk komunikasi jaringan tingkat rendah berbasis protokol TCP/IP.
    - **`threading` & `concurrent.futures`**: Untuk mengimplementasikan *ThreadPoolExecutor* di sisi server, memungkinkan penanganan klien secara konkuren.
    - **`json`**: Untuk serialisasi dan deserialisasi data yang dikirimkan antara klien dan server, memastikan format pesan yang terstruktur.
    - **`time`**: Digunakan untuk mengatur jeda antar pesan di server, memberikan waktu bagi klien untuk menjalankan animasi.

## Struktur File Proyek
```
.
├── assets/
│   ├── board.png
│   ├── dice1.png ... dice6.png
│   ├── pawn_blue.png
│   └── pawn_pink.png
├── sounds/
│   ├── dice_roll.wav
│   ├── pawn_move.wav
│   └── snake_slide.wav
├── client.py
├── server.py
├── game_server.py
├── game_state.py
└── README.md
```

## Instalasi & Pengaturan
Pastikan Anda memiliki Python 3 dan `pip` terinstal di sistem Anda.

1.  **Kloning Repositori**
    ```bash
    git clone [URL_REPOSITORI_GITHUB_ANDA]
    cd [NAMA_FOLDER_PROYEK]
    ```

2.  **Instalasi Dependensi**
    Proyek ini hanya membutuhkan `pygame`. Instal dengan perintah:
    ```bash
    pip install pygame
    ```

## Cara Bermain
Permainan ini dirancang untuk dua pemain di jaringan lokal. Anda memerlukan setidaknya dua terminal atau command prompt.

1.  **Jalankan Server**
    Buka terminal pertama dan jalankan server. Server akan berjalan dan menunggu koneksi.
    ```bash
    python server.py
    ```

2.  **Jalankan Klien Pemain 1**
    Buka terminal kedua. Jika menjalankan di komputer yang sama dengan server, cukup jalankan:
    ```bash
    python client.py
    ```
    Jika di komputer berbeda, sertakan IP Privat dari komputer server:
    ```bash
    python client.py [IP_SERVER]
    ```
    Masukkan nama Anda dan tekan ENTER.

3.  **Jalankan Klien Pemain 2**
    Buka terminal ketiga dan ulangi langkah klien di atas.

4.  **Mulai Bermain**
    - Setelah kedua pemain terhubung, salah satu pemain dapat menekan `SPACE` untuk memulai permainan.
    - Tekan `SPACE` pada giliran Anda untuk mengocok dadu.

## Protokol Komunikasi
Komunikasi antara client dan server menggunakan format JSON yang dikirim per baris (`\n`).

### Pesan dari Klien ke Server
| Perintah | Deskripsi | Contoh Payload |
| :--- | :--- | :--- |
| `[Nama Pemain]` | Dikirim sekali saat terhubung untuk mendaftarkan nama. | `Farrel\n` |
| `START_GAME` | Dikirim saat pemain menekan spasi sebelum game aktif. | `{"command": "START_GAME"}` |
| `ROLL_DICE` | Dikirim saat pemain menekan spasi pada gilirannya. | `{"command": "ROLL_DICE"}` |

### Pesan dari Server ke Klien
| Perintah | Deskripsi | Contoh Payload |
| :--- | :--- | :--- |
| `PLAYER_ASSIGNED` | Memberi tahu klien nomor pemainnya (1 atau 2). | `{"command": "PLAYER_ASSIGNED", "player_num": 1}` |
| `SERVER_FULL` | Diberikan jika klien mencoba terhubung saat sudah ada 2 pemain. | `{"command": "SERVER_FULL"}` |
| `DICE_RESULT` | Mengirim hasil kocokan dadu agar klien bisa memulai animasi. | `{"command": "DICE_RESULT", "dice": 6}` |
| `PLAYER_MOVE` | Mengirim jalur pergerakan pion setelah jeda animasi dadu. | `{"command": "PLAYER_MOVE", "player": 1, "path": [...]}` |
| `GAME_UPDATE` | Mengirim update lengkap kondisi permainan. | `{"command": "GAME_UPDATE", "p1_pos": 5, ...}` |

## Tim Pengembang
| Nama Anggota | NPM / NIM | Tugas Utama |
| :--- | :--- | :--- |
| **[Nama Lengkap Anda]** | [NPM/NIM Anda] | [Contoh: Full-Stack Development, Arsitektur, Dokumentasi] |
| **[Nama Anggota 2]** | [NPM/NIM Anggota 2] | [Tugasnya...] |
