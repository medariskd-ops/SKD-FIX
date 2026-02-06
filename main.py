import streamlit as st
from auth import login, logout

st.set_page_config(
    page_title="SKD App",
    layout="wide"
)

# ======================
# LOGIN CHECK
# ======================
if not login():
    st.stop()

# ======================
# APP UTAMA
# ======================

st.title("📊 SKD Application")

st.sidebar.title("Menu")

menu = st.sidebar.selectbox(
    "Pilih Menu",
    ["Item", "Grafik", "User"]
)

logout()

# ======================
# HALAMAN ITEM
# ======================
if menu == "Item":
    st.header("Data Item")
    st.write("Halaman item tampil di sini")

# ======================
# HALAMAN GRAFIK
# ======================
elif menu == "Grafik":
    st.header("Grafik")
    st.write("Grafik tampil di sini")

# ======================
# HALAMAN USER
# ======================
elif menu == "User":
    st.header("User Management")
    st.write("Data user tampil di sini")
