import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import bcrypt

from auth import login, logout
from database import supabase

st.set_page_config(
    page_title="SKD App",
    layout="wide"
)


def inject_global_css():
    st.markdown(
        """
        <style>
        /* 1. Paksa Latar Belakang Putih Total */
        .stApp {
            background-color: #FFFFFF !important;
        }

        /* 2. Sidebar Cerah */
        [data-testid="stSidebar"] {
            background-color: #F8FAFB !important;
            border-right: 1px solid #EAEFEF !important;
        }

        /* 3. Typography: Gunakan Abu Gelap, BUKAN Hitam */
        h1, h2, h3, p, span, label {
            color: #34495E !important; 
        }

        /* 4. Pop-up Tengah Layar (Sangat Cerah) */
        @keyframes popIn {
            0% { opacity: 0; transform: translate(-50%, -60%) scale(0.9); }
            15% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
            85% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
            100% { opacity: 0; transform: translate(-50%, -40%) scale(0.9); }
        }

        .custom-toast-container {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 1000001; /* Pastikan di atas segalanya */
            pointer-events: none;
        }

        .custom-toast {
            background: #FFFFFF !important;
            color: #FF9B51 !important; /* Teks Orange agar cerah */
            padding: 30px 50px !important;
            border-radius: 25px !important;
            text-align: center;
            box-shadow: 0 15px 50px rgba(0,0,0,0.1) !important; /* Shadow lembut */
            border: 4px solid #FF9B51 !important; /* Border orange tebal */
            animation: popIn 4s ease-in-out forwards;
            min-width: 350px;
        }

        .toast-text {
            font-size: 1.3rem !important;
            font-weight: 800 !important;
            margin-top: 10px;
            display: block;
        }

        /* 5. Tombol Orange */
        div.stButton > button {
            background-color: #FF9B51 !important;
            color: white !important;
            border-radius: 10px !important;
            border: none !important;
            padding: 0.5rem 2rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
def show_toast(message: str):
    st.markdown(
        f"""
        <div class="custom-toast-container">
            <div class="custom-toast">
                <div style="font-size: 50px;">🌟</div>
                <span class="toast-text">{message}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
def fetch_all_users():
    response = supabase.table("users").select("*").execute()
    return getattr(response, "data", []) or []


def fetch_all_scores():
    """Ambil semua data dari tabel scores."""
    try:
        response = supabase.table("scores").select("*").execute()
        return getattr(response, "data", []) or []
    except Exception:
        return []


def fetch_user_scores(user_id: str):
    """Ambil semua riwayat nilai untuk satu user (scores table)."""
    try:
        response = (
            supabase.table("scores")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return getattr(response, "data", []) or []
    except Exception:
        # Jika tabel scores belum ada atau error lain, kembalikan list kosong
        return []


def fetch_latest_score(user_id: str):
    """Ambil nilai terbaru user dari tabel scores."""
    scores = fetch_user_scores(user_id)
    return scores[0] if scores else None


# Cek apakah ada notifikasi tertunda di session state (setelah fungsi didefinisikan)
if "toast_msg" in st.session_state:
    show_toast(st.session_state.toast_msg)
    del st.session_state.toast_msg


def admin_user_management():
    st.header("👤 User Management (Admin)")

    users = fetch_all_users()
    with st.container(border=True):
        if users:
            df = pd.DataFrame(users)
            # Sesuai permintaan, daftar user hanya menampilkan nama dan role
            cols = [c for c in ["nama", "role"] if c in df.columns]

            st.subheader("Daftar User")
            st.dataframe(df[cols], use_container_width=True)
        else:
            st.info("Belum ada user di database.")

    st.markdown("---")

    # Edit user
    with st.container(border=True):
        st.subheader("Edit User")
        users = fetch_all_users()
        if users:
            nama_list = [u["nama"] for u in users]
            nama_pilih = st.selectbox("Pilih User", nama_list, key="edit_user_select")
            user_pilih = next(u for u in users if u["nama"] == nama_pilih)

            current_role = user_pilih.get("role", "user")

            with st.form("edit_user"):
                new_password = st.text_input(
                    "Password baru (kosongkan jika tidak diubah)", type="password"
                )
                new_role = st.selectbox(
                    "Role",
                    ["admin", "user"],
                    index=0 if current_role == "admin" else 1,
                )

                submitted_edit = st.form_submit_button("Simpan Perubahan")

        if submitted_edit:
            update_data = {
                "role": new_role,
            }
            if new_password:
                password_hash = bcrypt.hashpw(
                    new_password.encode("utf-8"), bcrypt.gensalt()
                ).decode("utf-8")
                update_data["password"] = password_hash

            supabase.table("users").update(update_data).eq(
                "id", user_pilih["id"]
            ).execute()
            st.session_state.toast_msg = "User berhasil diupdate"
            st.rerun()

    st.markdown("---")

    # Hapus user
    with st.container(border=True):
        st.subheader("Hapus User")
        users = fetch_all_users()
        if users:
            nama_list_hapus = [u["nama"] for u in users]
            nama_hapus = st.selectbox(
                "Pilih User untuk dihapus", nama_list_hapus, key="delete_user_select"
            )
            user_hapus = next(u for u in users if u["nama"] == nama_hapus)

            if st.button("Hapus User"):
                supabase.table("users").delete().eq("id", user_hapus["id"]).execute()
                st.session_state.toast_msg = "User berhasil dihapus"
                st.rerun()

    st.markdown("---")

    # Edit Nilai User (Admin)
    with st.container(border=True):
        st.subheader("Edit Nilai SKD User")
        users = fetch_all_users()
        if users:
            nama_list_score = [u["nama"] for u in users if u["role"] != "admin"]
            if nama_list_score:
                nama_pilih_score = st.selectbox("Pilih User untuk diedit nilainya", nama_list_score, key="admin_edit_score_user")
                user_pilih_score = next(u for u in users if u["nama"] == nama_pilih_score)
                
                user_scores = fetch_user_scores(user_pilih_score["id"])
                if user_scores:
                    df_user_scores = pd.DataFrame(user_scores)
                    if "created_at" in df_user_scores.columns:
                        df_user_scores = df_user_scores.sort_values("created_at")
                    df_user_scores["skd_ke"] = range(1, len(df_user_scores) + 1)
                    
                    edit_options_admin = [f"SKD ke-{row['skd_ke']}" for _, row in df_user_scores.iterrows()]
                    pilih_skd_admin = st.selectbox("Pilih Percobaan (Minggu)", edit_options_admin, key="admin_edit_score_week")
                    
                    idx_pilih_admin = int(pilih_skd_admin.split("-")[-1])
                    data_pilih_admin = df_user_scores[df_user_scores["skd_ke"] == idx_pilih_admin].iloc[0]

                    with st.form("admin_edit_nilai_form"):
                        ae_twk = st.number_input("Update TWK", min_value=0, value=int(data_pilih_admin["twk"]))
                        ae_tiu = st.number_input("Update TIU", min_value=0, value=int(data_pilih_admin["tiu"]))
                        ae_tkp = st.number_input("Update TKP", min_value=0, value=int(data_pilih_admin["tkp"]))
                        submitted_admin_edit_score = st.form_submit_button("Simpan Perubahan Nilai User")

                    if submitted_admin_edit_score:
                        ae_total = ae_twk + ae_tiu + ae_tkp
                        supabase.table("scores").update({
                            "twk": ae_twk,
                            "tiu": ae_tiu,
                            "tkp": ae_tkp,
                            "total": ae_total
                        }).eq("id", data_pilih_admin["id"]).execute()
                        
                        st.session_state.toast_msg = f"Nilai {nama_pilih_score} berhasil diperbarui"
                        st.rerun()
                else:
                    st.info("User ini belum memiliki riwayat nilai.")
            else:
                st.info("Belum ada user untuk diedit nilainya.")


def user_self_page(user: dict):
    st.header("📑 Profil & Nilai Saya")
    
    with st.container(border=True):
        st.write(f"Nama: **{user.get('nama')}**")
        st.write(f"Role: **{user.get('role', 'user')}**")

    st.markdown("---")
    
    with st.container(border=True):
        st.subheader("Input / Update Nilai SKD")

        latest = fetch_latest_score(user["id"])
        current_twk = (latest or {}).get("twk") or 0
        current_tiu = (latest or {}).get("tiu") or 0
        current_tkp = (latest or {}).get("tkp") or 0

        with st.form("update_nilai_saya"):
            twk = st.number_input("TWK", min_value=0, value=int(current_twk))
            tiu = st.number_input("TIU", min_value=0, value=int(current_tiu))
            tkp = st.number_input("TKP", min_value=0, value=int(current_tkp))
            submitted_nilai = st.form_submit_button("Simpan Nilai")

    if submitted_nilai:
        total = twk + tiu + tkp
        # Simpan sebagai percobaan baru di tabel scores
        supabase.table("scores").insert(
            {
                "user_id": user["id"],
                "twk": twk,
                "tiu": tiu,
                "tkp": tkp,
                "total": total,
            }
        ).execute()

        # Nilai sekarang hanya disimpan di tabel scores (history)
        
        # update juga di session supaya tampilan langsung ikut berubah
        user.update({"twk": twk, "tiu": tiu, "tkp": tkp, "total": total})
        st.session_state.user = user

        st.session_state.toast_msg = "Nilai berhasil disimpan"
        st.rerun()

    st.markdown("---")

    scores = fetch_user_scores(user["id"])
    if scores:
        df_scores = pd.DataFrame(scores)
        if "created_at" in df_scores.columns:
            df_scores = df_scores.sort_values("created_at")
        df_scores["skd_ke"] = range(1, len(df_scores) + 1)
        
        with st.container(border=True):
            # Tampilkan riwayat
            st.subheader("Riwayat Nilai SKD")
            cols = [c for c in ["skd_ke", "created_at", "twk", "tiu", "tkp", "total"] if c in df_scores.columns]
            st.dataframe(df_scores[cols], use_container_width=True)

        st.markdown("---")
        with st.container(border=True):
            st.subheader("Edit Nilai Percobaan (SKD ke-n)")
            
            edit_options = [f"SKD ke-{row['skd_ke']}" for _, row in df_scores.iterrows()]
            pilih_edit = st.selectbox("Pilih Percobaan yang Ingin Diubah", edit_options)
            
            idx_pilih = int(pilih_edit.split("-")[-1])
            data_pilih = df_scores[df_scores["skd_ke"] == idx_pilih].iloc[0]

            with st.form("edit_nilai_user"):
                e_twk = st.number_input("Update TWK", min_value=0, value=int(data_pilih["twk"]))
                e_tiu = st.number_input("Update TIU", min_value=0, value=int(data_pilih["tiu"]))
                e_tkp = st.number_input("Update TKP", min_value=0, value=int(data_pilih["tkp"]))
                submitted_edit_score = st.form_submit_button("Simpan Perubahan Nilai")

        if submitted_edit_score:
            e_total = e_twk + e_tiu + e_tkp
            supabase.table("scores").update({
                "twk": e_twk,
                "tiu": e_tiu,
                "tkp": e_tkp,
                "total": e_total
            }).eq("id", data_pilih["id"]).execute()
            
            st.session_state.toast_msg = f"Berhasil memperbarui {pilih_edit}"
            st.rerun()

    else:
        st.info("Belum ada riwayat nilai. Silakan input nilai pertama Anda.")


def grafik_dashboard():
    st.header("📈 Dashboard & Grafik Nilai SKD")

    users = fetch_all_users()
    scores = fetch_all_scores()

    if not users:
        st.info("Belum ada data user.")
        return

    if not scores:
        st.info("Belum ada data nilai (scores) di database.")
        return

    df_users = pd.DataFrame(users)
    df_scores = pd.DataFrame(scores)

    # Pastikan tipe data benar
    for col in ["twk", "tiu", "tkp"]:
        if col in df_scores.columns:
            df_scores[col] = pd.to_numeric(df_scores[col], errors="coerce").fillna(0)
    
    # Hitung ulang total untuk memastikan kolom total ada dan akurat
    df_scores["total"] = df_scores["twk"] + df_scores["tiu"] + df_scores["tkp"]

    # Gabungkan dengan data user untuk mendapatkan nama dan role
    df = pd.merge(
        df_scores,
        df_users[["id", "nama", "role"]],
        left_on="user_id",
        right_on="id",
        how="inner"
    )

    # Hilangkan admin dari tampilan
    if "role" in df.columns:
        df = df[df["role"] != "admin"]

    if df.empty:
        st.warning("Tidak ada data nilai dari user (non-admin).")
        return

    # Hitung SKD ke-n untuk tiap user
    # Pastikan created_at ada dan urutkan
    if "created_at" in df.columns:
        df = df.sort_values(["user_id", "created_at"])
    else:
        df = df.sort_values(["user_id"])
    
    df["skd_ke"] = df.groupby("user_id").cumcount() + 1

    # Filter Pilihan User
    user_list = ["Semua User"] + sorted(df["nama"].unique().tolist())
    pilih_user = st.selectbox("Pilih User", user_list)

    # Filter pilihan SKD
    max_skd = int(df["skd_ke"].max())
    options = ["Terakhir"] + [f"SKD ke-{i}" for i in range(1, max_skd + 1)] + ["Semua"]
    
    # Jika pilih user tertentu, default ke "Semua" riwayat dia
    default_skd_idx = 2 if pilih_user != "Semua User" else 0
    pilih_skd = st.selectbox("Pilih Percobaan SKD (Attempt)", options, index=default_skd_idx)

    # Apply User Filter
    if pilih_user != "Semua User":
        df = df[df["nama"] == pilih_user]

    if pilih_skd == "Terakhir":
        # Ambil record terbaru untuk tiap user
        if "created_at" in df.columns:
            filtered = df.sort_values("created_at").groupby("user_id").tail(1)
        else:
            filtered = df.groupby("user_id").tail(1)
        st.subheader("Data SKD Terakhir Setiap User")
    elif pilih_skd == "Semua":
        filtered = df.copy()
        st.subheader("Semua Riwayat Data SKD")
    else:
        # Ambil angka dari "SKD ke-n"
        try:
            n = int(pilih_skd.split("-")[-1])
            filtered = df[df["skd_ke"] == n]
            st.subheader(f"Data SKD Percobaan ke-{n}")
        except:
            filtered = df.copy()

    if filtered.empty:
        st.warning(f"Tidak ada data untuk filter: {pilih_skd}")
        return

    # Tampilkan Tabel
    with st.container(border=True):
        st.subheader("Data Riwayat SKD")
        cols_to_show = ["nama", "skd_ke", "twk", "tiu", "tkp", "total"]
        if "created_at" in filtered.columns:
            cols_to_show.insert(1, "created_at")
        
        st.dataframe(filtered[cols_to_show], use_container_width=True)

        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download CSV", 
            csv, 
            f"skd_data_{pilih_skd.replace(' ', '_')}.csv", 
            "text/csv"
        )

    # Label untuk grafik agar unik jika pilih "Semua"
    if pilih_skd == "Semua":
        if pilih_user == "Semua User":
            filtered["label"] = filtered["nama"] + " (SKD " + filtered["skd_ke"].astype(str) + ")"
        else:
            filtered["label"] = "SKD ke-" + filtered["skd_ke"].astype(str)
    else:
        filtered["label"] = filtered["nama"]

    with st.container(border=True):
        st.subheader("Grafik Komponen Nilai")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(filtered["label"], filtered["twk"], marker="o", label="TWK", color="#25343F")
        ax.plot(filtered["label"], filtered["tiu"], marker="o", label="TIU", color="#BFC9D1")
        ax.plot(filtered["label"], filtered["tkp"], marker="o", label="TKP", color="#FF9B51")
        # ax.set_xlabel("User")
        ax.set_ylabel("Nilai")
        ax.set_title(f"Komponen Nilai SKD ({pilih_skd})")
        ax.legend()
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)

    with st.container(border=True):
        st.subheader("Grafik Total Nilai")
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        ax2.plot(filtered["label"], filtered["total"], marker="o", color='#25343F')
        # ax2.set_xlabel("User")
        ax2.set_ylabel("Total Nilai")
        ax2.set_title(f"Total Nilai SKD ({pilih_skd})")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig2)


def user_personal_dashboard(user: dict):
    """Dashboard khusus user: hanya lihat nilai miliknya sendiri."""
    st.header("📊 Dashboard Nilai Saya")

    scores = fetch_user_scores(user["id"])
    if not scores:
        st.info("Belum ada data nilai. Silakan input nilai terlebih dahulu di menu User.")
        return

    df = pd.DataFrame(scores)

    # Urutkan berdasarkan waktu (kalau ada), lalu beri nomor percobaan "SKD ke-"
    if "created_at" in df.columns:
        df = df.sort_values("created_at")
    df["skd_ke"] = range(1, len(df) + 1)

    with st.container(border=True):
        st.subheader("Riwayat Nilai")
        cols = [c for c in ["skd_ke", "twk", "tiu", "tkp", "total"] if c in df.columns]
        st.dataframe(df[cols], use_container_width=True)

    with st.container(border=True):
        st.subheader("Grafik Komponen Nilai (Per Percobaan)")
        fig, ax = plt.subplots()
        x = df["skd_ke"]
        ax.plot(x, df["twk"], marker="o", label="TWK", color="#25343F")
        ax.plot(x, df["tiu"], marker="o", label="TIU", color="#BFC9D1")
        ax.plot(x, df["tkp"], marker="o", label="TKP", color="#FF9B51")
        # ax.set_xlabel("Percobaan (SKD ke-)")
        ax.set_ylabel("Nilai")
        ax.set_title("Perkembangan Nilai TWK / TIU / TKP")
        ax.legend()
        ax.set_xticks(x)
        ax.set_xticklabels([f"SKD ke-{i}" for i in x])
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)

    with st.container(border=True):
        st.subheader("Grafik Total Nilai")
        fig2, ax2 = plt.subplots()
        ax2.plot(x, df["total"], marker="o", color="#25343F")
        # ax2.set_xlabel("Percobaan (SKD ke-)")
        ax2.set_ylabel("Total Nilai")
        ax2.set_title("Perkembangan Total Nilai SKD")
        ax2.set_xticks(x)
        ax2.set_xticklabels([f"SKD ke-{i}" for i in x])
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig2)


def admin_maintenance():
    st.header("🛠️ Maintenance / Reset Data")
    st.warning(
        "**PERINGATAN:** Menu ini akan menghapus data secara permanen. "
        "Pastikan Anda benar-benar ingin melakukannya."
    )

    st.markdown("""
    **Aksi yang akan dilakukan:**
    1. **Menghapus semua data nilai SKD** (tabel `scores`).
    2. **Menghapus semua akun dengan role 'user'** (tabel `users`).
    3. **Menyisakan akun admin** agar sistem tetap dapat dikelola.
    """)

    st.markdown("---")
    
    confirm_phrase = "RESET SEMUA DATA"
    st.write(f"Untuk melanjutkan, silakan ketik kalimat konfirmasi di bawah ini:")
    st.code(confirm_phrase)
    
    input_confirm = st.text_input("Kalimat Konfirmasi", placeholder="Ketik di sini...")
    
    # Tombol reset hanya aktif jika input cocok
    is_confirmed = (input_confirm == confirm_phrase)
    
    if st.button("🚀 Jalankan Reset Data Sekarang", disabled=not is_confirmed):
        with st.spinner("Sedang memproses reset data..."):
            try:
                # 1. Hapus semua data scores
                # Di Supabase, .delete().neq("id", 0) atau semacamnya bisa digunakan untuk "hapus semua" jika diizinkan
                # Namun cara paling umum untuk hapus semua jika tidak ada filter spesifik:
                supabase.table("scores").delete().neq("twk", -1).execute()
                
                # 2. Hapus semua user dengan role 'user'
                supabase.table("users").delete().eq("role", "user").execute()
                
                st.session_state.toast_msg = "Semua data berhasil direset"
                st.balloons()
                
                # Beri sedikit jeda lalu rerun
                st.info("Sistem akan memuat ulang dalam sekejap...")
            except Exception as e:
                st.error(f"Terjadi kesalahan saat melakukan reset: {e}")


# ======================
# LOGIN CHECK
# ======================
if not login():
    st.stop()

user = st.session_state.get("user")
role = user.get("role", "user") if user else "user"


# ======================
# APP UTAMA
# ======================
st.title("📊 SKD Application")

st.sidebar.title("Sidebar Navigation")
menu_options = ["Dashboard", "User"]
if role == "admin":
    menu_options.append("Maintenance")

menu = st.sidebar.radio(
    "Pilih Halaman",
    menu_options,
    index=0,
)

logout()

# ======================
# HALAMAN DASHBOARD (ringkas)
# ======================
if menu == "Dashboard":
    if role == "admin":
        st.header("Ringkasan Nilai Semua User")
        grafik_dashboard()
    else:
        user_personal_dashboard(user)

# ======================
# HALAMAN USER
# ======================
elif menu == "User":
    if role == "admin":
        admin_user_management()
    else:
        if user is None:
            st.error("Data user tidak ditemukan di session.")
        else:
            user_self_page(user)

# ======================
# HALAMAN MAINTENANCE
# ======================
elif menu == "Maintenance":
    if role == "admin":
        admin_maintenance()
    else:
        st.error("Hanya Admin yang dapat mengakses halaman ini.")
