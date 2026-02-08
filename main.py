import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import bcrypt
import io
import datetime

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

        /* 6. Buttons Styling (Unified for all types) */
        div.stButton > button, 
        div.stDownloadButton > button,
        div[data-testid="stFormSubmitButton"] > button,
        [data-testid="baseButton-primary"],
        [data-testid="baseButton-secondary"] {
            background-color: #FFFFFF !important;
            color: #25343F !important;
            border: 1px solid #BFC9D1 !important;
            border-radius: 6px !important;
            padding: 10px 20px !important;
            font-weight: 600 !important;
            min-height: 45px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            transition: all 0.3s ease !important;
        }

        div.stButton > button:hover,
        div.stDownloadButton > button:hover,
        div[data-testid="stFormSubmitButton"] > button:hover,
        [data-testid="baseButton-primary"]:hover,
        [data-testid="baseButton-secondary"]:hover {
            background-color: #f8f9f9 !important;
            border-color: #25343F !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
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
        
        /* 10. Sidebar Collapse Button Visibility */
        [data-testid="stSidebarCollapseButton"] {
            opacity: 1 !important;
            visibility: visible !important;
        }
        
        /* 11. Hilangkan shadow default Streamlit */
        * {
            box-shadow: none !important;
        }

        /* 12. Mobile Responsiveness */
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
    
    # Warna yang lebih "tebal" (bold) agar tidak samar
    color_twk = "#25343F"  # Navy
    color_tiu = "#78909C"  # Darker Blue-Gray
    color_tkp = "#FB8C00"  # Darker Orange
    
    if is_component:
        ax.plot(df["label"], df["twk"], marker="o", label="TWK", color=color_twk, linewidth=3)
        ax.plot(df["label"], df["tiu"], marker="o", label="TIU", color=color_tiu, linewidth=3)
        ax.plot(df["label"], df["tkp"], marker="o", label="TKP", color=color_tkp, linewidth=3)
        ax.set_ylabel("Nilai", color=color_twk, fontweight='bold')
    else:
        ax.plot(df["label"], df["total"], marker="o", color=color_twk, linewidth=3.5, label="Total")
        ax.set_ylabel("Total Nilai", color=color_twk, fontweight='bold')

    ax.set_title(title, fontsize=14, fontweight='bold', pad=15, color=color_twk)
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    ax.grid(True, linestyle='--', alpha=0.6)
    
    ax.tick_params(axis='x', rotation=45, labelsize=9)
    ax.tick_params(axis='y', labelsize=9)
    fig.tight_layout()
    
    return fig


@st.cache_data(show_spinner=False)
def render_report_page(df, title, content_type="table"):
    """
    Render satu halaman laporan (Tabel atau Grafik) dengan ukuran A4 (approx 8.27x11.69 inch).
    """
    if df.empty: return None
    
    # Ukuran A4 Portrait (inch)
    figsize_a4 = (8.27, 11.69)
    fig = plt.figure(figsize=figsize_a4, dpi=100)
    
    color_primary = "#25343F"
    
    if content_type == "table":
        ax = fig.add_subplot(111)
        ax.axis('off')
        
        cols_to_show = ["skd_ke", "twk", "tiu", "tkp", "total"]
        if "nama" in df.columns and len(df["nama"].unique()) > 1:
            cols_to_show = ["nama"] + cols_to_show
        
        table_data = df[cols_to_show].copy()
        rename_map = {"skd_ke": "SKD ke-", "twk": "TWK", "tiu": "TIU", "tkp": "TKP", "total": "Total", "nama": "Nama"}
        table_data = table_data.rename(columns=rename_map)
        
        num_rows = len(table_data)
        # Dinamis font & scale agar tidak overlap dan pas di A4
        dyn_font = max(6, min(10, 500 // (num_rows + 20)))
        dyn_scale = max(1.1, min(2.5, 60 // (num_rows + 15)))

        the_table = ax.table(
            cellText=table_data.values,
            colLabels=table_data.columns,
            cellLoc='center',
            loc='upper center'
        )
        the_table.auto_set_font_size(False)
        the_table.set_fontsize(dyn_font)
        the_table.scale(1.2, dyn_scale)
        
        for (row, col), cell in the_table.get_celld().items():
            if row == 0:
                cell.set_text_props(weight='bold', color='white')
                cell.set_facecolor(color_primary)
            elif row > 0:
                cell.set_facecolor('#F8F9F9')
        
        ax.set_title(title + "\n(Halaman 1: Tabel Nilai)", fontsize=16, fontweight='bold', pad=50, color=color_primary)
        fig.subplots_adjust(top=0.85, bottom=0.05, left=0.1, right=0.9)

    else:
        # Grafik - 2 grafik ditumpuk vertikal
        ax_comp = fig.add_subplot(2, 1, 1)
        ax_total = fig.add_subplot(2, 1, 2)
        
        color_twk = "#25343F"
        color_tiu = "#78909C"
        color_tkp = "#FB8C00"

        # Pastikan data terurut
        if "skd_ke" in df.columns:
            df = df.sort_values("skd_ke")

        # Marker size & line width dinamis agar tidak berantakan saat data banyak
        num_pts = len(df)
        msize = max(2, min(8, 250 // (num_pts + 10)))
        lwidth = max(1, min(3, 100 // (num_pts + 10)))
        tick_size = max(5, min(9, 400 // (num_pts + 10)))

        # Grafik Komponen
        ax_comp.plot(df["label"], df["twk"], marker="o", label="TWK", color=color_twk, linewidth=lwidth, markersize=msize)
        ax_comp.plot(df["label"], df["tiu"], marker="o", label="TIU", color=color_tiu, linewidth=lwidth, markersize=msize)
        ax_comp.plot(df["label"], df["tkp"], marker="o", label="TKP", color=color_tkp, linewidth=lwidth, markersize=msize)
        ax_comp.set_ylabel("Nilai", color=color_twk, fontweight='bold')
        ax_comp.set_title("Grafik Komponen Nilai SKD", fontsize=14, fontweight='bold', pad=10, color=color_twk)
        ax_comp.legend(loc='upper left', bbox_to_anchor=(1, 1))
        ax_comp.grid(True, linestyle='--', alpha=0.6)
        ax_comp.tick_params(axis='x', rotation=45, labelsize=tick_size)

        # Grafik Total
        ax_total.plot(df["label"], df["total"], marker="o", color=color_twk, linewidth=lwidth + 0.5, markersize=msize, label="Total")
        ax_total.set_ylabel("Total Nilai", color=color_twk, fontweight='bold')
        ax_total.set_title("Grafik Total Nilai SKD", fontsize=14, fontweight='bold', pad=10, color=color_twk)
        ax_total.legend(loc='upper left', bbox_to_anchor=(1, 1))
        ax_total.grid(True, linestyle='--', alpha=0.6)
        ax_total.tick_params(axis='x', rotation=45, labelsize=tick_size)
        
        fig.suptitle(title + "\n(Halaman 2: Grafik Perkembangan)", fontsize=16, fontweight='bold', y=0.98, color=color_twk)
        fig.subplots_adjust(top=0.88, bottom=0.12, left=0.15, right=0.85, hspace=0.4)

    buf = io.BytesIO()
    # Gunakan bbox_inches=None agar ukuran tetap A4 murni
    fig.savefig(buf, format="png", bbox_inches=None)
    plt.close(fig)
    return buf.getvalue()


@st.dialog("Konfirmasi Update")
def confirm_update_dialog(message, session_key):
    st.write(message)
    if st.button("Ya, Simpan", use_container_width=True):
        st.session_state[session_key] = True
        st.rerun()


@st.dialog("Konfirmasi Hapus")
def confirm_delete_dialog(message, session_key):
    st.warning(message)
    if st.button("Ya, Hapus", use_container_width=True):
        st.session_state[session_key] = True
        st.rerun()


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
                    update_data = {"role": new_role}
                    if new_password:
                        password_hash = bcrypt.hashpw(
                            new_password.encode("utf-8"), bcrypt.gensalt()
                        ).decode("utf-8")
                        update_data["password"] = password_hash

                    st.session_state.pending_user_update = update_data
                    confirm_update_dialog(f"Simpan perubahan untuk user {user_pilih['nama']}?", "do_update_user")

                if st.session_state.get("do_update_user"):
                    supabase.table("users").update(st.session_state.pending_user_update).eq(
                        "id", user_pilih["id"]
                    ).execute()
                    st.session_state.toast_msg = "User berhasil diupdate"
                    del st.session_state.do_update_user
                    del st.session_state.pending_user_update
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
                    confirm_delete_dialog(f"Apakah Anda yakin ingin menghapus user {user_hapus['nama']}?", "do_delete_user")

                if st.session_state.get("do_delete_user"):
                    supabase.table("users").delete().eq("id", user_hapus["id"]).execute()
                    st.session_state.toast_msg = "User berhasil dihapus"
                    del st.session_state.do_delete_user
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
                            st.session_state.pending_admin_score_edit = {
                                "twk": ae_twk,
                                "tiu": ae_tiu,
                                "tkp": ae_tkp,
                                "total": ae_total,
                                "id": data_pilih_admin["id"],
                                "nama": nama_pilih_score,
                                "pilih_skd": pilih_skd_admin
                            }
                            confirm_update_dialog(f"Simpan perubahan nilai untuk {nama_pilih_score} ({pilih_skd_admin})?", "do_update_admin_score")

                        if st.session_state.get("do_update_admin_score"):
                            ps = st.session_state.pending_admin_score_edit
                            supabase.table("scores").update({
                                "twk": ps["twk"],
                                "tiu": ps["tiu"],
                                "tkp": ps["tkp"],
                                "total": ps["total"]
                            }).eq("id", ps["id"]).execute()
                            
                            st.session_state.toast_msg = f"Nilai {ps['nama']} berhasil diperbarui"
                            del st.session_state.do_update_admin_score
                            del st.session_state.pending_admin_score_edit
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
                            confirm_delete_dialog(f"Hapus {pilih_skd_del_admin} untuk {nama_pilih_del_score}?", "do_delete_admin_score")

                        if st.session_state.get("do_delete_admin_score"):
                            supabase.table("scores").delete().eq("id", data_pilih_del_admin["id"]).execute()
                            st.session_state.toast_msg = f"Nilai {pilih_skd_del_admin} untuk {nama_pilih_del_score} berhasil dihapus"
                            del st.session_state.do_delete_admin_score
                            st.rerun()
                    else:
                        st.info("User ini belum memiliki riwayat nilai.")
                else:
                    st.info("Belum ada user untuk dihapus nilainya.")


def user_self_page(user: dict):
    st.header("📑 Profil & Nilai Saya")
    
    tab1, tab2 = st.tabs(["📊 Kelola Nilai", "👥 Kelola Akun"])
    
    with tab1:
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
                st.session_state.pending_user_score_edit = {
                    "twk": e_twk,
                    "tiu": e_tiu,
                    "tkp": e_tkp,
                    "total": e_total,
                    "id": data_pilih["id"],
                    "pilih_edit": pilih_edit
                }
                confirm_update_dialog(f"Simpan perubahan untuk {pilih_edit}?", "do_update_user_score")

            if st.session_state.get("do_update_user_score"):
                pus = st.session_state.pending_user_score_edit
                supabase.table("scores").update({
                    "twk": pus["twk"],
                    "tiu": pus["tiu"],
                    "tkp": pus["tkp"],
                    "total": pus["total"]
                }).eq("id", pus["id"]).execute()
                
                st.session_state.toast_msg = f"Berhasil memperbarui {pus['pilih_edit']}"
                del st.session_state.do_update_user_score
                del st.session_state.pending_user_score_edit
                st.rerun()

        else:
            st.info("Belum ada riwayat nilai. Silakan input nilai pertama Anda.")

    with tab2:
        with st.container(border=True):
            st.write(f"Nama: **{user.get('nama')}**")
            st.write(f"Role: **{user.get('role', 'user')}**")

        st.markdown("---")
        
        # Edit Password
        with st.container(border=True):
            st.subheader("Edit Password")
            with st.form("user_edit_pass"):
                new_password = st.text_input("Password baru (kosongkan jika tidak diubah)", type="password")
                submitted_pass = st.form_submit_button("Simpan Perubahan Password")
            
            if submitted_pass:
                if new_password:
                    password_hash = bcrypt.hashpw(
                        new_password.encode("utf-8"), bcrypt.gensalt()
                    ).decode("utf-8")
                    st.session_state.pending_password_update = password_hash
                    confirm_update_dialog("Apakah Anda yakin ingin mengubah password?", "do_update_password")
                else:
                    st.info("Masukkan password baru jika ingin mengubah.")

            if st.session_state.get("do_update_password"):
                supabase.table("users").update({"password": st.session_state.pending_password_update}).eq("id", user["id"]).execute()
                st.session_state.toast_msg = "Password berhasil diupdate"
                del st.session_state.do_update_password
                del st.session_state.pending_password_update
                st.rerun()


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

    if pilih_user != "Semua User":
        df = df[df["nama"] == pilih_user]

    # Main Filtering for UI Display
    if pilih_skd == "Rentang":
        st.markdown("### 🔍 Filter Rentang")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            r_dari = st.number_input("Dari SKD ke-", min_value=1, max_value=max_skd, value=1, key="admin_r_dari")
        with col_r2:
            r_sampai = st.number_input("Sampai SKD ke-", min_value=r_dari, max_value=max_skd, value=max_skd, key="admin_r_sampai")

        filtered = df[(df["skd_ke"] >= r_dari) & (df["skd_ke"] <= r_sampai)].copy()
        filtered = filtered.sort_values(["skd_ke", "nama"])
        st.subheader(f"Data SKD Rentang ke-{r_dari} sampai {r_sampai}")
    elif pilih_skd == "Terakhir":
        show_this_week = st.radio("Filter Waktu:", ["Semua", "Minggu Ini"], horizontal=True, key="admin_time_filter")

        if show_this_week == "Minggu Ini" and "created_at" in df.columns:
            df = df.copy()
            df['created_at_dt'] = pd.to_datetime(df['created_at'])
            today = datetime.date.today()
            monday = today - datetime.timedelta(days=today.weekday())
            df = df[df['created_at_dt'].dt.date >= monday]
            st.subheader("Data SKD Terakhir User (Minggu Ini)")
        else:
            st.subheader("Data SKD Terakhir Setiap User")

        if "created_at" in df.columns:
            filtered = df.sort_values("created_at").groupby("user_id").tail(1).copy()
        else:
            filtered = df.groupby("user_id").tail(1).copy()
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

    # Pastikan filtered adalah copy untuk menghindari SettingWithCopyWarning
    filtered = filtered.copy()

    # Label for UI Chart
    if pilih_skd in ["Semua", "Rentang"]:
        if pilih_user == "Semua User":
            filtered["label"] = filtered["nama"] + " (SKD " + filtered["skd_ke"].astype(str) + ")"
        else:
            filtered["label"] = "SKD ke-" + filtered["skd_ke"].astype(str)
    else:
        filtered["label"] = filtered["nama"]

    # Tampilkan Tabel UI
    with st.container(border=True):
        st.subheader("Data Riwayat SKD")
        cols_to_show = ["nama", "skd_ke", "twk", "tiu", "tkp", "total"]
        st.dataframe(filtered[cols_to_show], use_container_width=True, hide_index=True)

    with st.container(border=True):
        st.subheader("Grafik Komponen Nilai")
        fig1 = render_skd_chart(filtered, f"Komponen Nilai SKD ({pilih_skd})", is_component=True)
        if fig1:
            st.pyplot(fig1)

    with st.container(border=True):
        st.subheader("Grafik Total Nilai")
        fig2 = render_skd_chart(filtered, f"Total Nilai SKD ({pilih_skd})", is_component=False)
        if fig2:
            st.pyplot(fig2)


def render_laporan_page(user, role):
    """Halaman Laporan dan Cetak khusus untuk download file laporan A4."""
    st.header("🖨️ Laporan & Cetak")
    
    if role == "admin":
        data = prepare_admin_data()
        if not data:
            st.info("Belum ada data user.")
            return

        if data["df"].empty:
            st.warning("Tidak ada data nilai user untuk dibuat laporan.")
        else:
            df = data["df"]
            user_list = ["Semua User"] + sorted(df["nama"].unique().tolist())
            pilih_user_rep = st.selectbox("Pilih User untuk Laporan", user_list)
            
            if pilih_user_rep == "Semua User":
                _render_all_users_report_ui(df)
            else:
                df_target = df[df["nama"] == pilih_user_rep].copy()
                _render_individual_report_ui(df_target, pilih_user_rep)
    else:
        scores = fetch_user_scores(user["id"])
        if not scores:
            st.info("Belum ada data nilai. Silakan input nilai terlebih dahulu di menu Profil.")
            return
        df_target = pd.DataFrame(scores)
        if "created_at" in df_target.columns:
            df_target = df_target.sort_values("created_at")
        df_target["skd_ke"] = range(1, len(df_target) + 1)
        pilih_user_rep = user.get("nama")
        _render_individual_report_ui(df_target, pilih_user_rep)


def _render_all_users_report_ui(df_all):
    """Helper untuk menampilkan UI laporan untuk semua user per SKD."""
    st.subheader("📊 Laporan Semua User")
    
    max_skd_global = int(df_all["skd_ke"].max())
    skd_options = [f"SKD ke-{i}" for i in range(1, max_skd_global + 1)] + ["SKD Terakhir"]
    
    pilih_skd = st.selectbox("Pilih Percobaan SKD", skd_options, index=len(skd_options)-1)
    
    if pilih_skd == "SKD Terakhir":
        # Ambil data terakhir untuk setiap user (berdasarkan skd_ke terbanyak)
        report_df = df_all.sort_values(["user_id", "skd_ke"]).groupby("user_id").tail(1).copy()
        report_title = "Laporan Semua User: SKD Terakhir"
        filename_base = "laporan_skd_semua_user_terakhir"
    else:
        n = int(pilih_skd.split("-")[-1])
        report_df = df_all[df_all["skd_ke"] == n].copy()
        report_title = f"Laporan Semua User: SKD ke-{n}"
        filename_base = f"laporan_skd_semua_user_ke_{n}"

    if report_df.empty:
        st.warning(f"Tidak ada data untuk {pilih_skd}")
        return

    # Siapkan label untuk grafik
    report_df["label"] = report_df["nama"]
    
    with st.container(border=True):
        st.subheader("Pratinjau Data")
        cols = ["nama", "skd_ke", "twk", "tiu", "tkp", "total"]
        st.dataframe(report_df[cols].sort_values("total", ascending=False), use_container_width=True, hide_index=True)

        st.markdown("---")
        # Tombol Download Laporan PNG
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            report_table = render_report_page(report_df, report_title, "table")
            if report_table:
                st.download_button(
                    label="📄 Download Tabel (PNG)",
                    data=report_table,
                    file_name=f"{filename_base}_tabel.png",
                    mime="image/png",
                    use_container_width=True,
                    key="btn_dl_table_all"
                )
        with col_btn2:
            report_charts = render_report_page(report_df, report_title, "charts")
            if report_charts:
                st.download_button(
                    label="📊 Download Grafik (PNG)",
                    data=report_charts,
                    file_name=f"{filename_base}_grafik.png",
                    mime="image/png",
                    use_container_width=True,
                    key="btn_dl_charts_all"
                )


def _render_individual_report_ui(df_target, pilih_user):
    """Helper untuk menampilkan UI laporan individu."""
    max_skd = len(df_target)
    df_target["label"] = "SKD ke-" + df_target["skd_ke"].astype(str)
    
    with st.container(border=True):
        st.subheader("🔍 Tentukan Rentang Data")
        st.info(f"Jumlah data: {max_skd}. Untuk hasil terbaik (A4), laporan dibatasi maksimal 15 data per halaman.")
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            default_dari = max(1, max_skd - 14)
            r_dari = st.number_input("Dari SKD ke-", min_value=1, max_value=max_skd, value=default_dari, key=f"rep_r_dari_{pilih_user}")
        with col_r2:
            max_val = min(r_dari + 14, max_skd)
            r_sampai = st.number_input("Sampai SKD ke-", min_value=r_dari, max_value=max_val, value=max_val, key=f"rep_r_sampai_{pilih_user}")
        
        st.success(f"💡 Rentang Laporan: SKD ke-{r_dari} sampai ke-{r_sampai}")

    report_df = df_target[(df_target["skd_ke"] >= r_dari) & (df_target["skd_ke"] <= r_sampai)].copy()

    with st.container(border=True):
        st.subheader(f"Pratinjau Data: {pilih_user}")
        cols = ["skd_ke", "twk", "tiu", "tkp", "total"]
        st.dataframe(report_df[cols], use_container_width=True, hide_index=True)

        st.markdown("---")
        # Tombol Download Laporan PNG
        report_title = f"Laporan Hasil SKD: {pilih_user} (SKD {r_dari}-{r_sampai})"
        filename_base = f"laporan_skd_{pilih_user}_{r_dari}_{r_sampai}".replace(" ", "_")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            report_table = render_report_page(report_df, report_title, "table")
            if report_table:
                st.download_button(
                    label="📄 Download Tabel (PNG)",
                    data=report_table,
                    file_name=f"{filename_base}_tabel.png",
                    mime="image/png",
                    use_container_width=True,
                    key=f"btn_dl_table_{pilih_user}"
                )
        with col_btn2:
            report_charts = render_report_page(report_df, report_title, "charts")
            if report_charts:
                st.download_button(
                    label="📊 Download Grafik (PNG)",
                    data=report_charts,
                    file_name=f"{filename_base}_grafik.png",
                    mime="image/png",
                    use_container_width=True,
                    key=f"btn_dl_charts_{pilih_user}"
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

    with st.container(border=True):
        st.subheader("Grafik Komponen Nilai (Per Percobaan)")
        fig1 = render_skd_chart(df, "Perkembangan Nilai TWK / TIU / TKP", is_component=True)
        if fig1:
            st.pyplot(fig1)

    with st.container(border=True):
        st.subheader("Grafik Total Nilai")
        fig2 = render_skd_chart(df, "Perkembangan Total Nilai SKD", is_component=False)
        if fig2:
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
        confirm_delete_dialog("Yakin ingin menghapus seluruh data score dan user? Tindakan ini permanen!", "do_reset_all_data")

    if st.session_state.get("do_reset_all_data"):
        with st.spinner("Sedang memproses reset data..."):
            try:
                # 1. Hapus semua data scores
                supabase.table("scores").delete().neq("twk", -1).execute()
                
                # 2. Hapus semua user dengan role 'user'
                supabase.table("users").delete().eq("role", "user").execute()
                
                st.session_state.toast_msg = "Semua data berhasil direset"
                st.balloons()
                
                del st.session_state.do_reset_all_data
                st.rerun()
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
    menu_options = ["Dashboard", "Grafik Nilai", "User Management", "Laporan", "Maintenance"]
else:
    menu_options = ["Dashboard", "Profil & Nilai Saya", "Laporan"]

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
# HALAMAN USER MANAGEMENT / PROFIL & NILAI
# ======================
elif menu in ["User Management", "Profil & Nilai Saya"]:
    if role == "admin":
        admin_user_management()
    else:
        if user is None:
            st.error("Data user tidak ditemukan di session.")
        else:
            user_self_page(user)

# ======================
# HALAMAN LAPORAN
# ======================
elif menu == "Laporan":
    render_laporan_page(user, role)

# ======================
# HALAMAN MAINTENANCE
# ======================
elif menu == "Maintenance":
    if role == "admin":
        admin_maintenance()
    else:
        st.error("Hanya Admin yang dapat mengakses halaman ini.")
