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

# ======================
# DESIGN SYSTEM (CSS)
# ======================
def inject_global_css():
    st.markdown(
        """
        <style>
        /* 1. Reset Global & Sidebar Header (Hapus SKD App yang kaku) */
        [data-testid="stSidebarHeader"] {
            display: none !important;
        }
        
        /* 2. Paksa Latar Belakang Putih Total */
        .stApp {
            background-color: #FFFFFF !important;
        }

        /* 3. Sidebar Cerah & Modern */
        [data-testid="stSidebar"] {
            background-color: #F8FAFB !important;
            border-right: 1px solid #EAEFEF !important;
        }
        
        [data-testid="stSidebarNav"] {
            padding-top: 0px !important;
        }

        /* 4. Typography: Abu Gelap untuk kenyamanan mata */
        h1, h2, h3, p, span, label {
            color: #34495E !important; 
        }

        /* 5. Pop-up Tengah Layar (Cerah & Kontras) */
        @keyframes popIn {
            0% { opacity: 0; transform: translate(-50%, -60%) scale(0.9); }
            15% { opacity: 1; transform: translate(-50%, -50%) scale(1.05); }
            20% { transform: translate(-50%, -50%) scale(1); }
            85% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
            100% { opacity: 0; transform: translate(-50%, -40%) scale(0.9); }
        }

        .custom-toast-container {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 1000001;
            pointer-events: none;
        }

        .custom-toast {
            background: #FFFFFF !important;
            color: #25343F !important;
            padding: 30px 50px !important;
            border-radius: 25px !important;
            text-align: center;
            box-shadow: 0 20px 60px rgba(37, 52, 63, 0.2) !important;
            border: 3px solid #FF9B51 !important;
            animation: popIn 4s ease-in-out forwards;
            min-width: 350px;
        }

        .toast-text {
            font-size: 1.2rem !important;
            font-weight: 700 !important;
            display: block;
            color: #25343F !important;
        }

        /* 6. Tombol Orange Custom */
        div.stButton > button {
            background-color: #FF9B51 !important;
            color: white !important;
            border-radius: 10px !important;
            border: none !important;
            padding: 0.5rem 2rem !important;
            font-weight: 600 !important;
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
                <div style="font-size: 40px; margin-bottom: 10px;">✨</div>
                <span class="toast-text">{message}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

inject_global_css()

# ======================
# DATA FETCHING
# ======================
def fetch_all_users():
    response = supabase.table("users").select("*").execute()
    return getattr(response, "data", []) or []

def fetch_all_scores():
    try:
        response = supabase.table("scores").select("*").execute()
        return getattr(response, "data", []) or []
    except Exception: return []

def fetch_user_scores(user_id: str):
    try:
        response = supabase.table("scores").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return getattr(response, "data", []) or []
    except Exception: return []

def fetch_latest_score(user_id: str):
    scores = fetch_user_scores(user_id)
    return scores[0] if scores else None

if "toast_msg" in st.session_state:
    show_toast(st.session_state.toast_msg)
    del st.session_state.toast_msg

# ======================
# ADMIN USER MANAGEMENT (KEMBALI KE ASLI)
# ======================
def admin_user_management():
    st.header("👤 User Management (Admin)")

    users = fetch_all_users()
    with st.container(border=True):
        if users:
            df = pd.DataFrame(users)
            cols = [c for c in ["nama", "role"] if c in df.columns]
            st.subheader("Daftar User")
            st.dataframe(df[cols], use_container_width=True)
        else:
            st.info("Belum ada user di database.")

    st.markdown("---")

    # Edit User Account
    with st.container(border=True):
        st.subheader("Edit User Account")
        if users:
            nama_list = [u["nama"] for u in users]
            nama_pilih = st.selectbox("Pilih User", nama_list, key="edit_user_select")
            user_pilih = next(u for u in users if u["nama"] == nama_pilih)
            with st.form("edit_user"):
                new_password = st.text_input("Password baru (kosongkan jika tidak diubah)", type="password")
                new_role = st.selectbox("Role", ["admin", "user"], index=0 if user_pilih.get("role") == "admin" else 1)
                submitted_edit = st.form_submit_button("Simpan Perubahan User")
            if submitted_edit:
                update_data = {"role": new_role}
                if new_password:
                    password_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                    update_data["password"] = password_hash
                supabase.table("users").update(update_data).eq("id", user_pilih["id"]).execute()
                st.session_state.toast_msg = "User Updated!"
                st.rerun()

    st.markdown("---")

    # Edit Nilai User (Tabel ini yang tadi hilang)
    with st.container(border=True):
        st.subheader("Edit Nilai SKD User")
        if users:
            nama_list_score = [u["nama"] for u in users if u["role"] != "admin"]
            if nama_list_score:
                nama_pilih_score = st.selectbox("Pilih User untuk diedit nilainya", nama_list_score)
                user_pilih_score = next(u for u in users if u["nama"] == nama_pilih_score)
                user_scores = fetch_user_scores(user_pilih_score["id"])
                
                if user_scores:
                    df_user_scores = pd.DataFrame(user_scores).sort_values("created_at")
                    df_user_scores["skd_ke"] = range(1, len(df_user_scores) + 1)
                    edit_options_admin = [f"SKD ke-{row['skd_ke']}" for _, row in df_user_scores.iterrows()]
                    pilih_skd_admin = st.selectbox("Pilih Percobaan", edit_options_admin)
                    
                    idx_pilih_admin = int(pilih_skd_admin.split("-")[-1])
                    data_pilih_admin = df_user_scores[df_user_scores["skd_ke"] == idx_pilih_admin].iloc[0]

                    with st.form("admin_edit_nilai_form"):
                        ae_twk = st.number_input("Update TWK", min_value=0, value=int(data_pilih_admin["twk"]))
                        ae_tiu = st.number_input("Update TIU", min_value=0, value=int(data_pilih_admin["tiu"]))
                        ae_tkp = st.number_input("Update TKP", min_value=0, value=int(data_pilih_admin["tkp"]))
                        submitted_admin_edit_score = st.form_submit_button("Simpan Perubahan Nilai")

                    if submitted_admin_edit_score:
                        supabase.table("scores").update({
                            "twk": ae_twk, "tiu": ae_tiu, "tkp": ae_tkp, "total": ae_twk+ae_tiu+ae_tkp
                        }).eq("id", data_pilih_admin["id"]).execute()
                        st.session_state.toast_msg = "Nilai Berhasil Diubah"
                        st.rerun()
                else: st.info("User belum punya nilai.")

# ======================
# USER PAGE & DASHBOARDS
# ======================
def user_self_page(user: dict):
    st.header("📑 Profil & Nilai Saya")
    # ... (sama seperti kodemu sebelumnya untuk input nilai user)
    st.write(f"Nama: **{user.get('nama')}**")
    latest = fetch_latest_score(user["id"])
    with st.form("input_nilai"):
        twk = st.number_input("TWK", value=int(latest["twk"]) if latest else 0)
        tiu = st.number_input("TIU", value=int(latest["tiu"]) if latest else 0)
        tkp = st.number_input("TKP", value=int(latest["tkp"]) if latest else 0)
        if st.form_submit_button("Simpan"):
            supabase.table("scores").insert({"user_id": user["id"], "twk": twk, "tiu": tiu, "tkp": tkp, "total": twk+tiu+tkp}).execute()
            st.session_state.toast_msg = "Nilai Tersimpan!"
            st.rerun()

def grafik_dashboard():
    # Fungsi grafik dashboard admin (menampilkan semua user)
    st.header("📈 Dashboard Global")
    # ... (logika merge dataframe dan plotting matplotlib)
    # Gunakan warna palet: #25343F (Navy), #FF9B51 (Orange)

def user_personal_dashboard(user: dict):
    st.header("📊 Progress Nilai")
    # ... (logika chart personal user)

def admin_maintenance():
    st.header("🛠️ Maintenance")
    if st.button("RESET DATA"): # Tambahkan logika konfirmasi teks jika perlu
        supabase.table("scores").delete().neq("twk", -1).execute()
        st.session_state.toast_msg = "Data Dihapus"
        st.rerun()

# ======================
# APP FLOW
# ======================
if not login(): st.stop()

user = st.session_state.get("user")
role = user.get("role", "user")

# Header Sidebar Kustom
st.sidebar.markdown(
    """
    <div style='text-align: center; padding-bottom: 20px; border-bottom: 1px solid #EAEFEF; margin-bottom: 20px;'>
        <h1 style='color: #25343F; font-size: 1.5rem; margin-bottom: 0;'>SKD<span style='color: #FF9B51;'>.pro</span></h1>
        <p style='color: #BFC9D1; font-size: 0.8rem;'>Monitoring System</p>
    </div>
    """, 
    unsafe_allow_html=True
)

menu = st.sidebar.radio("Navigasi", ["Dashboard", "User", "Maintenance"] if role=="admin" else ["Dashboard", "User"])
logout()

if menu == "Dashboard":
    if role == "admin": grafik_dashboard()
    else: user_personal_dashboard(user)
elif menu == "User":
    if role == "admin": admin_user_management()
    else: user_self_page(user)
elif menu == "Maintenance": admin_maintenance()
