# 🐍 Snake and Ladder Multiplayer (HTTP Edition) 🎲

![Python](https://img.shields.io/badge/python-3.11+-blue.svg) ![Pygame](https://img.shields.io/badge/pygame-2.5+-green.svg) ![Architecture](https://img.shields.io/badge/architecture-Load%20Balanced%20%26%20Stateless-orange.svg) ![Database](https://img.shields.io/badge/database-Azure%20Redis-red.svg)

Proyek ini merupakan implementasi teknis dari permainan Ular Tangga yang dikembangkan untuk memenuhi tugas mata kuliah Pemrograman Jaringan (C). Proyek ini berevolusi dari basis kode server HTTP sederhana dan mengubahnya menjadi sebuah **Game Server Multiplayer** yang fungsional. Fokus utama dari proyek ini adalah mendemonstrasikan arsitektur jaringan modern yang skalabel dan *stateless*, menggunakan **Load Balancer** untuk distribusi permintaan, dan **database terpusat (Azure Cache for Redis)** untuk manajemen *state*, yang memungkinkan banyak sesi permainan berjalan secara simultan.

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
- [Tim Kami](#tim-kami)

## Tentang Proyek
Proyek Ular Tangga Multiplayer ini adalah implementasi penuh dari game klasik, namun dibangun di atas arsitektur web modern yang *stateless*. Berbeda dari pendekatan koneksi TCP persisten, proyek ini menggunakan **protokol HTTP** untuk semua komunikasi, di mana setiap aksi pemain adalah sebuah permintaan HTTP yang independen. Arsitektur ini menggunakan **Load Balancer** untuk mendistribusikan permintaan ke beberapa *instance* **server backend yang stateless**. Semua status permainan disimpan dalam **database terpusat (Azure Cache for Redis)**, memastikan konsistensi data dan memungkinkan sistem untuk menangani banyak game secara paralel dengan cara yang tangguh dan skalabel.

## Fitur Unggulan
Proyek ini dirancang dengan berbagai fitur untuk menciptakan pengalaman bermain yang lengkap, modern, dan stabil.

### Gameplay
- **🧑‍🤝‍🧑 Multiplayer untuk 2 Pemain**: Didesain khusus untuk dua pemain yang dapat saling menemukan dan bermain bersama secara otomatis.
- **📜 Aturan Permainan Klasik**: Mengimplementasikan papan 10x10 dengan aturan ular (turun) dan tangga (naik).
- **⚖️ Sistem Giliran (Turn-Based) yang Adil**: State giliran yang terpusat di Redis memastikan tidak ada tumpang tindih giliran.
- **🎲 Giliran Ekstra**: Mendapatkan angka 6 pada dadu akan memberikan pemain hak untuk melempar dadu sekali lagi.
- **🎯 Kemenangan Akurat**: Pemain harus mendapatkan angka dadu yang pas untuk mendarat tepat di kotak 100.
- **🔄 Permainan Berkelanjutan**: Setelah permainan selesai, pemain dapat langsung memulai ronde baru dengan menekan spasi.

### Teknis & Jaringan
- **⚖️ Arsitektur Load Balancer**: Implementasi *Load Balancer* dengan strategi *Round-Robin* yang mendistribusikan beban permintaan HTTP secara merata ke semua *instance* server backend.
- **☁️ State Terpusat dengan Redis**: Semua *state* permainan disimpan di **Azure Cache for Redis**, memungkinkan server backend bersifat *stateless* dan skalabel.
- **🌐 Komunikasi Berbasis HTTP**: Seluruh komunikasi antara klien dan server menggunakan protokol HTTP, sesuai dengan instruksi tugas untuk memodifikasi server HTTP.
- **🔄 Polling Asinkron**: Klien menggunakan *polling* di *thread* terpisah untuk mendapatkan update status game, menghasilkan animasi yang mulus tanpa membekukan UI.
- **⚙️ Server Konkuren dengan Thread Pool**: Setiap *instance* server backend menggunakan `concurrent.futures.ThreadPoolExecutor` untuk menangani banyak permintaan HTTP secara efisien dan simultan.

### Pengalaman Pengguna (UX)
- **🎨 Antarmuka Grafis yang Menarik**: Dibangun dengan `Pygame`, menampilkan papan, bidak, dan informasi status permainan secara jelas.
- **💨 Animasi Sinkron**: Animasi kocokan dadu dan pergerakan bidak disinkronkan antar klien untuk memberikan pengalaman visual yang konsisten.
- **🔊 Efek Suara Imersif**: Dilengkapi dengan efek suara untuk kocokan dadu, pergerakan bidak, dan saat pemain menang.
- **💡 Feedback Giliran yang Jelas**: Lingkaran berwarna di sekitar indikator giliran menandakan siapa yang sedang aktif.
- **🏷️ Personalisasi Nama Pemain**: Pemain dapat memasukkan nama mereka, yang akan ditampilkan di judul jendela aplikasi.

## Arsitektur & Pilihan Desain
Proyek ini mengadopsi arsitektur **Stateless Terdistribusi dengan Load Balancer dan Database Terpusat**.

```
                         (1. Semua klien mengirim request HTTP ke sini)
                                             |
                                             ▼
                              +-----------------------------+
                              |    Load Balancer (Python)   |
                              |     (Port Utama: 55555)     |
                              | (Distribusi Round-Robin)    |
                              +--------------+--------------+
                                             | (2. Request diteruskan ke salah satu server)
                 +---------------------------+---------------------------+
                 |                           |                           |
                 ▼                           ▼                           ▼
  +-------------------------+   +-------------------------+   +-------------------------+
  | Server Backend #1 (8001)|   | Server Backend #2 (8002)|   | Server Backend #3 (8003)|
  | (Stateless, Python HTTP)|   | (Stateless, Python HTTP)|   | (Stateless, Python HTTP)|
  +-------------------------+   +-------------------------+   +-------------------------+
                 | (3. Semua server terhubung ke sumber data yang sama)  |
                 +---------------------------+---------------------------+
                                             |
                                             ▼
                                +---------------------------+
                                |  Azure Cache for Redis    |
                                | (Database State Terpusat) |
                                +---------------------------+

```

#### Pilihan Desain Utama:
> **Mengapa Arsitektur Stateless dengan Redis?** 🤔 Daripada menyimpan *state* di memori setiap server (yang akan menyulitkan *load balancing*), kami memusatkan semua *state* permainan di Redis. Ini memungkinkan server kami bersifat *stateless*—artinya, permintaan apa pun dari klien mana pun dapat dilayani oleh server mana pun tanpa kehilangan konteks. Desain ini secara fundamental lebih skalabel, tangguh, dan sejalan dengan praktik arsitektur web modern.

> **Mengapa Komunikasi via HTTP?** 🛡️ Sesuai dengan instruksi tugas, seluruh sistem ini dibangun di atas basis kode server HTTP. Kami memperluasnya untuk menangani protokol game kami sendiri yang disematkan dalam permintaan `GET`. Klien melakukan *polling* untuk mendapatkan *update*, mensimulasikan komunikasi dua arah di atas protokol *request-response* HTTP.

#### Tumpukan Teknologi (Technology Stack):
- **Bahasa Pemrograman**: Python 3
- **Library Grafis & Game**: Pygame
- **Server Logic**: Modifikasi dari `http.server`
- **Jaringan**: Modul `socket` bawaan Python
- **Database State**: Azure Cache for Redis
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
├── assets/                  # 🖼️ Direktori untuk semua aset visual
│   └── ...
├── sounds/                  # 🎵 Direktori untuk semua efek suara
│   └── ...
├── client.py                # 💻 Titik masuk untuk pemain, mengelola UI dan request.
├── game_http_server.py      # 🧠 Otak server, berisi logika HTTP, game, dan Redis.
├── load_balancer.py         # ⚖️ Titik masuk utama untuk semua client.
└── server_thread_pool_http.py # 🚀 Peluncur untuk instance server backend.
```

## Cara Menjalankan
Ikuti langkah-langkah berikut untuk menjalankan keseluruhan sistem.

#### 1. Prasyarat
- Python 3 terpasang.
- Membuat resource **Azure Cache for Redis** dan mendapatkan kredensialnya.
- Library Python yang dibutuhkan:
  ```bash
  pip install pygame redis python-dotenv
  ```

#### 2. Konfigurasi Kredensial
Sebelum menjalankan, buat file bernama `.env` di direktori utama proyek. Isi file tersebut dengan kredensial Azure Cache for Redis Anda seperti contoh berikut:
```env
REDIS_HOST=nama-host-redis-anda.redis.cache.windows.net
REDIS_PASSWORD=kunci-akses-redis-anda
```
Pastikan file `.env` sudah ada di dalam `.gitignore` agar tidak terunggah ke repositori.

#### 3. Jalankan Server Backend
Buka **3 jendela Terminal** terpisah. Di setiap terminal, jalankan perintah berikut, ganti port untuk masing-masing. Gunakan flag `-u` untuk memastikan log tampil secara *real-time*.
```bash
# Di Terminal 1:
python -u server_thread_pool_http.py 8001

# Di Terminal 2:
python -u server_thread_pool_http.py 8002

# Di Terminal 3:
python -u server_thread_pool_http.py 8003
```

#### 4. Jalankan Load Balancer
Buka **Terminal ke-4**. Pastikan ketiga server backend sudah berjalan.
```bash
python load_balancer.py
```
Load Balancer akan berjalan dan siap menerima koneksi dari semua client di port `55555`.

#### 5. Jalankan Client (Di Komputer yang Sama)
Buka **terminal baru** untuk setiap pemain dan jalankan perintah berikut. Klien akan otomatis terhubung ke Load Balancer yang berjalan di `127.0.0.1`.
```bash
python client.py
```
Jalankan perintah ini di satu terminal untuk pemain pertama, dan di terminal lain untuk pemain kedua.

---

### **Opsional: Bermain di Jaringan Lokal (Beda Komputer)**

Untuk bermain dengan teman di jaringan WiFi atau LAN yang sama, ikuti langkah tambahan ini setelah menjalankan semua server di satu komputer.

1.  **Cari Alamat IP Komputer Server**
    Di komputer yang menjalankan semua server dan load balancer, cari alamat IP lokalnya.
    - **Di Windows**: Buka `Command Prompt` dan ketik `ipconfig`. Cari alamat `IPv4` (contoh: `192.168.1.5`).
    - **Di macOS/Linux**: Buka `Terminal` dan ketik `ifconfig` atau `ip addr`.

2.  **Ubah Alamat di Kode Klien**
    Di komputer lain yang akan menjadi klien, buka file `client.py` dengan editor teks. Ubah alamat IP di baris paling atas. Ganti `'127.0.0.1'` dengan alamat IP komputer server yang sudah Anda temukan.
    ```python
    # Ganti '127.0.0.1' dengan IP komputer server Anda
    LOAD_BALANCER_ADDRESS = ('192.168.1.5', 55555)
    ```

3.  **Jalankan Klien**
    Sekarang, jalankan `python client.py` di komputer klien. Klien tersebut akan terhubung ke komputer server melalui jaringan.

> **Penting! Catatan Firewall**: Pastikan *Windows Firewall* atau *antivirus* di **komputer server** mengizinkan koneksi masuk pada port `55555`, `8001`, `8002`, dan `8003` agar klien dari komputer lain dapat terhubung.

---

## Tim Kami
- **Farrel Akmalazmi Nugraha - 5025221138**
- **Bintang Wibi Hanoraga - 5025221034**
- **Davin Fisabilillah Reynard Putra - 5025221137**
- **Alendra Rafif Athaillah - 5025221297**
- **Faiq Lidan Baihaqi - 5025221294**

Proyek ini dibuat sebagai bagian dari tugas mata kuliah **Pemrograman Jaringan**.
