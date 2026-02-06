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


def inject_global_css_dark_simple():
    """Dark mode minimal: sidebar gelap tipis, konten putih, tombol biru tipis, tanpa warna lain."""
    st.markdown(
        """
        <style>
        /* ===================
           BACKGROUND & TEXT
           =================== */
        .stApp {
            background: #111827; /* hitam pekat */
            color: #f9fafb; /* teks putih */
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1100px;
            color: #f9fafb;
        }

        h1, h2, h3 {
            color: #f9fafb;
        }

        /* ===================
           SIDEBAR
           =================== */
        section[data-testid="stSidebar"] {
            background-color: #1f2937 !important; /* gelap */
            color: #f9fafb !important;
            border-right: 1px solid #374151; /* tipis */
        }

        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] .stMarkdown p,
        section[data-testid="stSidebar"] .stRadio label,
        section[data-testid="stSidebar"] div {
            color: #f9fafb !important;
        }

        /* ===================
           KARTU & TABEL
           =================== */
        .skd-card {
            background-color: #1f2937; /* gelap tipis */
            padding: 1.5rem 1.75rem;
            border-radius: 12px;
            border: 1px solid #374151;
            margin-bottom: 1.5rem;
            color: #f9fafb;
        }

        .skd-card table {
            border-collapse: collapse !important;
        }

        .skd-card th {
            background-color: #111827 !important;
            font-weight: 600 !important;
            color: #f9fafb !important;
        }

        .skd-card td, .skd-card th {
            padding: 0.5rem 0.75rem !important;
            color: #f9fafb !important;
        }

        /* ===================
           TOMBOL
           =================== */
        button[kind="primary"] {
            background-color: #2563eb !important; /* biru tipis */
            color: #f9fafb !important;
            border-radius: 999px !important;
        }
        button[kind="secondary"] {
            background-color: #111827 !important;
            color: #f9fafb !important;
            border-radius: 999px !important;
        }

        a, .stButton button {
            color: #2563eb !important;
        }

        /* ===================
           FORM INPUT / SELECT
           =================== */
        input, .stTextInput>div>input, .stNumberInput>div>input {
            background-color: #111827 !important;
            color: #f9fafb !important;
            border: 1px solid #374151 !important;
            border-radius: 8px !important;
            padding: 0.4rem 0.6rem !important;
        }

        .stTextInput>div>div>button {
            color: #f9fafb !important; /* icon password */
        }

        select, .stSelectbox>div>select {
            background-color: #111827 !important;
            color: #f9fafb !important;
            border: 1px solid #374151 !important;
            border-radius: 8px !important;
            padding: 0.4rem 0.6rem !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )



inject_global_css()


# ======================
# HELPER FUNCTIONS
# ======================
def fetch_all_users():
    response = supabase.table("users").select("*").execute()
    return getattr(response, "data", []) or []


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


def admin_user_management():
    st.header("User Management (Admin)")

    users = fetch_all_users()
    if users:
        df = pd.DataFrame(users)
        for col in ["twk", "tiu", "tkp", "total"]:
            if col not in df.columns:
                df[col] = 0
        cols = [c for c in ["nama", "role", "twk", "tiu", "tkp", "total"] if c in df.columns]

        st.subheader("Daftar User")
        st.dataframe(df[cols])
    else:
        st.info("Belum ada user di database.")

    st.markdown("---")

    # Tambah user baru
    st.subheader("Tambah User Baru")
    with st.form("tambah_user"):
        nama = st.text_input("Nama")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["admin", "user"])
        submitted_tambah = st.form_submit_button("Simpan User")

    if submitted_tambah:
        if not nama or not password:
            st.error("Nama dan password wajib diisi.")
        else:
            existing = supabase.table("users").select("id").eq("nama", nama).execute()
            if getattr(existing, "data", None):
                st.error("Nama user sudah digunakan.")
            else:
                password_hash = bcrypt.hashpw(
                    password.encode("utf-8"), bcrypt.gensalt()
                ).decode("utf-8")
                supabase.table("users").insert(
                    {
                        "nama": nama,
                        "password": password_hash,
                        "role": role,
                        "twk": 0,
                        "tiu": 0,
                        "tkp": 0,
                    }
                ).execute()
                st.success("User baru berhasil ditambahkan.")
                st.rerun()

    st.markdown("---")

    # Edit user
    st.subheader("Edit User")
    users = fetch_all_users()
    if users:
        nama_list = [u["nama"] for u in users]
        nama_pilih = st.selectbox("Pilih User", nama_list, key="edit_user_select")
        user_pilih = next(u for u in users if u["nama"] == nama_pilih)

        current_role = user_pilih.get("role", "user")
        current_twk = user_pilih.get("twk") or 0
        current_tiu = user_pilih.get("tiu") or 0
        current_tkp = user_pilih.get("tkp") or 0

        with st.form("edit_user"):
            new_password = st.text_input(
                "Password baru (kosongkan jika tidak diubah)", type="password"
            )
            new_role = st.selectbox(
                "Role",
                ["admin", "user"],
                index=0 if current_role == "admin" else 1,
            )
            twk = st.number_input("TWK", min_value=0, value=int(current_twk))
            tiu = st.number_input("TIU", min_value=0, value=int(current_tiu))
            tkp = st.number_input("TKP", min_value=0, value=int(current_tkp))

            submitted_edit = st.form_submit_button("Simpan Perubahan")

        if submitted_edit:
            update_data = {
                "role": new_role,
                "twk": twk,
                "tiu": tiu,
                "tkp": tkp,
            }
            if new_password:
                password_hash = bcrypt.hashpw(
                    new_password.encode("utf-8"), bcrypt.gensalt()
                ).decode("utf-8")
                update_data["password"] = password_hash

            supabase.table("users").update(update_data).eq(
                "id", user_pilih["id"]
            ).execute()
            st.success("User berhasil diupdate.")
            st.rerun()

    st.markdown("---")

    # Hapus user
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
            st.success("User berhasil dihapus.")
            st.rerun()


def user_self_page(user: dict):
    st.header("Profil & Nilai Saya")
    st.write(f"Nama: **{user.get('nama')}**")
    st.write(f"Role: **{user.get('role', 'user')}**")

    st.markdown("---")
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

        # Update ringkasan nilai terakhir di tabel users
        supabase.table("users").update(
            {"twk": twk, "tiu": tiu, "tkp": tkp}
        ).eq("id", user["id"]).execute()

        # update juga di session supaya tampilan langsung ikut berubah
        user.update({"twk": twk, "tiu": tiu, "tkp": tkp, "total": total})
        st.session_state.user = user

        st.success("Nilai berhasil disimpan sebagai percobaan baru.")
        st.rerun()

    st.markdown("---")
    st.subheader("Riwayat Nilai SKD")

    scores = fetch_user_scores(user["id"])
    if scores:
        df_scores = pd.DataFrame(scores)
        # Tampilkan kolom yang paling penting saja jika ada
        cols = [c for c in ["created_at", "twk", "tiu", "tkp", "total"] if c in df_scores.columns]
        st.dataframe(df_scores[cols])
    else:
        st.info("Belum ada riwayat nilai. Silakan input nilai pertama Anda.")


def grafik_dashboard():
    st.header("Dashboard & Grafik Nilai SKD")

    users = fetch_all_users()
    if not users:
        st.info("Belum ada data user.")
        return

    df = pd.DataFrame(users)
    for col in ["twk", "tiu", "tkp"]:
        if col not in df.columns:
            df[col] = 0
        # pastikan tipe numerik supaya filter dan grafik jalan benar
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Hitung ulang total di sisi aplikasi agar konsisten
    df["total"] = df["twk"] + df["tiu"] + df["tkp"]

    # Hilangkan admin dari tampilan nilai/grafik agar tidak makan tempat
    if "role" in df.columns:
        df = df[df["role"] != "admin"]

    # Tidak ada filter tambahan; gunakan semua user (kecuali admin)
    filtered = df.copy()

    if filtered.empty:
        st.warning("Tidak ada data yang cocok dengan filter.")
        return

    st.subheader("Tabel Nilai User")
    cols = [c for c in ["nama", "role", "twk", "tiu", "tkp", "total"] if c in filtered.columns]
    st.dataframe(filtered[cols])

    csv = filtered[cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download CSV",
        csv,
        "users_nilai.csv",
        "text/csv",
    )

    st.subheader("Grafik Komponen Nilai")
    fig, ax = plt.subplots()
    ax.plot(filtered["nama"], filtered["twk"], marker="o", label="TWK")
    ax.plot(filtered["nama"], filtered["tiu"], marker="o", label="TIU")
    ax.plot(filtered["nama"], filtered["tkp"], marker="o", label="TKP")
    ax.set_xlabel("User")
    ax.set_ylabel("Nilai")
    ax.set_title("Nilai TWK / TIU / TKP per User")
    ax.legend()
    plt.xticks(rotation=45)
    st.pyplot(fig)

    st.subheader("Grafik Total Nilai")
    fig2, ax2 = plt.subplots()
    ax2.plot(filtered["nama"], filtered["total"], marker="o")
    ax2.set_xlabel("User")
    ax2.set_ylabel("Total Nilai")
    ax2.set_title("Total Nilai SKD per User")
    plt.xticks(rotation=45)
    st.pyplot(fig2)


def user_personal_dashboard(user: dict):
    """Dashboard khusus user: hanya lihat nilai miliknya sendiri."""
    st.header("Dashboard Nilai Saya")

    scores = fetch_user_scores(user["id"])
    if not scores:
        st.info("Belum ada data nilai. Silakan input nilai terlebih dahulu di menu User.")
        return

    df = pd.DataFrame(scores)

    # Urutkan berdasarkan waktu (kalau ada), lalu beri nomor percobaan "SKD ke-"
    if "created_at" in df.columns:
        df = df.sort_values("created_at")
    df["skd_ke"] = range(1, len(df) + 1)

    st.subheader("Riwayat Nilai")
    cols = [c for c in ["skd_ke", "twk", "tiu", "tkp", "total"] if c in df.columns]
    st.dataframe(df[cols])

    st.subheader("Grafik Komponen Nilai (Per Percobaan)")
    fig, ax = plt.subplots()
    x = df["skd_ke"]
    ax.plot(x, df["twk"], marker="o", label="TWK")
    ax.plot(x, df["tiu"], marker="o", label="TIU")
    ax.plot(x, df["tkp"], marker="o", label="TKP")
    ax.set_xlabel("Percobaan (SKD ke-)")
    ax.set_ylabel("Nilai")
    ax.set_title("Perkembangan Nilai TWK / TIU / TKP")
    ax.legend()
    ax.set_xticks(x)
    ax.set_xticklabels([f"SKD ke-{i}" for i in x])
    plt.xticks(rotation=45)
    st.pyplot(fig)

    st.subheader("Grafik Total Nilai")
    fig2, ax2 = plt.subplots()
    ax2.plot(x, df["total"], marker="o")
    ax2.set_xlabel("Percobaan (SKD ke-)")
    ax2.set_ylabel("Total Nilai")
    ax2.set_title("Perkembangan Total Nilai SKD")
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"SKD ke-{i}" for i in x])
    plt.xticks(rotation=45)
    st.pyplot(fig2)


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
menu = st.sidebar.radio(
    "Pilih Halaman",
    ["Dashboard", "User"],
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
