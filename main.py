import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import bcrypt
import io

from auth import login, logout
from database import supabase

st.set_page_config(
    page_title="SKD App",
    layout="wide"
)


# ======================
# HELPER FUNCTIONS
# ======================
def show_toast(message: str):
    """Menampilkan notifikasi toast custom di posisi top-center."""
    st.markdown(
        f"""
        <div class="custom-toast">
            <span>✅</span>
            <span>{message}</span>
        </div>
        """,
        unsafe_allow_html=True
    )


def inject_global_css():
    """Menerapkan Design System baru: Minimalis, Profesional, dan Modern."""
    st.markdown(
        """
        <style>
        /* 1. Global Background & Text */
        .stApp {
            background-color: #EAEFEF !important;
            color: #25343F !important;
        }
        
        [data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid #BFC9D1 !important;
        }

        /* 2. Header / Top Navigation */
        header[data-testid="stHeader"] {
            background-color: #BFC9D1 !important;
            color: #25343F !important;
        }
        header[data-testid="stHeader"] svg {
            fill: #FFFFFF !important;
        }

        /* 3. Cards Styling */
        .main-card {
            background-color: #FFFFFF !important;
            border: 1px solid #BFC9D1 !important;
            border-radius: 8px !important;
            padding: 20px !important;
            margin-bottom: 20px !important;
        }

        /* 4. Input Fields Styling */
        div[data-baseweb="input"], 
        div[data-baseweb="select"] > div, 
        div[data-baseweb="textarea"] textarea,
        .stTextInput input, .stNumberInput input, .stSelectbox div[role="button"] {
            background-color: #FFFFFF !important;
            color: #25343F !important;
            border: 1px solid #BFC9D1 !important;
            border-radius: 6px !important;
        }

        /* 5. Typography */
        h1, h2, h3, h4, h5, h6, label, p, span, .stMarkdown {
            color: #25343F !important;
        }
        [data-testid="stWidgetLabel"] p {
            font-weight: 500 !important;
            color: #25343F !important;
        }
        /* Text Sekunder */
        .stCaption, small {
            color: rgba(37, 52, 63, 0.7) !important;
        }

        /* 6. Buttons Styling (Primary, Secondary, Accent) */
        /* Primary Buttons */
        div.stButton > button, 
        div[data-testid="stFormSubmitButton"] > button,
        [data-testid="baseButton-primary"] {
            background-color: #FFFFFF !important;
            color: #FFFFFF !important;
            border: 1px solid #25343F !important;
            border-radius: 6px !important;
            padding: 10px 20px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        div.stButton > button:hover,
        div[data-testid="stFormSubmitButton"] > button:hover,
        [data-testid="baseButton-primary"]:hover {
            background-color: #FFFFFF !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        }

        /* Secondary / Download Buttons */
        div.stDownloadButton > button,
        [data-testid="baseButton-secondary"] {
            background-color: #FFFFFF !important;
            color: #25343F !important;
            border: 1px solid #BFC9D1 !important;
            border-radius: 6px !important;
        }
        div.stDownloadButton > button:hover,
        [data-testid="baseButton-secondary"]:hover {
            background-color: #f8f9f9 !important;
            color: #25343F !important;
            border-color: #25343F !important;
        }

        /* Accent Elements */
        .accent-box {
            background-color: #FFFFFF !important;
            color: #FFFFFF !important;
            padding: 8px 12px !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
        }

        /* 7. Toast Notification (Center, smooth fade) */
        @keyframes fadeInOut {
            0% { opacity: 0; transform: translate(-50%, -60%); }
            10% { opacity: 1; transform: translate(-50%, -50%); }
            90% { opacity: 1; transform: translate(-50%, -50%); }
            100% { opacity: 0; transform: translate(-50%, -40%); }
        }
        .custom-toast {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: #A8FBD3 !important;
            color: #FFFFFF !important;
            padding: 12px 24px !important;
            border-radius: 8px !important;
            z-index: 10000;
            display: flex;
            align-items: center;
            gap: 12px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
            animation: fadeInOut 4s ease-in-out forwards;
            font-weight: 600 !important;
            font-size: 1rem !important;
            white-space: nowrap;
            justify-content: center;
        }

        /* 8. Table Styling */
        [data-testid="stDataFrame"], [data-testid="stTable"] {
            border: 1px solid #BFC9D1 !important;
            border-radius: 8px !important;
            overflow: hidden !important;
        }

        /* 9. Container Border (Cards) */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #FFFFFF !important;
            border: 1px solid #BFC9D1 !important;
            border-radius: 8px !important;
            padding: 10px !important;
        }
        
        /* 10. Hilangkan shadow default Streamlit */
        * {
            box-shadow: none !important;
        }

        /* 11. Mobile Responsiveness */
        @media (max-width: 768px) {
            .main .block-container {
                padding: 1rem 0.5rem !important;
            }
            h1 { font-size: 1.8rem !important; }
            h2 { font-size: 1.4rem !important; }
            h3 { font-size: 1.2rem !important; }

            /* Sembunyikan sidebar secara default jika diperlukan atau biarkan Streamlit handle */
        }

        /* 12. Print Styles */
        @media print {
            /* Sembunyikan elemen UI yang tidak diperlukan saat cetak */
            [data-testid="stSidebar"], 
            header[data-testid="stHeader"], 
            .stButton, 
            .stDownloadButton,
            div[data-testid="stSelectbox"], 
            div[data-testid="stNumberInput"],
            .custom-toast,
            [data-testid="stSidebarNav"],
            footer {
                display: none !important;
            }
            
            /* Optimasi layout halaman cetak */
            .main .block-container {
                padding: 0 !important;
                margin: 0 !important;
                max-width: 100% !important;
            }
            
            .stApp {
                background-color: white !important;
            }

            /* Kartu dan Container */
            .main-card, [data-testid="stVerticalBlockBorderWrapper"] {
                width: 100% !important;
                border: 1px solid #EEE !important; /* Border tipis saja untuk pemisah */
                box-shadow: none !important;
                margin-bottom: 10px !important;
                page-break-inside: avoid !important;
                padding: 10px !important;
            }

            /* Tabel: Paksa tampilkan semua tanpa scroll */
            [data-testid="stDataFrame"], [data-testid="stTable"], .stTable {
                overflow: visible !important;
                width: 100% !important;
            }

            /* Sembunyikan elemen scrollbar */
            ::-webkit-scrollbar {
                display: none;
            }
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

inject_global_css()


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


def render_skd_chart(df, title, is_component=True):
    """
    Render grafik SKD dengan gaya seragam dan responsif.
    """
    if df.empty:
        st.warning(f"Data kosong untuk {title}")
        return None

    # Hitung figsize dinamis berdasarkan jumlah data
    num_data = len(df)
    dynamic_width = max(8, num_data * 0.7)

    fig, ax = plt.subplots(figsize=(dynamic_width, 5), dpi=100)

    if is_component:
        ax.plot(df["label"], df["twk"], marker="o", label="TWK", color="#25343F", linewidth=2)
        ax.plot(df["label"], df["tiu"], marker="o", label="TIU", color="#BFC9D1", linewidth=2)
        ax.plot(df["label"], df["tkp"], marker="o", label="TKP", color="#FF9B51", linewidth=2)
        ax.set_ylabel("Nilai")
    else:
        ax.plot(df["label"], df["total"], marker="o", color='#25343F', linewidth=2.5, label="Total")
        ax.set_ylabel("Total Nilai")

    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    ax.grid(True, linestyle='--', alpha=0.6)

    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.yticks(fontsize=9)
    plt.tight_layout()

    return fig


# Cek apakah ada notifikasi tertunda di session state (setelah fungsi didefinisikan)
if "toast_msg" in st.session_state:
    show_toast(st.session_state.toast_msg)
    del st.session_state.toast_msg


def admin_user_management():
    st.header("👤 User Management (Admin)")

    tab1, tab2 = st.tabs(["👥 Kelola Akun", "📊 Kelola Nilai"])

    with tab1:
        users = fetch_all_users()
        with st.container(border=True):
            if users:
                df = pd.DataFrame(users)
                # Sesuai permintaan, daftar user hanya menampilkan nama dan role
                cols = [c for c in ["nama", "role"] if c in df.columns]

                st.subheader("Daftar User")
                st.dataframe(df[cols], use_container_width=True, hide_index=True)
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

    with tab2:
        # Edit Nilai SKD User (Admin)
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

        st.markdown("---")

        # Hapus Nilai SKD User (Admin)
        with st.container(border=True):
            st.subheader("Hapus Nilai SKD User")
            users = fetch_all_users()
            if users:
                nama_list_del_score = [u["nama"] for u in users if u["role"] != "admin"]
                if nama_list_del_score:
                    nama_pilih_del_score = st.selectbox("Pilih User untuk dihapus nilainya", nama_list_del_score, key="admin_delete_score_user")
                    user_pilih_del_score = next(u for u in users if u["nama"] == nama_pilih_del_score)
                    
                    user_scores = fetch_user_scores(user_pilih_del_score["id"])
                    if user_scores:
                        df_user_scores_del = pd.DataFrame(user_scores)
                        if "created_at" in df_user_scores_del.columns:
                            df_user_scores_del = df_user_scores_del.sort_values("created_at")
                        df_user_scores_del["skd_ke"] = range(1, len(df_user_scores_del) + 1)
                        
                        del_options_admin = [f"SKD ke-{row['skd_ke']}" for _, row in df_user_scores_del.iterrows()]
                        pilih_skd_del_admin = st.selectbox("Pilih Percobaan yang akan dihapus", del_options_admin, key="admin_delete_score_week")
                        
                        idx_pilih_del_admin = int(pilih_skd_del_admin.split("-")[-1])
                        data_pilih_del_admin = df_user_scores_del[df_user_scores_del["skd_ke"] == idx_pilih_del_admin].iloc[0]

                        if st.button(f"Hapus {pilih_skd_del_admin} untuk {nama_pilih_del_score}", key="btn_del_score"):
                            supabase.table("scores").delete().eq("id", data_pilih_del_admin["id"]).execute()
                            st.session_state.toast_msg = f"Nilai {pilih_skd_del_admin} untuk {nama_pilih_del_score} berhasil dihapus"
                            st.rerun()
                    else:
                        st.info("User ini belum memiliki riwayat nilai.")
                else:
                    st.info("Belum ada user untuk dihapus nilainya.")


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
            cols = [c for c in ["skd_ke", "twk", "tiu", "tkp", "total"] if c in df_scores.columns]
            st.dataframe(df_scores[cols], use_container_width=True, hide_index=True)

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


def prepare_admin_data():
    """Mengambil dan menyiapkan data untuk dashboard admin."""
    users = fetch_all_users()
    scores = fetch_all_scores()

    if not users:
        return None

    df_users = pd.DataFrame(users)
    total_user = len(df_users[df_users["role"] == "user"])
    total_admin = len(df_users[df_users["role"] == "admin"])
    
    df = pd.DataFrame()
    if scores:
        df_scores = pd.DataFrame(scores)
        for col in ["twk", "tiu", "tkp"]:
            if col in df_scores.columns:
                df_scores[col] = pd.to_numeric(df_scores[col], errors="coerce").fillna(0)
        
        df_scores["total"] = df_scores["twk"] + df_scores["tiu"] + df_scores["tkp"]

        df = pd.merge(
            df_scores,
            df_users[["id", "nama", "role"]],
            left_on="user_id",
            right_on="id",
            how="inner"
        )

        if "role" in df.columns:
            df = df[df["role"] != "admin"]

        if not df.empty:
            if "created_at" in df.columns:
                df = df.sort_values(["user_id", "created_at"])
            else:
                df = df.sort_values(["user_id"])
            
            df["skd_ke"] = df.groupby("user_id").cumcount() + 1
            
    return {
        "df_users": df_users,
        "total_user": total_user,
        "total_admin": total_admin,
        "scores": scores,
        "df": df
    }


def admin_dashboard_summary():
    st.header("📈 Dashboard Summary")
    data = prepare_admin_data()
    if not data:
        st.info("Belum ada data user.")
        return

    df_users = data["df_users"]
    total_user = data["total_user"]
    total_admin = data["total_admin"]
    df = data["df"]
    
    total_skd_max = 0
    score_summary = pd.DataFrame(columns=["user_id", "total_skd", "max_score"])

    if not df.empty:
        total_skd_max = df["skd_ke"].max()
        score_summary = df.groupby("user_id").agg(
            total_skd=("skd_ke", "max"),
            max_score=("total", "max")
        ).reset_index()

    # --- Bagian Metrics Atas ---
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.metric("Total User", total_user)
    with col2:
        with st.container(border=True):
            st.metric("Total Admin", total_admin)
    with col3:
        with st.container(border=True):
            st.metric("SKD Terbanyak", total_skd_max)

    # --- Tabel Ringkasan Aktivitas User ---
    user_summary_df = df_users[df_users["role"] == "user"][["id", "nama"]].merge(
        score_summary, left_on="id", right_on="user_id", how="left"
    )
    user_summary_df["total_skd"] = user_summary_df["total_skd"].fillna(0).astype(int)
    user_summary_df["max_score"] = user_summary_df["max_score"].fillna(0).astype(int)
    user_summary_df = user_summary_df[["nama", "total_skd", "max_score"]].sort_values("max_score", ascending=False)
    user_summary_df.columns = ["Nama User", "Total SKD", "Nilai Tertinggi"]
    
    with st.container(border=True):
        st.subheader("📊 Ringkasan Aktivitas User")
        st.dataframe(user_summary_df, use_container_width=True, hide_index=True)
        if st.button("🖨️ Cetak Ringkasan"):
            st.components.v1.html("<script>window.parent.print();</script>", height=0)


def admin_grafik_nilai():
    st.header("📊 Grafik Nilai SKD")
    data = prepare_admin_data()
    if not data:
        st.info("Belum ada data user.")
        return
    
    scores = data["scores"]
    df = data["df"]

    if not scores:
        st.info("Belum ada data nilai (scores) di database.")
        return

    if df.empty:
        st.warning("Tidak ada data nilai dari user (non-admin).")
        return

    # Filter Pilihan User
    user_list = ["Semua User"] + sorted(df["nama"].unique().tolist())
    pilih_user = st.selectbox("Pilih User", user_list)

    if pilih_user != "Semua User":
        max_skd = int(df[df["nama"] == pilih_user]["skd_ke"].max()) if not df.empty else 0
    else:
        max_skd = int(df["skd_ke"].max()) if not df.empty else 0

    options = ["Terakhir", "Semua", "Rentang"] + [f"SKD ke-{i}" for i in range(1, max_skd + 1)]
    
    default_skd_idx = 1 if pilih_user != "Semua User" else 0
    pilih_skd = st.selectbox("Pilih Percobaan SKD (Attempt)", options, index=default_skd_idx)

    rentang_aktif = False
    if pilih_skd == "Rentang":
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            r_dari = st.number_input("Dari SKD ke-", min_value=1, max_value=max_skd, value=1)
        with col_r2:
            r_sampai = st.number_input("Sampai SKD ke-", min_value=r_dari, max_value=max_skd, value=max_skd)
        rentang_aktif = True

    if pilih_user != "Semua User":
        df = df[df["nama"] == pilih_user]

    if rentang_aktif:
        filtered = df[(df["skd_ke"] >= r_dari) & (df["skd_ke"] <= r_sampai)]
        filtered = filtered.sort_values(["skd_ke", "nama"])
        st.subheader(f"Data SKD Rentang ke-{r_dari} sampai {r_sampai}")
    elif pilih_skd == "Terakhir":
        if "created_at" in df.columns:
            filtered = df.sort_values("created_at").groupby("user_id").tail(1).copy()
        else:
            filtered = df.groupby("user_id").tail(1).copy()
        st.subheader("Data SKD Terakhir Setiap User")
    elif pilih_skd == "Semua":
        filtered = df.copy()
        filtered = filtered.sort_values(["skd_ke", "nama"])
        st.subheader("Semua Riwayat Data SKD")
    else:
        try:
            n = int(pilih_skd.split("-")[-1])
            filtered = df[df["skd_ke"] == n].copy()
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
        st.dataframe(filtered[cols_to_show], use_container_width=True, hide_index=True)

        if st.button("🖨️ Cetak Nilai & Diagram"):
            st.components.v1.html("<script>window.parent.print();</script>", height=0)

    if pilih_skd in ["Semua", "Rentang"]:
        if pilih_user == "Semua User":
            filtered["label"] = filtered["nama"] + " (SKD " + filtered["skd_ke"].astype(str) + ")"
        else:
            filtered["label"] = "SKD ke-" + filtered["skd_ke"].astype(str)
    else:
        filtered["label"] = filtered["nama"]

    with st.container(border=True):
        st.subheader("Grafik Komponen Nilai")
        fig1 = render_skd_chart(filtered, f"Komponen Nilai SKD ({pilih_skd})", is_component=True)
        if fig1:
            st.pyplot(fig1)
            # Tombol Download
            buf1 = io.BytesIO()
            fig1.savefig(buf1, format="png", bbox_inches="tight")
            st.download_button(
                label="📥 Download Grafik Komponen (PNG)",
                data=buf1.getvalue(),
                file_name=f"skd_komponen_{pilih_user}_{pilih_skd}.png",
                mime="image/png"
            )

    with st.container(border=True):
        st.subheader("Grafik Total Nilai")
        fig2 = render_skd_chart(filtered, f"Total Nilai SKD ({pilih_skd})", is_component=False)
        if fig2:
            st.pyplot(fig2)
            # Tombol Download
            buf2 = io.BytesIO()
            fig2.savefig(buf2, format="png", bbox_inches="tight")
            st.download_button(
                label="📥 Download Grafik Total (PNG)",
                data=buf2.getvalue(),
                file_name=f"skd_total_{pilih_user}_{pilih_skd}.png",
                mime="image/png"
            )


def user_personal_dashboard(user: dict):
    """Dashboard khusus user: hanya lihat nilai miliknya sendiri."""
    st.header("📊 Dashboard Nilai Saya")

    scores = fetch_user_scores(user["id"])
    
    # --- Bagian Metrics Atas ---
    total_skd = len(scores)
    max_score = max([s.get("total", 0) for s in scores]) if scores else 0
    
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.metric("Total SKD Saya", total_skd)
    with col2:
        with st.container(border=True):
            st.metric("Nilai Tertinggi Saya", max_score)

    if not scores:
        st.info("Belum ada data nilai. Silakan input nilai terlebih dahulu di menu User.")
        return

    df = pd.DataFrame(scores)

    # Urutkan berdasarkan waktu (kalau ada), lalu beri nomor percobaan "SKD ke-"
    if "created_at" in df.columns:
        df = df.sort_values("created_at")
    df["skd_ke"] = range(1, len(df) + 1)
    df["label"] = "SKD ke-" + df["skd_ke"].astype(str)

    with st.container(border=True):
        st.subheader("Riwayat Nilai")
        cols = [c for c in ["skd_ke", "twk", "tiu", "tkp", "total"] if c in df.columns]
        st.dataframe(df[cols], use_container_width=True, hide_index=True)
        if st.button("🖨️ Cetak Nilai & Diagram"):
            st.components.v1.html("<script>window.parent.print();</script>", height=0)

    with st.container(border=True):
        st.subheader("Grafik Komponen Nilai (Per Percobaan)")
        fig1 = render_skd_chart(df, "Perkembangan Nilai TWK / TIU / TKP", is_component=True)
        if fig1:
            st.pyplot(fig1)
            buf1 = io.BytesIO()
            fig1.savefig(buf1, format="png", bbox_inches="tight")
            st.download_button(
                label="📥 Download Grafik Komponen (PNG)",
                data=buf1.getvalue(),
                file_name=f"my_skd_komponen.png",
                mime="image/png"
            )

    with st.container(border=True):
        st.subheader("Grafik Total Nilai")
        fig2 = render_skd_chart(df, "Perkembangan Total Nilai SKD", is_component=False)
        if fig2:
            st.pyplot(fig2)
            buf2 = io.BytesIO()
            fig2.savefig(buf2, format="png", bbox_inches="tight")
            st.download_button(
                label="📥 Download Grafik Total (PNG)",
                data=buf2.getvalue(),
                file_name=f"my_skd_total.png",
                mime="image/png"
            )


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

if role == "admin":
    menu_options = ["Dashboard", "Grafik Nilai", "User", "Maintenance"]
else:
    menu_options = ["Dashboard", "User"]

with st.sidebar:
    st.markdown("### 🧭 Menu Utama")
    menu = st.radio(
        "Pilih Halaman",
        menu_options,
        index=0,
    )
    st.markdown("---")
    logout()

# ======================
# HALAMAN DASHBOARD
# ======================
if menu == "Dashboard":
    if role == "admin":
        admin_dashboard_summary()
    else:
        user_personal_dashboard(user)

# ======================
# HALAMAN GRAFIK NILAI
# ======================
elif menu == "Grafik Nilai":
    if role == "admin":
        admin_grafik_nilai()
    else:
        st.error("Hanya Admin yang dapat mengakses halaman ini.")

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
