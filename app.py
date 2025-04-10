import time
import random
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "zamzama"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/produk')
def produk():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produk")
    produk_list = cursor.fetchall()  # Ambil semua produk
    conn.close()

    # Ubah produk_list menjadi list of dictionaries untuk memudahkan akses di template
    produk_dict_list = []
    for produk in produk_list:
        produk_dict_list.append({
            'id': produk[0],
            'nama': produk[1],
            'deskripsi': produk[2],
            'harga': produk[3],
            'gambar': produk[4]
        })

    return render_template('produk.html', produk_list=produk_dict_list)

# Route Login
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        if username == "admin" and check_password_hash(generate_password_hash("zamzama"), password):
            session['admin'] = True
            flash("Login berhasil!", "success")
            return redirect(url_for("produk"))
        else:
            flash("Login gagal!", "danger")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('admin', None)
    flash("Anda telah logout.", "info")
    return redirect(url_for("home"))

# Konversi URL gambar dari Google Drive
def convert_img_url(url):
    if "drive.google.com" in url:
        match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
        if match:
            return f"https://drive.google.com/uc?id={match.group(1)}"
    return url

app.jinja_env.globals.update(convert_img_url=convert_img_url)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # Agar hasil query menjadi dictionary
    return conn
@app.route('/tambah', methods=['GET', 'POST'])
def tambah_produk():
    if request.method == 'POST':
        nama = request.form['nama']
        deskripsi = request.form['deskripsi']
        harga = int(request.form['harga'])  # Mengonversi input harga menjadi integer
        gambar = request.form['gambar']  # URL gambar dari input text

        # Simpan data ke database (termasuk URL gambar, tanpa file produk)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO produk (nama, deskripsi, harga, gambar) VALUES (?, ?, ?, ?)",
                       (nama, deskripsi, harga, gambar))
        conn.commit()
        conn.close()

        flash("Produk berhasil ditambahkan!", "success")
        return redirect(url_for('produk'))

    return render_template('tambah.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_produk(id):
    if 'admin' not in session:
        flash("Silakan login!", "warning")
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        nama = request.form['nama']
        deskripsi = request.form['deskripsi']
        harga = request.form['harga']
        gambar = request.form['gambar']

        cursor.execute("UPDATE produk SET nama=?, deskripsi=?, harga=?, gambar=? WHERE id=?",
                       (nama, deskripsi, harga, gambar, id))
        conn.commit()
        conn.close()

        flash("Produk berhasil diperbarui!", "success")
        return redirect(url_for('produk'))

    cursor.execute("SELECT * FROM produk WHERE id=?", (id,))
    produk_row = cursor.fetchone()
    conn.close()

    if not produk_row:
        flash("Produk tidak ditemukan!", "danger")
        return redirect(url_for("produk"))

    produk = dict(produk_row)
    return render_template('edit.html', produk=produk)

# Route untuk hapus produk
@app.route('/hapus/<int:id>')
def hapus_produk(id):
    if 'admin' not in session:
        flash("Silakan login!", "warning")
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produk WHERE id=?", (id,))
    conn.commit()
    conn.close()

    flash("Produk berhasil dihapus!", "success")
    return redirect(url_for('produk'))

def get_produk_by_id(id):
    conn = sqlite3.connect('database.db')  # Koneksi ke database
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM produk WHERE id = ?", (id,))
    produk = cursor.fetchone()  # Ambil hasil query pertama
    conn.close()  # Tutup koneksi

    if produk:
        return {
            'id': produk[0],
            'nama': produk[1],
            'deskripsi': produk[2],
            'harga': produk[3],
            'gambar': produk[4]
        }
    return None


if __name__ == '__main__':
    app.run(debug=True)
