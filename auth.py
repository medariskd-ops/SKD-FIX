import streamlit as st
import bcrypt
import datetime

from database import supabase


def _is_bcrypt_hash(value: str) -> bool:
    """Cek apakah string sudah berupa hash bcrypt."""
    return isinstance(value, str) and value.startswith("$2b$")


def _get_user_by_username(username: str):
    """Ambil data user dari Supabase berdasarkan nama."""
    try:
        response = supabase.table("users").select("*").eq("nama", username).execute()
        data = getattr(response, "data", None)
        if data:
            return data[0]
        return None
    except Exception as e:
        st.error(f"Error fetching user: {e}")
        return None


def login():
    """Halaman login & registrasi dengan penyimpanan user di session_state."""
    
    # kalau sudah login, tidak perlu login lagi
    if st.session_state.get("user") is not None:
        return True

    _, mid, _ = st.columns([1, 1.4, 1])
    with mid:
        st.markdown(
            """
            <div class="login-brand">
                <div class="icon">school</div>
                <h2>SKD App</h2>
                <p>Pantau progres tryout SKD kamu</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.container(key="login_card"):
            tab1, tab2 = st.tabs(["Login", "Daftar Akun"])

            with tab1:
                username = st.text_input("Username", key="login_user")
                password = st.text_input("Password", type="password", key="login_pass")
                st.markdown(
                    "<small>Jika Anda lupa password, silakan hubungi admin untuk reset atau bantuan lebih lanjut.</small>",
                    unsafe_allow_html=True
                )

                if st.button("Login", type="primary", use_container_width=True):
                    if not username or not password:
                        st.error("Username dan password wajib diisi")
                        return False

                    with st.spinner("Sedang masuk..."):
                        user = _get_user_by_username(username)
                        if not user:
                            st.error("User tidak ditemukan")
                            return False

                        stored_password = user.get("password")
                        ok = False

                        if stored_password:
                            if _is_bcrypt_hash(stored_password):
                                try:
                                    ok = bcrypt.checkpw(
                                        password.encode("utf-8"), stored_password.encode("utf-8")
                                    )
                                except ValueError:
                                    ok = False
                            else:
                                if password == stored_password:
                                    ok = True
                                    try:
                                        new_hash = bcrypt.hashpw(
                                            password.encode("utf-8"), bcrypt.gensalt()
                                        ).decode("utf-8")
                                        supabase.table("users").update(
                                            {"password": new_hash}
                                        ).eq("id", user["id"]).execute()
                                    except Exception:
                                        pass

                    if not ok:
                        st.error("Username atau password salah")
                        return False

                    st.session_state.user = user
                    st.session_state.role = user.get("role", "user")
                    # Reset filter angkatan agar admin selalu mulai dari angkatan terbaru
                    st.session_state.pop("filter_tahun_aktif", None)
                    st.session_state._just_logged_in = True
                    st.rerun()

            with tab2:
                new_username = st.text_input("Username", key="reg_user")
                new_password = st.text_input("Password", type="password", key="reg_pass")
                confirm_password = st.text_input("Konfirmasi Password", type="password", key="reg_conf")
        
                # Dropdown Angkatan (Tahun Sekarang & Tahun Sekarang + 1)
                year_now = datetime.date.today().year
                new_angkatan = st.selectbox("Angkatan", [year_now, year_now + 1], index=0)

                if st.button("Daftar", type="primary", use_container_width=True):
                    if not new_username or not new_password:
                        st.error("Nama dan password wajib diisi")
                    elif new_password != confirm_password:
                        st.error("Konfirmasi password tidak cocok")
                    else:
                        existing = _get_user_by_username(new_username)
                        if existing:
                            st.error("Nama sudah digunakan, silakan pilih nama lain")
                        else:
                            password_hash = bcrypt.hashpw(
                                new_password.encode("utf-8"), bcrypt.gensalt()
                            ).decode("utf-8")
                    
                            try:
                                supabase.table("users").insert({
                                    "nama": new_username,
                                    "password": password_hash,
                                    "role": "user", # Selalu 'user' untuk registrasi mandiri
                                    "tahun_masuk": new_angkatan,
                                    "tahun_aktif": new_angkatan
                                }).execute()
                                st.session_state.toast_msg = "Pendaftaran berhasil! Silakan login."
                                st.rerun()
                            except Exception as e:
                                error_msg = str(e)
                                if "23502" in error_msg or "violates not-null constraint" in error_msg:
                                    st.error("Gagal mendaftar: Konfigurasi Database (ID Default) belum diset di Supabase. Silakan hubungi admin.")
                                else:
                                    st.error(f"Terjadi kesalahan: {e}")

    return False


@st.dialog("Keluar dari akun?")
def _logout_dialog():
    st.write("Kamu perlu login lagi untuk masuk ke aplikasi.")
    c1, c2 = st.columns(2)
    if c1.button("Batal", key="dlg_logout_batal", use_container_width=True):
        st.rerun()
    if c2.button("Keluar", key="dangerfill_dlg_logout", use_container_width=True):
        for key in ("user", "role", "logged_in", "toast_msg", "filter_tahun_aktif"):
            st.session_state.pop(key, None)
        st.rerun()


def logout():
    """Tombol logout di sidebar, konfirmasinya lewat dialog pop up."""
    if st.sidebar.button("Logout", key="danger_logout_side", use_container_width=True):
        _logout_dialog()
