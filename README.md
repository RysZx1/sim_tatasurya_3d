# Simulasi Tata Surya 3D Interaktif

Proyek Grafika Komputer untuk memvisualisasikan sistem tata surya menggunakan ruang 3D interaktif. Simulasi ini dibangun dengan bahasa Python, memanfaatkan PyOpenGL untuk komputasi matriks grafis 3D dan Pygame sebagai wadah aplikasi serta pendeteksi input pengguna.

## 🚀 Fitur Utama
* **Visualisasi Realistis:** Menggunakan tekstur permukaan planet dan pantulan cahaya (*Point Light*) dari Matahari yang akurat.
* **Akurasi Hirarki Orbit:** Menerapkan sistem gerakan satelit bertingkat (induk-anak) seperti pada rotasi Bumi dan Bulan.
* **Eksplorasi Tanpa Batas:** Dilengkapi kamera *Free-Look* bergaya FPS untuk kebebasan sudut pandang pengamat dalam ruang 3D, dikelilingi *skybox* bertekstur galaksi resolusi tinggi.
* **Navigasi Interaktif:** Mendukung fitur seleksi objek berbasis *Ray-Casting* untuk memilih planet menggunakan klik mouse, menampilkan informasi dan metrik secara *real-time* di Dasbor/HUD 2D transparan.
* **Kontrol Waktu Dinamis:** Akselerasi (percepat/perlambat) dan jeda rotasi planet secara langsung.

## ⚙️ Persyaratan & Instalasi

1. Pastikan Python 3.x sudah terpasang.
2. *Clone repository* ini ke komputer lokal.
3. Instal pustaka yang dibutuhkan menggunakan perintah:
   ```bash
   pip install -r requirements.txt


1. Masuk ke folder penyimpanan kode (src), lalu    jalankan program utamanya
cd src
python main.py

⌨️ Panduan Kontrol
W / A / S / D : Navigasi gerakan kamera (Maju, Kiri, Mundur, Kanan)
Q / E : Turun / Naik posisi kamera
Geser Mouse : Mengarahkan pandangan kamera (Free-Look)
Geser Mouse : Mengarahkan pandangan kamera (Free-Look)
P : Jeda / Lanjutkan rotasi planet (Pause / Play)
L : Hidupkan / Matikan efek pencahayaan (Lighting)
O : Tampilkan / Sembunyikan garis jalur orbit
Panah Atas (↑) : Mempercepat laju kecepatan orbit simulasi
Panah Bawah (↓) : Memperlambat laju kecepatan orbit simulasi
ESC : Keluar dari aplikasi