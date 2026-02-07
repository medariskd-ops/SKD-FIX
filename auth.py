import streamlit as st
import bcrypt

from database import supabase


def _is_bcrypt_hash(value: str) -> bool:
    """Cek apakah string sudah berupa hash bcrypt."""
    return isinstance(value, str) and value.startswith("$2b$")


def _get_user_by_username(username: str):
    """Ambil data user dari Supabase berdasarkan nama."""
    response = supabase.table("users").select("*").eq("nama", username).execute()
    data = getattr(response, "data", None)
    if data:
        return data[0]
    return None


def login():
    """Halaman login & registrasi dengan penyimpanan user di session_state."""
    
    # kalau sudah login, tidak perlu login lagi
    if st.session_state.get("user") is not None:
        return True

    tab1, tab2 = st.tabs(["Login", "Daftar Akun"])

    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        st.markdown(
            "<small>Jika Anda lupa password, silakan hubungi admin untuk reset atau bantuan lebih lanjut.</small>",
            unsafe_allow_html=True
        )

        if st.button("Login"):
            if not username or not password:
                st.error("Username dan password wajib diisi")
                return False

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
            st.session_state.toast_msg = "Login berhasil"
            st.rerun()

    with tab2:
        st.subheader("Daftar Akun Baru")
        new_username = st.text_input("Username", key="reg_user")
        new_password = st.text_input("Password", type="password", key="reg_pass")
        confirm_password = st.text_input("Konfirmasi Password", type="password", key="reg_conf")

        if st.button("Daftar"):
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
                        }).execute()
                        st.session_state.toast_msg = "Pendaftaran berhasil! Silakan login."
                        st.rerun()
                    except Exception as e:
                        st.error(f"Terjadi kesalahan: {e}")

    return False


def logout():
    """Tombol logout di sidebar dengan konfirmasi."""
    if "confirm_logout" not in st.session_state:
        st.session_state.confirm_logout = False

    if not st.session_state.confirm_logout:
        if st.sidebar.button("Logout"):
            st.session_state.confirm_logout = True
            st.rerun()
    else:
        st.sidebar.warning("Yakin ingin keluar?")
        col1, col2 = st.sidebar.columns(2)
        if col1.button("Ya", use_container_width=True):
            for key in ("user", "role", "logged_in", "confirm_logout", "toast_msg"):
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        if col2.button("Tidak", use_container_width=True):
            st.session_state.confirm_logout = False
            st.rerun()
