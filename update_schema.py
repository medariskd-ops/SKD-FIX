from database import supabase

def update_schema():
    """
    Script untuk migrasi database:
    1. Menambahkan kolom 'angkatan' ke tabel 'users'.
    2. Memberikan nilai default untuk user lama yang belum memiliki angkatan.

    Jalankan SQL berikut di SQL Editor Supabase:

    -- 1. Tambah kolom
    ALTER TABLE users ADD COLUMN angkatan TEXT;

    -- 2. Update user lama ke angkatan default (opsional)
    UPDATE users SET angkatan = '(2025/2026)' WHERE angkatan IS NULL;
    """
    print("=== MIGRASI DATABASE ===")
    print("Silakan jalankan perintah berikut di SQL Editor Supabase:")
    print("")
    print("ALTER TABLE users ADD COLUMN angkatan TEXT;")
    print("UPDATE users SET angkatan = '(2025/2026)' WHERE angkatan IS NULL;")
    print("")
    print("=========================")

if __name__ == "__main__":
    update_schema()
