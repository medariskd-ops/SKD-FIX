import streamlit as st
import bcrypt

from database import supabase, ANGKATAN_OPTIONS


def _is_bcrypt_hash(value: str) -> bool:
    """Cek apakah string sudah berupa hash bcrypt."""
    return isinstance(value, str) and value.startswith("$2b$")


def _get_user_by_username_and_angkatan(username: str, angkatan: str):
    """Ambil data user dari Supabase berdasarkan nama dan angkatan."""
    # 1. Coba cari yang cocok nama dan angkatan
    response = (
        supabase.table("users")
        .select("*")
        .eq("nama", username)
        .eq("angkatan", angkatan)
        .execute()
    )
    data = getattr(response, "data", None)
    if data:
        return data[0]

    # 2. Fallback: Cari berdasarkan nama saja untuk handle legacy users yang belum punya angkatan
    response_legacy = (
        supabase.table("users")
        .select("*")
        .eq("nama", username)
        .execute()
    )
    data_legacy = getattr(response_legacy, "data", None)
    if data_legacy:
        user = data_legacy[0]
        # Jika user legacy ini belum punya angkatan (atau role admin), izinkan login
        if not user.get("angkatan") or user.get("role") == "admin":
            return user

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
        login_angkatan = st.selectbox("Angkatan", ANGKATAN_OPTIONS, key="login_angkatan")
        st.markdown(
            "<small>Jika Anda lupa password, silakan hubungi admin untuk reset atau bantuan lebih lanjut.</small>",
            unsafe_allow_html=True
        )

        if st.button("Login"):
            if not username or not password:
                st.error("Username dan password wajib diisi")
                return False

            user = _get_user_by_username_and_angkatan(username, login_angkatan)
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
        new_angkatan = st.selectbox("Angkatan", ANGKATAN_OPTIONS, key="reg_angkatan")

        if st.button("Daftar"):
            if not new_username or not new_password:
                st.error("Nama dan password wajib diisi")
            elif new_password != confirm_password:
                st.error("Konfirmasi password tidak cocok")
            else:
                existing = _get_user_by_username_and_angkatan(new_username, new_angkatan)
                if existing:
                    st.error("Nama sudah digunakan di angkatan ini, silakan pilih nama lain")
                else:
                    password_hash = bcrypt.hashpw(
                        new_password.encode("utf-8"), bcrypt.gensalt()
                    ).decode("utf-8")
                    
                    try:
                        supabase.table("users").insert({
                            "nama": new_username,
                            "password": password_hash,
                            "role": "user", # Selalu 'user' untuk registrasi mandiri
                            "angkatan": new_angkatan,
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

    def trigger_confirm():
        st.session_state.confirm_logout = True

    def cancel_confirm():
        st.session_state.confirm_logout = False

    def do_logout():
        for key in ("user", "role", "logged_in", "confirm_logout", "toast_msg"):
            st.session_state.pop(key, None)

    # Gunakan sidebar.container agar tetap di sidebar dan transisi lebih bersih
    with st.sidebar.container():
        if not st.session_state.confirm_logout:
            st.button(
                "Logout", 
                key="btn_logout_side", 
                use_container_width=True, 
                on_click=trigger_confirm
            )
        else:
            st.warning("Yakin ingin keluar?")
            col1, col2 = st.columns(2)
            col1.button("Iya", key="btn_logout_iya", use_container_width=True, on_click=do_logout, type="primary")
            col2.button("Tidak", key="btn_logout_tidak", use_container_width=True, on_click=cancel_confirm)
