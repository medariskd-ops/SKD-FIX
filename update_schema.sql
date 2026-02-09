-- Update schema untuk mendukung fitur Angkatan dan Transmigrasi
ALTER TABLE users ADD COLUMN IF NOT EXISTS tahun_masuk INT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS tahun_aktif INT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS tahun_transmigrasi INT;

-- Catatan: Jika ada data lama, Anda mungkin ingin mengisi tahun_aktif dengan tahun saat ini
-- UPDATE users SET tahun_aktif = 2025, tahun_masuk = 2025 WHERE tahun_aktif IS NULL;
