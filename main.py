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
    """Mengubah semua elemen (input, box, button) menjadi putih dengan border hitam & teks hitam."""
    st.markdown(
        """
        <style>
        /* 1. Reset Global: Background Putih & Teks Hitam */
        .stApp, [data-testid="stSidebar"], .main {
            background-color: #ffffff !important;
            color: #000000 !important;
        }

        /* 2. Sidebar Border */
        [data-testid="stSidebar"] {
            border-right: 2px solid #000000 !important;
        }

        /* 3. Semua Input Field (Kolom Teks, Number, Selectbox, Multiselect) */
        /* Menargetkan input, textarea, dan container selectbox */
        div[data-baseweb="input"], 
        div[data-baseweb="select"] > div, 
        div[data-baseweb="textarea"] textarea,
        .stTextInput input, .stNumberInput input, .stSelectbox div[role="button"] {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 2px solid #000000 !important;
            border-radius: 4px !important;
        }

        /* Fix untuk teks di dalam input agar tidak abu-abu */
        input, textarea, select {
            color: #000000 !important;
            -webkit-text-fill-color: #000000 !important;
        }

        /* 4. Teks Label & Header */
        h1, h2, h3, h4, h5, h6, label, p, span, .stMarkdown {
            color: #000000 !important;
        }

        /* 5. Radio Button & Checkbox */
        div[data-baseweb="radio"] div {
            color: #000000 !important;
        }
        /* Bulatan radio button */
        div[data-baseweb="radio"] div[role="presentation"] {
            border: 2px solid #000000 !important;
            background-color: #ffffff !important;
        }

        /* 6. Tombol (Button) */
        div.stButton > button {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 2px solid #000000 !important;
            border-radius: 4px !important;
            font-weight: bold !important;
            width: 100%;
        }
        
        div.stButton > button:hover {
            background-color: #000000 !important;
            color: #ffffff !important;
        }

        /* 7. Dataframe / Tabel */
        .styled-table, .stDataFrame {
            border: 2px solid #000000 !important;
        }

        /* Menghilangkan bayangan/shadow agar clean */
        * {
            box-shadow: none !important;
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

    # Filter pilihan SKD
    max_skd = int(df["skd_ke"].max())
    options = ["Terakhir"] + [f"SKD ke-{i}" for i in range(1, max_skd + 1)] + ["Semua"]
    pilih_skd = st.selectbox("Pilih Percobaan SKD (Attempt)", options)

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
    cols_to_show = ["nama", "skd_ke", "twk", "tiu", "tkp", "total"]
    if "created_at" in filtered.columns:
        cols_to_show.insert(1, "created_at")

    st.dataframe(filtered[cols_to_show])

    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download CSV",
        csv,
        f"skd_data_{pilih_skd.replace(' ', '_')}.csv",
        "text/csv"
    )

    # Label untuk grafik agar unik jika pilih "Semua"
    if pilih_skd == "Semua":
        filtered["label"] = filtered["nama"] + " (SKD " + filtered["skd_ke"].astype(str) + ")"
    else:
        filtered["label"] = filtered["nama"]

    st.subheader("Grafik Komponen Nilai")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(filtered["label"], filtered["twk"], marker="o", label="TWK")
    ax.plot(filtered["label"], filtered["tiu"], marker="o", label="TIU")
    ax.plot(filtered["label"], filtered["tkp"], marker="o", label="TKP")
    ax.set_xlabel("User")
    ax.set_ylabel("Nilai")
    ax.set_title(f"Komponen Nilai SKD ({pilih_skd})")
    ax.legend()
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)

    st.subheader("Grafik Total Nilai")
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.plot(filtered["label"], filtered["total"], marker="o", color='tab:orange')
    ax2.set_xlabel("User")
    ax2.set_ylabel("Total Nilai")
    ax2.set_title(f"Total Nilai SKD ({pilih_skd})")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
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
