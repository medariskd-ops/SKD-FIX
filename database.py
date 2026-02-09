import os

import streamlit as st
from supabase import create_client
from dotenv import load_dotenv

# Untuk development lokal: baca dari .env
load_dotenv()


def _get_supabase_credentials():
    """
    Ambil SUPABASE_URL dan SUPABASE_KEY.
    Prioritas:
    1. st.secrets (Streamlit Cloud)
    2. Environment variables / .env
    """
    url = None
    key = None

    # 1) Coba dari st.secrets (Cloud)
    try:
        if "SUPABASE_URL" in st.secrets:
            url = st.secrets["SUPABASE_URL"]
        if "SUPABASE_KEY" in st.secrets:
            key = st.secrets["SUPABASE_KEY"]
    except Exception:
        # st.secrets mungkin tidak ada saat running sebagai script biasa
        pass

    # 2) Fallback ke environment / .env
    url = url or os.getenv("SUPABASE_URL")
    key = key or os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL dan SUPABASE_KEY harus di-set di st.secrets atau environment."
        )

    return url, key


URL, KEY = _get_supabase_credentials()

supabase = create_client(URL, KEY)

# Opsi Angkatan Terpusat
ANGKATAN_OPTIONS = ["(2025/2026)", "(2027/2028)"]
