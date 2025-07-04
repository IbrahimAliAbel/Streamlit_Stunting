import streamlit as st
import numpy as np
import pickle
import pandas as pd
import sqlite3
import uuid
import hashlib
from datetime import datetime
import warnings

# Suppress sklearn version warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

# Konfigurasi halaman
st.set_page_config(
    page_title="Prediksi Stunting - Petugas Kesehatan", 
    layout="wide", 
    page_icon="🏥",
    initial_sidebar_state="expanded"
)

# CSS styling yang lebih modern dan user-friendly
st.markdown("""
<style>
    /* Background dan tema utama */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    /* Card styling */
    .main-card {
        background: transparent; 
        padding: 2rem;
        border-radius: 15px;
        box-shadow: none; 
        backdrop-filter: none; 
        border: none; 
        margin: 1rem 0;
    }
    
    /* Header styling */
    .header-container {
        text-align: center;
        padding: 2rem 0;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        margin-bottom: 2rem;
        backdrop-filter: blur(10px);
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        font-size: 1.2rem;
        color: rgba(255, 255, 255, 0.9);
        font-weight: 300;
    }
    
    /* Form styling */
    .form-container {
    background: transparent;
    padding: 2rem;
    border-radius: 15px;
    box-shadow: none;
    margin: 1rem 0;
    backdrop-filter: none;
    border: none;
}
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Alert styling */
    .stSuccess > div {
        background: linear-gradient(45deg, #56ab2f, #a8e6cf);
        color: white;
        border-radius: 10px;
        padding: 1.5rem;
        border: none;
    }
    
    .stError > div {
        background: linear-gradient(45deg, #ff416c, #ff4b2b);
        color: white;
        border-radius: 10px;
        padding: 1.5rem;
        border: none;
    }
    
    .stWarning > div {
        background: linear-gradient(45deg, #f7971e, #ffd200);
        color: #333;
        border-radius: 10px;
        padding: 1.5rem;
        border: none;
    }
    
    .stInfo > div {
        background: linear-gradient(45deg, #2196F3, #21CBF3);
        color: white;
        border-radius: 10px;
        padding: 1.5rem;
        border: none;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
    }
    
    /* Input field styling */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 0.75rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #667eea;
        box-shadow: 0 0 10px rgba(102, 126, 234, 0.3);
    }
    
    /* User info card */
    .user-info {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    /* Statistics cards */
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
    
    /* Delete button styling */
    .delete-button {
        background: linear-gradient(45deg, #ff4757, #ff3742) !important;
        color: white !important;
        border: none !important;
        border-radius: 5px !important;
        padding: 0.3rem 0.8rem !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
    }
    
    .delete-button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 15px rgba(255, 71, 87, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

# Fungsi untuk hash password
def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# Fungsi untuk verifikasi password
def verify_password(password, hashed):
    return hash_password(password) == hashed

# Inisialisasi database
def init_database():
    conn = sqlite3.connect('stunting_app.db')
    c = conn.cursor()
    
    # Tabel untuk users (petugas kesehatan)
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        nama_lengkap TEXT NOT NULL,
        jabatan TEXT,
        instansi TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Tabel untuk prediksi stunting (dimodifikasi dengan user_id)
    c.execute('''
    CREATE TABLE IF NOT EXISTS prediksi_stunting (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        nama TEXT,
        gender TEXT,
        usia INTEGER,
        berat_lahir REAL,
        panjang_lahir REAL,
        berat_sekarang REAL,
        panjang_sekarang REAL,
        asi TEXT,
        hasil_prediksi TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    conn.commit()
    conn.close()

# Fungsi registrasi
def register_user(username, password, nama_lengkap, jabatan, instansi):
    conn = sqlite3.connect('stunting_app.db')
    c = conn.cursor()
    
    try:
        hashed_password = hash_password(password)
        c.execute('''
        INSERT INTO users (username, password, nama_lengkap, jabatan, instansi)
        VALUES (?, ?, ?, ?, ?)
        ''', (username, hashed_password, nama_lengkap, jabatan, instansi))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

# Fungsi login
def login_user(username, password):
    conn = sqlite3.connect('stunting_app.db')
    c = conn.cursor()
    
    c.execute('SELECT id, password, nama_lengkap, jabatan, instansi FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    
    if user and verify_password(password, user[1]):
        return {
            'id': user[0],
            'username': username,
            'nama_lengkap': user[2],
            'jabatan': user[3],
            'instansi': user[4]
        }
    return None

# Fungsi untuk mendapatkan statistik user
def get_user_statistics(user_id):
    conn = sqlite3.connect('stunting_app.db')
    c = conn.cursor()
    
    # Total prediksi
    c.execute('SELECT COUNT(*) FROM prediksi_stunting WHERE user_id = ?', (user_id,))
    total_prediksi = c.fetchone()[0]
    
    # Prediksi berisiko
    c.execute('SELECT COUNT(*) FROM prediksi_stunting WHERE user_id = ? AND hasil_prediksi = "Berisiko stunting"', (user_id,))
    berisiko = c.fetchone()[0]
    
    # Prediksi tidak berisiko
    tidak_berisiko = total_prediksi - berisiko
    
    conn.close()
    
    return {
        'total_prediksi': total_prediksi,
        'berisiko': berisiko,
        'tidak_berisiko': tidak_berisiko
    }

# Fungsi untuk menghapus semua riwayat prediksi user
def delete_all_predictions(user_id):
    conn = sqlite3.connect('stunting_app.db')
    c = conn.cursor()
    
    c.execute('DELETE FROM prediksi_stunting WHERE user_id = ?', (user_id,))
    affected_rows = c.rowcount
    conn.commit()
    conn.close()
    
    return affected_rows

# Fungsi untuk mendapatkan riwayat terbaru
def get_recent_predictions(user_id, limit=5):
    conn = sqlite3.connect('stunting_app.db')
    c = conn.cursor()
    c.execute('''
    SELECT nama, hasil_prediksi, created_at 
    FROM prediksi_stunting 
    WHERE user_id = ? 
    ORDER BY created_at DESC 
    LIMIT ?
    ''', (user_id, limit))
    recent_data = c.fetchall()
    conn.close()
    return recent_data

# Inisialisasi database
init_database()

# Inisialisasi session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'show_register' not in st.session_state:
    st.session_state.show_register = False
if 'show_delete_confirmation' not in st.session_state:
    st.session_state.show_delete_confirmation = False
if 'delete_all_confirmation' not in st.session_state:
    st.session_state.delete_all_confirmation = False
if 'prediction_made' not in st.session_state:
    st.session_state.prediction_made = False
if 'last_prediction_result' not in st.session_state:
    st.session_state.last_prediction_result = None

# Halaman Login/Register
if not st.session_state.logged_in:
    # Header
    st.markdown("""
    <div class="header-container">
        <h1 class="main-title">🏥 Sistem Prediksi Stunting</h1>
        <p class="subtitle">Platform untuk Petugas Kesehatan</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if not st.session_state.show_register:
            # Form Login
            st.markdown('<div class="form-container">', unsafe_allow_html=True)
            st.markdown("### 🔐 Login Petugas Kesehatan")
            
            with st.form("login_form"):
                username = st.text_input("👤 Username", placeholder="Masukkan username Anda")
                password = st.text_input("🔒 Password", type="password", placeholder="Masukkan password Anda")
                
                col_login, col_register = st.columns(2)
                with col_login:
                    login_button = st.form_submit_button("🚀 Login", use_container_width=True)
                with col_register:
                    register_button = st.form_submit_button("📝 Daftar Baru", use_container_width=True)
                
                if login_button:
                    if username and password:
                        user = login_user(username, password)
                        if user:
                            st.session_state.logged_in = True
                            st.session_state.user_info = user
                            st.success(f"Selamat datang, {user['nama_lengkap']}!")
                            st.rerun()
                        else:
                            st.error("❌ Username atau password salah!")
                    else:
                        st.warning("⚠️ Mohon lengkapi semua field!")
                
                if register_button:
                    st.session_state.show_register = True
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            # Form Register
            st.markdown('<div class="form-container">', unsafe_allow_html=True)
            st.markdown("### 📝 Registrasi Petugas Kesehatan Baru")
            
            with st.form("register_form"):
                reg_username = st.text_input("👤 Username", placeholder="Pilih username unik")
                reg_password = st.text_input("🔒 Password", type="password", placeholder="Buat password yang kuat")
                reg_confirm_password = st.text_input("🔒 Konfirmasi Password", type="password", placeholder="Ulangi password")
                reg_nama_lengkap = st.text_input("👨‍⚕️ Nama Lengkap", placeholder="Masukkan nama lengkap")
                reg_jabatan = st.selectbox("💼 Jabatan", [
                    "Dokter", "Perawat", "Bidan", "Ahli Gizi", "Tenaga Kesehatan Masyarakat", "Lainnya"
                ])
                reg_instansi = st.text_input("🏥 Instansi", placeholder="Puskesmas/Rumah Sakit/Klinik")
                
                col_back, col_submit = st.columns(2)
                with col_back:
                    back_button = st.form_submit_button("⬅️ Kembali", use_container_width=True)
                with col_submit:
                    submit_button = st.form_submit_button("✅ Daftar", use_container_width=True)
                
                if back_button:
                    st.session_state.show_register = False
                    st.rerun()
                
                if submit_button:
                    if all([reg_username, reg_password, reg_confirm_password, reg_nama_lengkap, reg_instansi]):
                        if reg_password == reg_confirm_password:
                            if len(reg_password) >= 6:
                                if register_user(reg_username, reg_password, reg_nama_lengkap, reg_jabatan, reg_instansi):
                                    st.success("✅ Registrasi berhasil! Silakan login.")
                                    st.session_state.show_register = False
                                    st.rerun()
                                else:
                                    st.error("❌ Username sudah digunakan!")
                            else:
                                st.error("❌ Password minimal 6 karakter!")
                        else:
                            st.error("❌ Konfirmasi password tidak cocok!")
                    else:
                        st.warning("⚠️ Mohon lengkapi semua field!")
            
            st.markdown('</div>', unsafe_allow_html=True)

else:
    # Halaman utama setelah login
    user_info = st.session_state.user_info
    
    # Header dengan info user
    col_header1, col_header2, col_header3 = st.columns([2, 1, 1])
    
    with col_header1:
        st.markdown(f"""
        <div class="user-info">
            <h2>👋 Selamat datang, {user_info['nama_lengkap']}</h2>
            <p>{user_info['jabatan']} - {user_info['instansi']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_header3:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_info = None
            st.session_state.prediction_made = False
            st.session_state.last_prediction_result = None
            st.rerun()
    
    # Load model dan scaler
    try:
        classifier = pickle.load(open('stunting.sav', 'rb'))
        scaler = pickle.load(open('scaler.sav', 'rb'))
    except FileNotFoundError:
        st.error("❌ File model tidak ditemukan! Pastikan file 'stunting.sav' dan 'scaler.sav' tersedia.")
        st.stop()
    
    # Sidebar dengan statistik dan riwayat
    with st.sidebar:
        st.markdown("### 📊 Statistik Anda")
        
        stats = get_user_statistics(user_info['id'])
        
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats['total_prediksi']}</div>
            <div class="stat-label">Total Prediksi</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number" style="color: #ff4757;">{stats['berisiko']}</div>
            <div class="stat-label">Berisiko Stunting</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number" style="color: #2ed573;">{stats['tidak_berisiko']}</div>
            <div class="stat-label">Tidak Berisiko</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Riwayat prediksi
        st.markdown("### 📋 Riwayat Prediksi")
        
        recent_data = get_recent_predictions(user_info['id'], 5)
        
        if recent_data:
            for data in recent_data:
                icon = "🔴" if data[1] == "Berisiko stunting" else "🟢"
                date_str = data[2][:10] if data[2] else "N/A"
                st.markdown(f"{icon} **{data[0]}** - {date_str}")
        else:
            st.info("Belum ada riwayat prediksi")
        
        col_history, col_delete = st.columns(2)
        with col_history:
            if st.button("📊 Lihat Semua"):
                st.session_state.show_history = True
        
        with col_delete:
            if stats['total_prediksi'] > 0:
                if st.button("🗑️ Hapus Semua"):
                    st.session_state.delete_all_confirmation = True
    
    # Main content
    st.markdown("""
    <div class="header-container">
        <h1 class="main-title">👶 Prediksi Risiko Stunting</h1>
        <p class="subtitle">Masukkan data anak untuk analisis risiko stunting</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Konfirmasi hapus semua riwayat
    if st.session_state.delete_all_confirmation:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.warning("⚠️ **Konfirmasi Hapus Semua Riwayat**")
        st.write("Apakah Anda yakin ingin menghapus semua riwayat prediksi? Tindakan ini tidak dapat dibatalkan.")
        
        col_cancel, col_confirm = st.columns(2)
        with col_cancel:
            if st.button("❌ Batal", use_container_width=True):
                st.session_state.delete_all_confirmation = False
                st.rerun()
        
        with col_confirm:
            if st.button("✅ Ya, Hapus Semua", use_container_width=True):
                deleted_count = delete_all_predictions(user_info['id'])
                if deleted_count > 0:
                    st.success(f"✅ Berhasil menghapus {deleted_count} riwayat prediksi.")
                else:
                    st.info("ℹ️ Tidak ada riwayat yang dihapus.")
                st.session_state.delete_all_confirmation = False
                st.session_state.show_history = False
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # Form input dalam card
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        
        # Tampilkan hasil prediksi jika ada
        if st.session_state.prediction_made and st.session_state.last_prediction_result:
            result = st.session_state.last_prediction_result
            
            st.markdown("### 📊 Hasil Analisis")
            
            if result['prediction'] == 1:
                st.error(f"**⚠️ {result['nama']} berisiko mengalami stunting**")
                st.markdown("""
                **🏥 Rekomendasi Tindakan:**
                - Rujuk ke dokter spesialis anak untuk evaluasi lebih lanjut
                - Konsultasi dengan ahli gizi untuk penyusunan diet khusus
                - Monitoring pertumbuhan intensif setiap bulan
                - Edukasi orangtua tentang gizi seimbang
                - Evaluasi faktor lingkungan dan sosial ekonomi
                """)
            else:
                st.success(f"**✅ {result['nama']} tidak berisiko stunting**")
                st.markdown("""
                **💡 Tips Pemeliharaan:**
                - Lanjutkan pola pemberian makan yang baik
                - Pantau pertumbuhan secara berkala (setiap 3 bulan)
                - Pastikan imunisasi lengkap sesuai jadwal
                - Edukasi orangtua tentang deteksi dini masalah pertumbuhan
                - Promosikan praktik hidup bersih dan sehat
                """)
            
            # Tampilkan ringkasan data
            st.markdown("---")
            st.markdown("### 📋 Ringkasan Data Anak")
            
            data_summary = pd.DataFrame({
                'Parameter': ['Nama Anak', 'Jenis Kelamin', 'Usia (bulan)', 'Berat Lahir (kg)', 
                            'Panjang Lahir (cm)', 'Berat Sekarang (kg)', 'Panjang Sekarang (cm)', 'ASI Eksklusif'],
                'Nilai': [str(result['nama']), str(result['gender']), str(result['usia']), str(result['berat_lahir']), 
                        str(result['panjang_lahir']), str(result['berat_sekarang']), str(result['panjang_sekarang']), str(result['asi'])]
            })
            
            st.table(data_summary.set_index('Parameter'))
            
            # Tombol untuk membuat prediksi baru
            if st.button("🔄 Analisis Baru", use_container_width=True):
                st.session_state.prediction_made = False
                st.session_state.last_prediction_result = None
                st.rerun()
            
            st.markdown("---")
        
        # Form input prediksi
        if not st.session_state.prediction_made:
            with st.form("prediction_form"):
                st.markdown("### 📝 Data Anak")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    nama = st.text_input("👶 Nama Anak", placeholder="Masukkan nama lengkap anak")
                    gender = st.selectbox("🚻 Jenis Kelamin", ["Laki-laki", "Perempuan"])
                    usia = st.number_input("🕒 Usia (bulan)", min_value=0, max_value=60, step=1, value=12)
                    berat_lahir = st.number_input("⚖️ Berat Lahir (kg)", min_value=1.0, max_value=5.0, step=0.1, value=3.0)
                
                with col2:
                    panjang_lahir = st.number_input("📏 Panjang Lahir (cm)", min_value=30.0, max_value=60.0, step=0.1, value=49.0)
                    berat_sekarang = st.number_input("⚖️ Berat Sekarang (kg)", min_value=1.0, max_value=20.0, step=0.1, value=10.0)
                    panjang_sekarang = st.number_input("📏 Panjang Sekarang (cm)", min_value=30.0, max_value=120.0, step=0.1, value=70.0)
                    asi = st.selectbox("🍼 Diberi ASI Eksklusif", ["Tidak", "Ya"])
                
                submitted = st.form_submit_button("🔍 Analisis Risiko Stunting", use_container_width=True)
                
                if submitted:
                    if nama.strip():
                        # Konversi input ke format yang sesuai
                        gender_num = 0 if gender == "Laki-laki" else 1
                        asi_num = 0 if asi == "Tidak" else 1
                        
                        # Membuat array input
                        input_data = (gender_num, usia, berat_lahir, panjang_lahir, 
                                    berat_sekarang, panjang_sekarang, asi_num)
                        
                        input_data_as_numpy_array = np.array(input_data).reshape(1, -1)
                        
                        # Normalisasi data input
                        std_data = scaler.transform(input_data_as_numpy_array)
                        
                        # Prediksi
                        prediction = classifier.predict(std_data)
                        
                        # Menyimpan hasil prediksi
                        hasil_prediksi = "Berisiko stunting" if prediction[0] == 1 else "Tidak berisiko stunting"
                        
                        # Simpan ke database
                        conn = sqlite3.connect('stunting_app.db')
                        c = conn.cursor()
                        c.execute('''
                        INSERT INTO prediksi_stunting 
                        (user_id, nama, gender, usia, berat_lahir, panjang_lahir, 
                         berat_sekarang, panjang_sekarang, asi, hasil_prediksi) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (user_info['id'], nama, gender, usia, berat_lahir, panjang_lahir, 
                              berat_sekarang, panjang_sekarang, asi, hasil_prediksi))
                        conn.commit()
                        conn.close()
                        
                        # Simpan hasil ke session state
                        st.session_state.prediction_made = True
                        st.session_state.last_prediction_result = {
                            'nama': nama,
                            'gender': gender,
                            'usia': usia,
                            'berat_lahir': berat_lahir,
                            'panjang_lahir': panjang_lahir,
                            'berat_sekarang': berat_sekarang,
                            'panjang_sekarang': panjang_sekarang,
                            'asi': asi,
                            'prediction': prediction[0]
                        }
                        
                        # Rerun untuk memperbarui tampilan
                        st.rerun()
                        
                    else:
                        st.warning("⚠️ Mohon masukkan nama anak untuk melanjutkan analisis.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tampilkan riwayat lengkap jika diminta
    if 'show_history' in st.session_state and st.session_state.show_history:
        st.markdown("---")
        st.markdown("### 📊 Riwayat Lengkap Prediksi")
        
        conn = sqlite3.connect('stunting_app.db')
        df_history = pd.read_sql_query('''
        SELECT nama, gender, usia, berat_lahir, panjang_lahir, 
               berat_sekarang, panjang_sekarang, asi, hasil_prediksi, created_at
        FROM prediksi_stunting 
        WHERE user_id = ? 
        ORDER BY created_at DESC
        ''', conn, params=(user_info['id'],))
        conn.close()
        
        if not df_history.empty:
            # Konversi tanggal dan pastikan semua kolom dalam format yang tepat
            df_history['created_at'] = pd.to_datetime(df_history['created_at']).dt.strftime('%Y-%m-%d %H:%M')
            df_history.columns = ['Nama', 'Gender', 'Usia (bln)', 'BB Lahir (kg)', 'PB Lahir (cm)', 
                                'BB Sekarang (kg)', 'PB Sekarang (cm)', 'ASI', 'Hasil Prediksi', 'Tanggal']
            
            # Pastikan semua kolom numerik dalam format yang tepat
            df_history['Usia (bln)'] = df_history['Usia (bln)'].astype(str)
            df_history['BB Lahir (kg)'] = df_history['BB Lahir (kg)'].astype(str)
            df_history['PB Lahir (cm)'] = df_history['PB Lahir (cm)'].astype(str)
            df_history['BB Sekarang (kg)'] = df_history['BB Sekarang (kg)'].astype(str)
            df_history['PB Sekarang (cm)'] = df_history['PB Sekarang (cm)'].astype(str)
            
            st.dataframe(df_history, use_container_width=True)
            
            # Tombol untuk menutup riwayat dan hapus semua
            col_close, col_delete_all = st.columns(2)
            with col_close:
                if st.button("❌ Tutup Riwayat", use_container_width=True):
                    st.session_state.show_history = False
                    st.rerun()
            
            with col_delete_all:
                if st.button("🗑️ Hapus Semua Riwayat", use_container_width=True):
                    st.session_state.delete_all_confirmation = True
                    st.session_state.show_history = False
                    st.rerun()
        else:
            st.info("Belum ada riwayat prediksi yang tersimpan.")
            
            # Tombol untuk menutup riwayat
            if st.button("❌ Tutup Riwayat"):
                st.session_state.show_history = False
                st.rerun()

# Cara Running
# py -m streamlit run stunting_detection_app.py