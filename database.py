import sqlite3
import random
import time

# Fungsi untuk membuat database dan tabel
def init_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()

        # Hapus tabel jika sudah ada
        cursor.execute("DROP TABLE IF EXISTS produk")
        cursor.execute("DROP TABLE IF EXISTS otp_verifikasi")

        # Buat tabel produk
        cursor.execute('''
        CREATE TABLE produk (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            deskripsi TEXT NOT NULL,
            harga INTEGER NOT NULL,
            gambar TEXT NOT NULL,
            file TEXT NOT NULL
        )
        ''')

        # Buat tabel OTP verifikasi
        cursor.execute('''
        CREATE TABLE otp_verifikasi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            otp TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            timestamp INTEGER NOT NULL,
            expiry_time INTEGER NOT NULL
        )
        ''')

        # Tambahkan indeks untuk pencarian lebih cepat
        cursor.execute("CREATE INDEX idx_otp_user ON otp_verifikasi (user, otp)")

        # Tambahkan produk contoh
        produk_sample = (
            'ScanPARAM',
            'scanPARAMETER adalah alat berbasis Python yang dirancang untuk membantu pentester dan bug hunter dalam mendeteksi parameter URL.',
            20000,
            'https://i.imgur.com/your-image.jpg',
            'scanPARAM.zip'
        )
        cursor.execute("INSERT INTO produk (nama, deskripsi, harga, gambar, file) VALUES (?, ?, ?, ?, ?)", produk_sample)

        conn.commit()
    return "Database berhasil diinisialisasi."

# Fungsi untuk mengambil produk berdasarkan ID
def get_produk_by_id(id):
    try:
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM produk WHERE id = ?", (id,))
            produk = cursor.fetchone()
            if produk:
                return {
                    'id': produk[0], 'nama': produk[1], 'deskripsi': produk[2],
                    'harga': produk[3], 'gambar': produk[4], 'file': produk[5]
                }
        return None
    except sqlite3.Error as e:
        print(f"Database Error: {e}")
        return None

# Fungsi untuk membuat OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Fungsi untuk menyimpan OTP
def tambah_otp(user):
    try:
        otp = generate_otp()
        timestamp = int(time.time())
        expiry_time = timestamp + 300  # 5 menit

        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO otp_verifikasi (user, otp, timestamp, expiry_time) VALUES (?, ?, ?, ?)",
                        (user, otp, timestamp, expiry_time))
            conn.commit()
        
        print(f"OTP untuk {user}: {otp}")
        return otp
    except sqlite3.Error as e:
        print(f"Database Error: {e}")
        return None

# Fungsi untuk mengecek OTP
def cek_otp(user, otp):
    try:
        current_time = int(time.time())

        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()

            # Hapus OTP kadaluarsa terlebih dahulu
            cursor.execute("DELETE FROM otp_verifikasi WHERE expiry_time < ?", (current_time,))
            conn.commit()

            # Cek OTP yang masih berlaku
            cursor.execute("SELECT id FROM otp_verifikasi WHERE user = ? AND otp = ? AND status = 'pending'", (user, otp))
            hasil = cursor.fetchone()

            if hasil:
                otp_id = hasil[0]
                cursor.execute("UPDATE otp_verifikasi SET status = 'verified' WHERE id = ?", (otp_id,))
                conn.commit()
                return True

        return False
    except sqlite3.Error as e:
        print(f"Database Error: {e}")
        return False

if __name__ == "__main__":
    print(init_db())
