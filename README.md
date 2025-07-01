# 🐍 Snake and Ladder Multiplayer (HTTP Edition) 🎲

![Python](https://img.shields.io/badge/python-3.11+-blue.svg) ![Pygame](https://img.shields.io/badge/pygame-2.5+-green.svg) ![Architecture](https://img.shields.io/badge/architecture-Stateful%20Monolithic-blue.svg)

Proyek ini merupakan implementasi teknis dari permainan Ular Tangga yang dikembangkan untuk memenuhi tugas mata kuliah Pemrograman Jaringan. Proyek ini berevolusi dari basis kode server HTTP sederhana dan mengubahnya menjadi sebuah **Game Server Multiplayer** yang fungsional, konkuren, dan *stateful*.

## Anggota Kelompok
|  Nama 	|  NRP 	|
|---	|---	|
|  Bintang Wibi Hanoraga 	|  5025221034 	|
|  Davin Fisabilillah Reynard Putra 	|  5025221137 	|
|  Farrel Akmalazmi Nugraha 	|   5025221138	|
|  Faiq Lidan Baihaqi 	|  5025221294 	|
|  Alendra Rafif Athaillah 	|  5025221297 |

## Tangkapan Layar (Screenshots)
Berikut ini adalah dua screenshot saat sedang bermain Snake and Ladder, dari dua client yang berbeda yang terhubung ke sistem server yang sama.
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

## Tentang Proyek
Proyek Ular Tangga Multiplayer ini adalah implementasi penuh dari game klasik yang dibangun dengan memodifikasi sebuah server HTTP dasar. Berbeda dari pendekatan koneksi TCP persisten, proyek ini menggunakan **protokol HTTP** untuk semua komunikasi, di mana setiap aksi pemain adalah sebuah permintaan HTTP yang independen. Arsitektur yang digunakan adalah **server monolitik yang stateful**, di mana semua status permainan disimpan langsung di dalam memori server, memungkinkan sistem untuk menangani banyak sesi permainan secara paralel dalam satu proses yang efisien.

## Fitur Unggulan
Proyek ini dirancang dengan berbagai fitur untuk menciptakan pengalaman bermain yang lengkap dan stabil.

### Gameplay
- **🧑‍🤝‍🧑 Multiplayer untuk 2 Pemain**: Didesain khusus untuk dua pemain yang dapat saling menemukan dan bermain bersama secara otomatis.
- **📜 Aturan Permainan Klasik**: Mengimplementasikan papan 10x10 dengan aturan ular (turun) dan tangga (naik).
- **⚖️ Sistem Giliran (Turn-Based) yang Adil**: State giliran yang terpusat di memori server memastikan tidak ada tumpang tindih giliran.
- **🎲 Giliran Ekstra**: Mendapatkan angka 6 pada dadu akan memberikan pemain hak untuk melempar dadu sekali lagi.
- **🎯 Kemenangan Akurat**: Pemain harus mendapatkan angka dadu yang pas untuk mendarat tepat di kotak 100.
- **🔄 Permainan Berkelanjutan**: Setelah permainan selesai, pemain dapat langsung memulai ronde baru dengan menekan spasi.

### Teknis & Jaringan
- **⚙️ Server Stateful dengan State di Memori**: Semua state permainan disimpan dalam sebuah *global variable* di server. Akses ke state ini diamankan menggunakan `threading.RLock` untuk mencegah *race condition* dan *deadlock*.
- **🌐 Komunikasi Berbasis HTTP**: Seluruh komunikasi antara klien dan server menggunakan protokol HTTP, sesuai dengan instruksi tugas untuk memodifikasi server HTTP.
- **🔄 Polling Asinkron**: Klien menggunakan *polling* di *thread* terpisah untuk mendapatkan update status game, menghasilkan animasi yang mulus tanpa membekukan UI.
- **🚀 Server Konkuren dengan Thread Pool**: Server menggunakan `concurrent.futures.ThreadPoolExecutor` untuk menangani banyak permintaan HTTP secara efisien dan simultan dalam satu proses.

### Pengalaman Pengguna (UX)
- **🎨 Antarmuka Grafis yang Menarik**: Dibangun dengan `Pygame`, menampilkan papan, bidak, dan informasi status permainan secara jelas.
- **💨 Animasi Sinkron**: Animasi kocokan dadu dan pergerakan bidak disinkronkan antar klien untuk memberikan pengalaman visual yang konsisten.
- **🔊 Efek Suara Imersif**: Dilengkapi dengan efek suara untuk kocokan dadu, pergerakan bidak, dan saat pemain menang.
- **💡 Feedback Giliran yang Jelas**: Lingkaran berwarna di sekitar indikator giliran menandakan siapa yang sedang aktif.
- **🏷️ Personalisasi Nama Pemain**: Pemain dapat memasukkan nama mereka, yang akan ditampilkan di judul jendela aplikasi.

## Arsitektur & Pilihan Desain
Proyek ini mengadopsi arsitektur **Server Monolitik yang Stateful dan Konkuren**.

```
                 +---------------------------------+
                 |   Server Game Tunggal (Python)  |
                 |      (Port TCP: 8000)           |
                 |---------------------------------|
                 |  - ThreadPoolExecutor (Konkuren)|
                 |  - Logika Game (Ular Tangga)    |
                 |  - State Management (Global Var)|
                 |    (Dilindungi oleh RLock)      |
                 +-----------------+---------------+
                                   ^
                                   | (Permintaan HTTP GET)
                                   |
                +------------------+------------------+
                |                                     |
                ▼                                     ▼
      +-----------------+                   +-----------------+
      |   Klien 1       |                   |   Klien 2       |
      |   (Pygame)      |                   |   (Pygame)      |
      +-----------------+                   +-----------------+
```

#### Pilihan Desain Utama:
> **Mengapa Arsitektur Stateful dengan Global Variable?** 🤔 Sesuai dengan arahan, arsitektur diubah dari model terdistribusi menjadi model monolitik. Semua *state* permainan disimpan dalam sebuah *global variable* di dalam memori server. Pilihan ini menyederhanakan arsitektur secara signifikan karena tidak lagi memerlukan database eksternal. Untuk memastikan keamanan data dalam lingkungan *multithreaded*, akses ke *global variable* ini dilindungi menggunakan `threading.RLock` untuk mencegah *race condition* dan *deadlock*.

> **Mengapa Komunikasi via HTTP?** 🛡️ Sesuai dengan instruksi tugas, seluruh sistem ini dibangun di atas basis kode server HTTP. Kami memperluasnya untuk menangani protokol game kami sendiri yang disematkan dalam permintaan `GET`. Klien melakukan *polling* untuk mendapatkan *update*, mensimulasikan komunikasi dua arah di atas protokol *request-response* HTTP.

#### Tumpukan Teknologi (Technology Stack):
- **Bahasa Pemrograman**: Python 3
- **Library Grafis & Game**: Pygame
- **Server Logic**: Modifikasi dari `http.server`
- **Jaringan**: Modul `socket` bawaan Python
- **Konkurensi**: Modul `threading` dan `concurrent.futures.ThreadPoolExecutor`

## Protokol Jaringan
Komunikasi antara klien dan server menggunakan protokol HTTP/1.1 melalui metode `GET`. Perintah dan data dikirimkan sebagai *query parameters*. Server merespons dengan format JSON.

| Perintah | Deskripsi | Contoh URL |
| :--- | :--- | :--- |
| `FIND_OR_CREATE_GAME` | Mencari game yang menunggu pemain. Jika ada, bergabung. Jika tidak, membuat game baru. | `/game?command=FIND_OR_CREATE_GAME&name=Farrel`|
| `GET_STATE` | Mengambil status permainan terbaru untuk sinkronisasi. | `/game?command=GET_STATE&game_id=game_123abc` |
| `START_GAME` | Memulai/memulai ulang permainan. | `/game?command=START_GAME&game_id=game_123abc` |
| `ROLL_DICE` | Melempar dadu untuk pemain yang sedang giliran. | `/game?command=ROLL_DICE&game_id=game_123abc&player_num=1` |

## Struktur Proyek
```
.
├── assets/                  # 🖼️ Direktori untuk semua aset visual
│   └── ...
├── sounds/                  # 🎵 Direktori untuk semua efek suara
│   └── ...
├── client.py                # 💻 Titik masuk untuk pemain, mengelola UI dan request.
├── game_http_server.py      # 🧠 Otak server, berisi logika HTTP, game, dan state management.
└── server_thread_pool_http.py # 🚀 Peluncur untuk Server Game Tunggal.
```

## Cara Menjalankan
Ikuti langkah-langkah berikut untuk menjalankan keseluruhan sistem.

#### 1. Prasyarat
- Python 3 terpasang.
- Library Python yang dibutuhkan:
  ```bash
  pip install pygame
  ```

#### 2. Menjalankan di Satu Komputer (Lokal)
1.  **Jalankan Server**: Buka satu jendela Terminal, lalu jalankan perintah:
    ```bash
    python server_thread_pool_http.py
    ```
    Server akan berjalan di port `8000`. Biarkan terminal ini tetap berjalan.

2.  **Jalankan Klien**: Buka terminal baru untuk setiap pemain (misalnya, buka dua terminal baru untuk dua pemain). Di setiap terminal klien, jalankan perintah:
    ```bash
    python client.py
    ```
    Klien pertama akan membuat game baru, dan klien kedua akan otomatis menemukan dan bergabung ke game tersebut.

---

### **Opsional: Bermain di Jaringan Lokal (Beda Komputer)**

Untuk bermain dengan teman di jaringan WiFi atau LAN yang sama, ikuti langkah tambahan ini.

1.  **Cari Alamat IP Komputer Server**
    Di komputer yang menjalankan server, cari alamat IP lokalnya.
    - **Di Windows**: Buka `Command Prompt` dan ketik `ipconfig`. Cari alamat `IPv4` (contoh: `192.168.1.5`).
    - **Di macOS/Linux**: Buka `Terminal` dan ketik `ifconfig` atau `ip addr`.

2.  **Jalankan Server**
    Jalankan server di komputer utama seperti pada langkah di atas.

3.  **Ubah Alamat di Kode Klien**
    Di komputer lain yang akan menjadi klien, buka file `client.py` dengan editor teks. Ubah alamat IP di baris paling atas. Ganti `'127.0.0.1'` dengan alamat IP komputer server yang sudah Anda temukan.
    ```python
    # Ganti '127.0.0.1' dengan IP komputer server Anda
    SERVER_ADDRESS = ('192.168.1.5', 8000)
    ```

4.  **Jalankan Klien**
    Sekarang, jalankan `python client.py` di komputer klien. Klien tersebut akan terhubung ke komputer server melalui jaringan.

> **Penting! Catatan Firewall**: Pastikan *Windows Firewall* atau *antivirus* di **komputer server** mengizinkan koneksi masuk pada port `8000` agar klien dari komputer lain dapat terhubung.

---

Proyek ini dibuat sebagai bagian dari tugas mata kuliah **Pemrograman Jaringan**.
