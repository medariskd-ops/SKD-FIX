import streamlit as st

# contoh akun login sementara
# nanti bisa diganti ambil dari database
USER_DATA = {
    "admin": "admin123"
}


def login():
    st.title("🔐 Login SKD App")

    # buat session login
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # kalau sudah login
    if st.session_state.logged_in:
        return True

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USER_DATA and USER_DATA[username] == password:
            st.session_state.logged_in = True
            st.success("Login berhasil")
            st.rerun()
        else:
            st.error("Username atau password salah")

    return False


def logout():
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
